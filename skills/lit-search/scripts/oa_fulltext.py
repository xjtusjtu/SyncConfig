# -*- coding: utf-8 -*-
"""开放获取与全文渠道：Unpaywall（OA 状态/最佳 PDF）+ CORE（全文检索/下载）。

重要：下载动作**永不隐式执行**。download() 先产出「下载计划」，必须由调用方
显式传 confirm=True 才会真正下载；在 agent 工作流中，须先把计划汇报给用户
并取得批准后再传该参数。

凭据：
- UNPAYWALL_EMAIL：Unpaywall 必填（真实邮箱）
- CORE_API_KEY：CORE 必填（无 key 时只能文档化，不可用）

Python 3.7+，依赖 requests。
"""

from __future__ import print_function

import os
import sys

UNPAYWALL_API = "https://api.unpaywall.org/v2/"
CORE_API = "https://api.core.ac.uk/v3/"


class OAError(Exception):
    pass


class OARateLimitError(OAError):
    """429：按策略立即停止。"""


def normalize_unpaywall(doi, payload):
    """Unpaywall 响应 → OA 信息片段（附到记录的 openAccess 字段）。"""
    best = payload.get("best_oa_location") or {}
    locations = []
    for loc in payload.get("oa_locations") or []:
        locations.append({
            "url": loc.get("url"),
            "url_for_pdf": loc.get("url_for_pdf"),
            "host_type": loc.get("host_type"),
            "license": loc.get("license"),
            "version": loc.get("version"),
            "is_oa": loc.get("is_oa"),
        })
    return {
        "doi": doi,
        "is_oa": payload.get("is_oa"),
        "oa_status": payload.get("oa_status"),
        "oa_url": best.get("url"),
        "pdf_url": best.get("url_for_pdf"),
        "host_type": best.get("host_type"),
        "license": best.get("license"),
        "locations": locations,
    }


def normalize_core(work):
    """CORE work → 统一记录。"""
    if not work:
        return None
    doi = (work.get("doi") or "").replace("https://doi.org/", "").strip()
    authors = []
    for a in work.get("authors") or []:
        name = a.get("name")
        if name:
            authors.append({"name": name})
    year = work.get("yearPublished")
    source = (work.get("source") or {})
    venue = source.get("title") or work.get("publisher") or ""
    ext = {}
    if doi:
        ext["DOI"] = doi
    if work.get("id"):
        ext["CORE"] = str(work.get("id"))
    fulltext_urls = work.get("sourceFulltextUrls") or []
    return {
        "paperId": ("DOI:" + doi) if doi else (str(work.get("id")) if work.get("id") else None),
        "title": work.get("title") or "",
        "year": int(year) if str(year).isdigit() else None,
        "venue": venue,
        "authors": authors,
        "externalIds": ext,
        "citationCount": work.get("citedByCount"),
        "publicationDate": work.get("firstPublicationDate") or "",
        "publicationTypes": [work.get("type") or ""] if work.get("type") else [],
        "abstract": work.get("abstract") or "",
        "url": work.get("downloadUrl") or (work.get("url") or ""),
        "fullText": work.get("fullText") or "",
        "fullTextUrls": fulltext_urls,
        "_meta": {"source": "core"},
    }


