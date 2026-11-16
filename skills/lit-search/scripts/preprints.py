# -*- coding: utf-8 -*-
"""预印本渠道：arXiv（Atom XML）+ bioRxiv / medRxiv（JSON API）。

- arXiv：标准库解析 Atom XML，支持分类（cat:）、日期区间、排序。限速 3s/请求。
- bioRxiv/medRxiv：只支持按日期区间浏览（无关键词检索），可关联预印本↔正式发表版。

Python 3.7+，仅依赖 requests + 标准库。
"""

from __future__ import print_function

import re
import sys
import time
import xml.etree.ElementTree as ET

ARXIV_API = "https://export.arxiv.org/api/query"
BIORXIV_API = "https://api.biorxiv.org/details"
BIORXIV_PUBS = "https://api.biorxiv.org/pubs"
ATOM = "{http://www.w3.org/2005/Atom}"


class PreprintError(Exception):
    pass


class PreprintRateLimitError(PreprintError):
    """429：按策略立即停止。"""


def _cjk(text):
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def normalize_arxiv(entry):
    """Atom entry → 统一记录。"""
    def txt(path):
        node = entry.find(path)
        if node is None or node.text is None:
            return ""
        return " ".join(node.text.split())

    arxiv_id = txt(ATOM + "id")
    arxiv_id = arxiv_id.rsplit("/abs/", 1)[-1] if "/abs/" in arxiv_id else arxiv_id
    title = txt(ATOM + "title")
    summary = txt(ATOM + "summary")
    published = txt(ATOM + "published")
    updated = txt(ATOM + "updated")

    authors = []
    for a in entry.findall(ATOM + "author"):
        name = (a.findtext(ATOM + "name") or "").strip()
        if name:
            authors.append({"name": name})

    doi = txt(ATOM + "doi")
    journal_ref = txt(ATOM + "journal_ref")
    primary = entry.find(ATOM + "primary_category")
    category = primary.get("term") if primary is not None else ""
    categories = [c.get("term") for c in entry.findall(ATOM + "category")
                  if c.get("term")]

    ext = {}
    if arxiv_id:
        ext["ArXiv"] = arxiv_id
    if doi:
        ext["DOI"] = doi

    pub_types = ["preprint"]
    if journal_ref:
        pub_types.append("conference")

    pdf_url = ("https://arxiv.org/pdf/%s" % arxiv_id) if arxiv_id else ""

    return {
        "paperId": ("arXiv:" + arxiv_id) if arxiv_id else None,
        "title": title,
        "year": int(published[:4]) if published[:4].isdigit() else None,
        "venue": journal_ref or ("arXiv " + category if category else "arXiv"),
        "authors": authors,
        "externalIds": ext,
        "citationCount": None,
        "publicationDate": published,
        "publicationTypes": pub_types,
        "abstract": summary,
        "url": ("https://arxiv.org/abs/%s" % arxiv_id) if arxiv_id else "",
        "updated": updated,
        "categories": categories,
        "pdfUrls": [pdf_url] if pdf_url else [],
        "_meta": {"source": "arxiv"},
    }


def normalize_biorxiv(item, server="biorxiv"):
    """bioRxiv/medRxiv details 记录 → 统一记录。"""
    doi = item.get("doi") or ""
    title = item.get("title") or ""
    authors = []
    for name in (item.get("authors") or "").split(";"):
        name = name.strip()
        if name:
            authors.append({"name": name})
    year = item.get("year")
    date = item.get("date") or ""
    if not str(year or "").isdigit() and len(date) >= 4 and date[:4].isdigit():
        year = date[:4]

    ext = {}
    if doi:
        ext["DOI"] = doi
    if item.get("category"):
        ext["RxivCategory"] = item.get("category")

    venue = "%s preprint" % ("medRxiv" if server == "medrxiv" else "bioRxiv")
    return {
        "paperId": ("DOI:" + doi) if doi else None,
        "title": title,
        "year": int(year) if str(year).isdigit() else None,
        "venue": venue,
        "authors": authors,
        "externalIds": ext,
        "citationCount": None,
        "publicationDate": date,
        "publicationTypes": ["preprint"],
        "abstract": item.get("abstract") or "",
        "url": ("https://doi.org/%s" % doi) if doi else "",
        "version": item.get("version"),
        "server": server,
        "_meta": {"source": server},
    }


