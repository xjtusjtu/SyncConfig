"""OpenCitations Index API v2 —— 引用图谱通道（免 key）。

作用：回答"谁引用了这篇 / 这篇引用了谁 / 有哪些共同引用的相关文献"，
并给出 DOI、PMID、OpenAlex、OMID 的交叉标识，便于与其它通道对齐。

接口（实测 2026-11-13 可用，无需鉴权）：
    GET /index/v2/citations/{doi}    → 引用了目标文献的文献
    GET /index/v2/references/{doi}   → 目标文献引用的文献

（similar/metadata/author 等端点实测返回 404，公开 API 未开放；共被引相似改用
OpenAlex 的 related_works，见 scripts/openalex.py。）

标识写法：doi:10.1038/nature12373
返回条目形如：
    {"oci": "...", "citing": "omid:... doi:... openalex:W... pmid:...",
     "cited": "...", "creation": "2013-07-31", "journal_sc": "no", "author_sc": "no"}
"""

import json
import os
import re
import sys
import time

API = "https://api.opencitations.net/index/v2"

ID_PREFIXES = ("doi", "pmid", "pmc", "omid", "openalex", "mag", "arxiv")


class OpenCitationsError(Exception):
    pass


def _requests():
    try:
        import requests
    except ImportError:
        raise SystemExit("缺少依赖：pip install requests")
    return requests


def normalize_id(value):
    """10.1038/nature12373 → doi:10.1038/nature12373；已带前缀的原样返回。"""
    value = (value or "").strip()
    if not value:
        raise OpenCitationsError("缺少标识（DOI / doi: / pmid: …）")
    if ":" in value:
        prefix = value.split(":", 1)[0].lower()
        if prefix in ID_PREFIXES:
            return value
    return "doi:" + value


def _parse_id_blob(blob):
    """'omid:br/xxx doi:10.1/x pmid:123 openalex:W123' → dict"""
    out = {}
    for token in (blob or "").split():
        if ":" not in token:
            continue
        prefix, _, val = token.partition(":")
        prefix = prefix.lower()
        if prefix in ID_PREFIXES:
            out[prefix.upper() if prefix != "openalex" else "OpenAlex"] = val
    return out


def _normalize_entry(entry, direction):
    citing = _parse_id_blob(entry.get("citing"))
    cited = _parse_id_blob(entry.get("cited"))
    if direction == "citations":
        primary, counterpart = citing, cited
    else:
        primary, counterpart = cited, citing
    ext = {k: v for k, v in primary.items() if k != "DOI"}
    if primary.get("DOI"):
        ext["DOI"] = primary["DOI"]
    return {
        "paperId": primary.get("DOI") or primary.get("OpenAlex") or "",
        "title": "",
        "authors": [],
        "externalIds": ext,
        "relation": {
            "direction": direction,
            "counterpart": counterpart,
            "oci": entry.get("oci"),
            "creation": entry.get("creation"),
            "timespan": entry.get("timespan"),
            "secondary_journal": entry.get("journal_sc"),
            "secondary_author": entry.get("author_sc"),
        },
        "_meta": {"source": "opencitations"},
    }


class OpenCitationsClient(object):
    def __init__(self, timeout=60, proxy=None, trust_env=True, verbose=True,
                 sleep=0.34):
        self._requests = _requests()
        self.timeout = timeout
        self.proxy = proxy
        self.trust_env = trust_env
        self.verbose = verbose
        self.sleep = sleep
        self.session = self._requests.Session()
        if proxy:
            self.session.trust_env = False
            self.session.proxies = {"http": proxy, "https": proxy}
        else:
            self.session.trust_env = trust_env
        self.session.headers.update({
            "User-Agent": "lit-search/1.0 (academic literature retrieval)",
            "Accept": "application/json",
        })

    def _get(self, path, params=None):
        url = API + path
        last = None
        for attempt in range(3):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
            except Exception as exc:
                last = exc
                time.sleep(1.5 * (attempt + 1))
                continue
            if resp.status_code == 429:
                raise OpenCitationsError(
                    "HTTP 429：OpenCitations 限流。已停止，不再重试。")
            if resp.status_code == 404:
                return []
            if resp.status_code >= 400:
                last = OpenCitationsError("HTTP %s：%s" % (resp.status_code, resp.text[:200]))
                time.sleep(1.5 * (attempt + 1))
                continue
            try:
                return resp.json()
            except Exception as exc:
                last = exc
                time.sleep(1.0)
        raise OpenCitationsError(str(last))

    def _edge(self, kind, ident):
        payload = self._get("/%s/%s" % (kind, ident))
        if isinstance(payload, dict):
            payload = payload.get("results") or []
        return [_normalize_entry(e, kind) for e in payload if isinstance(e, dict)]

    def citations(self, doi, limit=None):
        """引用了该 DOI 的文献。"""
        rows = self._edge("citations", normalize_id(doi))
        return rows[:limit] if limit else rows

    def references(self, doi, limit=None):
        """该 DOI 引用的文献。"""
        rows = self._edge("references", normalize_id(doi))
        return rows[:limit] if limit else rows

    def similar(self, doi, limit=None):
        """共被引相似：公开 API 未开放（404），改用 OpenAlex related_works。"""
        raise OpenCitationsError(
            "OpenCitations 公开 API 未提供 similar 端点；请用 "
            "`litsearch.py openalex --doi <doi> --related`。")


def _cli(argv):
    import argparse
    ap = argparse.ArgumentParser(description="OpenCitations 引用图谱（免 key）")
    ap.add_argument("--doi", required=True)
    ap.add_argument("--direction", default="citations",
                    choices=["citations", "references"])
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--proxy", default=None)
    ap.add_argument("--no-proxy", action="store_true")
    args = ap.parse_args(argv)

    client = OpenCitationsClient(proxy=args.proxy,
                                 trust_env=not args.no_proxy)
    rows = getattr(client, args.direction)(args.doi, limit=args.limit)
    for row in rows:
        rel = row.get("relation") or {}
        cp = rel.get("counterpart") or {}
        ext = row.get("externalIds") or {}
        print("- %s | 关系 %s | 对方 %s | %s" % (
            ext.get("DOI") or ext.get("OpenAlex") or "?",
            rel.get("direction"),
            cp.get("DOI") or cp.get("OpenAlex") or "?",
            rel.get("creation") or ""))
    print("共 %d 条" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