class OAClient(object):
    def __init__(self, email=None, core_api_key=None, timeout=120, proxy=None,
                 trust_env=True, verbose=True):
        try:
            import requests
        except ImportError:
            raise SystemExit("缺少依赖：pip install requests")

        import s2api
        self._requests = requests
        self.email = email or s2api.resolve_key_from_env(("UNPAYWALL_EMAIL",))
        self.core_api_keys = s2api.resolve_prefixed_keys("CORE_API_KEY", core_api_key)
        self.core_api_key = self.core_api_keys[0] if self.core_api_keys else None
        self._core_cursor = 0
        self.timeout = timeout
        self.verbose = verbose
        self.session = requests.Session()
        import s2api
        s2api.configure_session(self.session, proxy=proxy, trust_env=trust_env)
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.session.headers["User-Agent"] = "lit-search/1.0 (skill)"
        if len(self.core_api_keys) > 1:
            self._log("  CORE key 池：%d 个，轮流使用" % len(self.core_api_keys))

    def _log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    def _get(self, url, params, headers=None, allow_status=()):
        try:
            resp = self.session.get(url, params=params, headers=headers,
                                    timeout=self.timeout)
        except self._requests.RequestException as exc:
            raise OAError("网络请求失败：%s" % exc)
        if resp.status_code == 429:
            raise OARateLimitError(
                "HTTP 429：%s 限流。已停止，不再重试。" % url.split("/")[2])
        if resp.status_code != 200 and resp.status_code not in allow_status:
            raise OAError("HTTP %s：%s" % (resp.status_code, resp.text[:300]))
        return resp

    # -- Unpaywall --------------------------------------------------------

    def unpaywall(self, doi):
        """查单条 DOI 的 OA 状态与最佳 PDF 链接。"""
        if not self.email:
            raise OAError("缺少 UNPAYWALL_EMAIL（Unpaywall 要求真实邮箱）")
        clean = str(doi).replace("https://doi.org/", "").strip()
        resp = self._get(UNPAYWALL_API + clean, {"email": self.email})
        try:
            payload = resp.json()
        except ValueError:
            raise OAError("Unpaywall 返回不是 JSON")
        return normalize_unpaywall(clean, payload)

    def unpaywall_many(self, dois):
        out = []
        for doi in dois:
            try:
                out.append(self.unpaywall(doi))
            except OAError as exc:
                self._log("  Unpaywall %s 失败：%s" % (doi, exc))
        return out

    def annotate_oa(self, records):
        """给记录补 openAccess 字段（批量查询 DOIs）。"""
        dois = [r.get("externalIds", {}).get("DOI") for r in records]
        dois = [d for d in dois if d]
        if not dois:
            return records
        results = self.unpaywall_many(dois)
        by_doi = {r["doi"]: r for r in results}
        for rec in records:
            doi = rec.get("externalIds", {}).get("DOI")
            if doi and doi in by_doi:
                rec["openAccess"] = by_doi[doi]
        return records

    # -- CORE -------------------------------------------------------------

    def _next_core_key(self):
        """轮换取下一个 key（分摊配额用）。"""
        if not self.core_api_keys:
            return None
        key = self.core_api_keys[self._core_cursor % len(self.core_api_keys)]
        self._core_cursor += 1
        return key

    def _core_get(self, url, params):
        """带 key 轮换的 CORE 请求。

        - 401/403：当前 key 无效或无权限 → 换下一个 key 重试（最多轮完一轮）；
        - 429：按本 skill 的硬规则**立即停止**，不靠换 key 绕过限流；
        - 其余错误：直接报错。
        """
        if not self.core_api_keys:
            raise OAError("缺少 CORE_API_KEY（CORE API 必需）")
        tried = 0
        total = len(self.core_api_keys)
        while True:
            key = self._next_core_key()
            resp = self._get(url, params, headers={"Authorization": "Bearer %s" % key},
                             allow_status=(401, 403))
            if resp.status_code in (401, 403) and tried < total - 1:
                tried += 1
                self._log("  CORE key 被拒（HTTP %s），换下一个 key 重试" % resp.status_code)
                continue
            if resp.status_code != 200:
                raise OAError("HTTP %s：%s" % (resp.status_code, resp.text[:300]))
            return resp

    def core_search(self, query, limit=20, offset=0):
        resp = self._core_get(CORE_API + "search/works", {
            "q": query, "limit": limit, "offset": offset,
        })
        try:
            payload = resp.json()
        except ValueError:
            raise OAError("CORE 返回不是 JSON")
        records = []
        for work in payload.get("results") or []:
            rec = normalize_core(work)
            if rec:
                records.append(rec)
        self._log("  CORE 命中 %s 条，取回 %d 条"
                  % (payload.get("totalHits"), len(records)))
        return records

    def core_work(self, work_id):
        resp = self._core_get(CORE_API + "works/" + str(work_id), {})
        try:
            payload = resp.json()
        except ValueError:
            raise OAError("CORE 返回不是 JSON")
        return normalize_core(payload)

    # -- 下载（需批准） ----------------------------------------------------

    def build_download_plan(self, records, directory="downloads"):
        """生成下载计划（只描述，不执行）。"""
        items = []
        for rec in records or []:
            title = rec.get("title") or "(untitled)"
            doi = rec.get("externalIds", {}).get("DOI", "")
            urls = []
            oa = rec.get("openAccess") or {}
            if oa.get("pdf_url"):
                urls.append(("pdf", oa["pdf_url"], "unpaywall"))
            elif oa.get("oa_url"):
                urls.append(("link", oa["oa_url"], "unpaywall"))
            if rec.get("pdf_url"):
                urls.append(("pdf", rec["pdf_url"], "unpaywall"))
            elif rec.get("oa_url"):
                urls.append(("link", rec["oa_url"], "unpaywall"))
            for u in rec.get("fullTextUrls") or []:
                urls.append(("fulltext", u, "core"))
            for u in rec.get("pdfUrls") or []:
                urls.append(("pdf", u, "record"))
            if rec.get("url") and rec.get("url", "").lower().endswith(".pdf"):
                urls.append(("pdf", rec["url"], "record"))
            seen = set()
            for kind, url, origin in urls:
                if not url or url in seen:
                    continue
                seen.add(url)
                host = url.split("/")[2] if "://" in url else ""
                items.append({
                    "title": title,
                    "doi": doi,
                    "kind": kind,
                    "origin": origin,
                    "host": host,
                    "url": url,
                    "directory": directory,
                })
        return {"directory": directory, "items": items}

    def download(self, plan, confirm=False):
        """执行下载。confirm=False 时只回显计划，等待批准。

        返回 {"status": "awaiting_approval", "plan": ...} 或
             {"status": "completed", "downloaded": [...], "failed": [...]}。
        """
        items = (plan or {}).get("items") or []
        if not items:
            return {"status": "completed", "downloaded": [], "failed": [],
                    "note": "计划为空，无文件可下载"}
        if not confirm:
            return {"status": "awaiting_approval", "plan": plan,
                    "note": "需人工批准后，以 confirm=True 重新执行"}

        directory = (plan or {}).get("directory") or "downloads"
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError as exc:
                raise OAError("无法创建目录 %s：%s" % (directory, exc))

        downloaded, failed = [], []
        for item in items:
            safe = "".join(c if c.isalnum() or c in "-_." else "_"
                           for c in (item.get("doi") or item.get("title") or "doc"))[:80]
            ext = ".pdf" if item.get("kind") == "pdf" else ".txt"
            suffix = ext if safe.lower().endswith(ext) else safe + ext
            path = os.path.join(directory, suffix)
            try:
                resp = self._get(item["url"], {})
                with open(path, "wb") as fh:
                    fh.write(resp.content)
                downloaded.append({"path": path, "url": item["url"],
                                   "bytes": len(resp.content)})
                self._log("  已下载 %s (%d bytes)" % (path, len(resp.content)))
            except (OAError, OSError) as exc:
                failed.append({"url": item["url"], "error": str(exc)})
        return {"status": "completed", "downloaded": downloaded, "failed": failed}
