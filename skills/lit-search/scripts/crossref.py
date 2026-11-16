# -*- coding: utf-8 -*-
"""Crossref REST 客户端 —— 无需 API key 的第三检索通道。

为什么要有它：
- S2 的速率限制（429）一旦触发，按策略要立刻停手；这时还需要"查几条文献"时，
  Crossref 是可用的兜底：公开 API、不需要 key，且 DOI 元数据最权威。
- Crossref 偏题录（DOI、期刊、作者、被引数、参考文献列表），不擅长语义检索。

接口：https://api.crossref.org/works
礼貌池：带上 mailto 参数可获得更快的响应速率。

Python 3.7+，依赖 requests。
"""

from __future__ import print_function

import json
import os
import sys
import time

API = "https://api.crossref.org/works"
API_ROOT = "https://api.crossref.org"


class CrossrefError(Exception):
    pass


class CrossrefRateLimitError(CrossrefError):
    """Crossref 侧的限流。"""


def _pick(seq, default=""):
    if isinstance(seq, (list, tuple)):
        return seq[0] if seq else default
    if seq:
        return seq
    return default


def _year_of(item):
    for key in ("published-print", "published-online", "published", "issued",
                "created"):
        parts = (item.get(key) or {}).get("date-parts")
        if parts and parts[0] and parts[0][0]:
            return parts[0][0]
    return None


def _event_name(item):
    """event 可能是 dict，也可能是字符串。"""
    event = item.get("event") or {}
    if isinstance(event, dict):
        return event.get("name") or ""
    return str(event)


def normalize(item, source="crossref"):
    """把 Crossref work 记录转成与 S2 相近的字段结构，便于与 S2 结果合并去重。"""
    doi = (item.get("DOI") or "").strip().lower()
    title = _pick(item.get("title") or [])
    venue = _pick(item.get("container-title") or []) or _event_name(item)
    authors = []
    for a in item.get("author") or []:
        name = " ".join(x for x in [a.get("given"), a.get("family")] if x)
        if not name:
            name = a.get("name") or ""
        if name:
            authors.append({"name": name})
    year = _year_of(item)
    url = item.get("URL") or ("https://doi.org/" + doi if doi else "")
    rec = {
        "paperId": ("DOI:" + doi) if doi else None,
        "title": title,
        "year": year,
        "venue": venue,
        "authors": authors,
        "externalIds": {"DOI": doi} if doi else {},
        "citationCount": item.get("is-referenced-by-count") or 0,
        "publicationDate": "-".join(
            "%02d" % p for p in ((item.get("issued") or {}).get("date-parts") or [[]])[0][:2]
        ) if ((item.get("issued") or {}).get("date-parts") or [[]])[0] else "",
        "publicationTypes": [item.get("type")] if item.get("type") else [],
        "abstract": (item.get("abstract") or "").strip(),
        "url": url,
        "publisher": item.get("publisher") or "",
        "referenceCount": item.get("reference-count") or 0,
        "_meta": {"source": source},
    }
    return rec


class CrossrefClient(object):
    def __init__(self, mailto=None, timeout=60, proxy=None, trust_env=True,
                 max_retries=3, verbose=True):
        try:
            import requests
        except ImportError:
            raise SystemExit("缺少依赖：pip install requests")

        self._requests = requests
        self.timeout = timeout
        self.max_retries = max_retries
        self.verbose = verbose
        self.mailto = mailto or os.environ.get("CROSSREF_MAILTO") or ""

        self.session = requests.Session()
        import s2api
        s2api.configure_session(self.session, proxy=proxy, trust_env=trust_env)
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.session.headers["User-Agent"] = "lit-search/1.0 (skill)"
        if self.mailto:
            self.session.headers["Mailto"] = self.mailto

    def _log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    def _get(self, url, params):
        attempt = 0
        while True:
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
            except self._requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise CrossrefError("网络请求失败：%s" % exc)
                time.sleep(min(2 ** (attempt + 1), 30))
                attempt += 1
                continue

            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 429:
                raise CrossrefRateLimitError(
                    "HTTP 429：Crossref 限流。已停止，不再重试。%s" % resp.text[:200])
            if resp.status_code in (500, 502, 503, 504) and attempt < self.max_retries:
                wait = min(2 ** (attempt + 2), 30)
                self._log("  [HTTP %s] %ss 后重试" % (resp.status_code, wait))
                time.sleep(wait)
                attempt += 1
                continue
            raise CrossrefError("HTTP %s：%s" % (resp.status_code, resp.text[:300]))

    def _params(self, extra):
        params = {"mailto": self.mailto} if self.mailto else {}
        params.update(extra or {})
        return {k: v for k, v in params.items() if v not in (None, "")}

    def search(self, query=None, title=None, author=None, rows=20,
               filters=None, sort=None, order=None, select=None):
        """works 检索。query 走 bibliographic 模糊匹配，title/author 更精确。"""
        params = self._params({"rows": rows})
        if query:
            params["query.bibliographic"] = query
        if title:
            params["query.title"] = title
        if author:
            params["query.author"] = author
        if filters:
            params["filter"] = filters
        if sort:
            params["sort"] = sort
        if order:
            params["order"] = order
        if select:
            params["select"] = select
        payload = self._get(API, params)
        items = ((payload or {}).get("message") or {}).get("items") or []
        total = ((payload or {}).get("message") or {}).get("total-results")
        return items, total

    def journal_works(self, issn, query=None, rows=20, filters=None, sort=None,
                      order=None, select=None):
        """指定期刊（ISSN）内检索：/journals/{issn}/works。"""
        url = "%s/journals/%s/works" % (API_ROOT, issn)
        params = self._params({"rows": rows})
        if query:
            params["query.bibliographic"] = query
        if filters:
            params["filter"] = filters
        if sort:
            params["sort"] = sort
        if order:
            params["order"] = order
        if select:
            params["select"] = select
        payload = self._get(url, params)
        items = ((payload or {}).get("message") or {}).get("items") or []
        total = ((payload or {}).get("message") or {}).get("total-results")
        return items, total

    def prefix_works(self, prefix, query=None, rows=20, filters=None, sort=None,
                     order=None, select=None):
        """按 DOI 前缀检索（例：10.2139 = SSRN，10.3386 = NBER）。"""
        merged = "prefix:%s" % prefix
        if filters:
            merged = merged + "," + filters
        return self.search(query=query, rows=rows, filters=merged, sort=sort,
                           order=order, select=select)

    def get_work(self, doi):
        """按 DOI 取一条记录（含 reference 列表、is-referenced-by-count）。"""
        payload = self._get(API + "/" + str(doi), None)
        return (payload or {}).get("message") or {}

    def references(self, doi):
        """一篇文献的参考文献（Crossref 返回的 reference 列表，含 DOI 线索）。"""
        work = self.get_work(doi)
        refs = []
        for ref in work.get("reference") or []:
            refs.append({
                "doi": (ref.get("DOI") or "").lower(),
                "title": ref.get("article-title") or ref.get("volume-title") or "",
                "year": ref.get("year"),
                "journal": ref.get("journal-title") or "",
                "author": ref.get("author") or "",
            })
        return refs