class PreprintClient(object):
    def __init__(self, timeout=60, proxy=None, trust_env=True, verbose=True):
        try:
            import requests
        except ImportError:
            raise SystemExit("缺少依赖：pip install requests")

        self._requests = requests
        self.timeout = timeout
        self.verbose = verbose
        self.session = requests.Session()
        import s2api
        s2api.configure_session(self.session, proxy=proxy, trust_env=trust_env)
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.session.headers["User-Agent"] = (
            "Mozilla/5.0 (compatible; lit-search/1.0; +research retrieval)")
        self._last_arxiv = 0.0

    def _log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    # -- arXiv ------------------------------------------------------------

    def arxiv_search(self, query, max_results=20, start=0, sort_by="relevance",
                     sort_order="descending", categories=None, date_range=None):
        """query 为 arXiv 语法（all:、ti:、au:、cat:…）。"""
        params = {
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }
        if categories:
            params["search_query"] = "(%s) AND (%s)" % (
                query, " OR ".join("cat:%s" % c for c in categories))
        if date_range:
            mindate, maxdate = date_range
            params["search_query"] = "(%s) AND submittedDate:[%s TO %s]" % (
                params["search_query"], mindate, maxdate)

        gap = time.time() - self._last_arxiv
        if gap < 3.0:
            time.sleep(3.0 - gap)
        self._last_arxiv = time.time()

        try:
            resp = self.session.get(ARXIV_API, params=params, timeout=self.timeout)
        except self._requests.RequestException as exc:
            raise PreprintError("arXiv 请求失败：%s" % exc)
        if resp.status_code == 429:
            raise PreprintRateLimitError(
                "HTTP 429：arXiv 限流。已停止，不再重试。")
        if resp.status_code != 200:
            raise PreprintError("HTTP %s：%s" % (resp.status_code, resp.text[:300]))
        try:
            root = ET.fromstring(resp.text)
        except ET.ParseError as exc:
            raise PreprintError("arXiv XML 解析失败：%s" % exc)

        records = []
        for entry in root.findall(ATOM + "entry"):
            rec = normalize_arxiv(entry)
            if rec:
                records.append(rec)
        total = root.findtext("{http://a9.com/-/spec/opensearch/1.1/}totalResults") or ""
        self._log("  arXiv 命中约 %s 条，取回 %d 条" % (total, len(records)))
        return records

    # -- bioRxiv / medRxiv ------------------------------------------------

    def biorxiv_details(self, server="biorxiv", date_range=None, cursor=0,
                        limit=100):
        """按日期区间浏览。date_range=(start,end)，格式 YYYY-MM-DD。"""
        if date_range:
            interval = "%s/%s" % (date_range[0], date_range[1])
        else:
            interval = "%s/%s" % (time.strftime("%Y-%m-01"), time.strftime("%Y-%m-%d"))
        url = "%s/%s/%s/%s/json" % (BIORXIV_API, server, interval, cursor)
        payload = self._get_json(url)
        return self._parse_biorxiv(payload, server, limit)

    def biorxiv_published(self, server="biorxiv", date_range=None, cursor=0,
                          limit=100):
        """预印本→正式发表版的对应关系。"""
        if date_range:
            interval = "%s/%s" % (date_range[0], date_range[1])
        else:
            interval = "%s/%s" % (time.strftime("%Y-%m-01"), time.strftime("%Y-%m-%d"))
        url = "%s/%s/%s/%s/json" % (BIORXIV_PUBS, server, interval, cursor)
        payload = self._get_json(url)
        return self._parse_biorxiv(payload, server, limit)

    def _parse_biorxiv(self, payload, server, limit):
        collection = (payload or {}).get("collection") or []
        records = []
        for item in collection:
            rec = normalize_biorxiv(item, server)
            if rec:
                if item.get("published_doi"):
                    rec["externalIds"]["PublishedDOI"] = item["published_doi"]
                    rec["publishedDoi"] = item["published_doi"]
                    rec["publishedJournal"] = item.get("published_journal") or ""
                records.append(rec)
        self._log("  %s 返回 %d 条" % (server, len(records)))
        return records[:limit] if limit else records

    def _get_json(self, url):
        try:
            resp = self.session.get(url, timeout=self.timeout)
        except self._requests.RequestException as exc:
            raise PreprintError("请求失败：%s" % exc)
        if resp.status_code == 429:
            raise PreprintRateLimitError(
                "HTTP 429：%s 限流。已停止，不再重试。" % url.split("/")[2])
        if resp.status_code != 200:
            raise PreprintError("HTTP %s：%s" % (resp.status_code, resp.text[:300]))
        try:
            return resp.json()
        except ValueError:
            raise PreprintError("返回不是 JSON：%s" % resp.text[:200])

    # -- 跨库检索 ---------------------------------------------------------

    def search(self, source, query=None, limit=20, date_range=None,
               categories=None, sort_by="relevance", strict_category=False):
        """统一入口：source ∈ arxiv | biorxiv | medrxiv。

        strict_category=True 时做本地分类校验：arXiv 的 `cat:` 过滤并不总是
        严格生效，可能返回其它学科的论文，这里按记录里的 categories 复核。
        """
        if source == "arxiv":
            records = self.arxiv_search(query or "all:", max_results=limit,
                                        categories=categories,
                                        date_range=date_range)
            if strict_category and categories:
                wanted = set(c.lower() for c in categories)
                kept = []
                for rec in records:
                    got = set(c.lower() for c in (rec.get("categories") or []))
                    if got & wanted:
                        kept.append(rec)
                dropped = len(records) - len(kept)
                if dropped:
                    self._log("  分类校验：剔除 %d 条分类不符的记录" % dropped)
                records = kept
            return records
        if source in ("biorxiv", "medrxiv"):
            records = self.biorxiv_details(server=source, date_range=date_range,
                                           limit=limit)
            return self._filter_keywords(records, query)
        raise PreprintError("未知预印本源：%s" % source)

    def _filter_keywords(self, records, query):
        if not query:
            return records
        terms = [t.lower() for t in re.findall(r"[^\s]+", query) if len(t) > 2]
        out = []
        for rec in records:
            blob = ("%s %s" % (rec.get("title", ""), rec.get("abstract", ""))).lower()
            if all(t in blob for t in terms):
                out.append(rec)
        return out
