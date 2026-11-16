# -*- coding: utf-8 -*-
"""NBER 工作论文通道（美国国家经济研究局，经济学工作论文主源）。

接口特点：
- 官方 JSON API，**无需 key**，无需登录；
- 端点：/api/v1/working_page_listing/contentType/working_paper/{_|programs/名称}/search
- 摘要字段只给前约 300 字符；作者字段含 HTML 标签，需清洗；
- DOI 可由编号直接构造：10.3386/w{number}；
- PDF 直链规律：https://www.nber.org/system/files/working_papers/w{n}/w{n}.pdf
- 无日期过滤参数，按相关度排序；需要按年筛时在本地过滤 displaydate。

Python 3.7+，依赖 requests。
"""

from __future__ import print_function

import re
import sys
import time

API = "https://www.nber.org/api/v1/working_page_listing/contentType/working_paper"
PAPER_BASE = "https://www.nber.org"
PDF_BASE = "https://www.nber.org/system/files/working_papers"

# NBER 项目（路径用 + 代替空格）
PROGRAMS = [
    "Economic Fluctuations and Growth",
    "Labor Studies",
    "Industrial Organization",
    "Public Economics",
    "Economics of Health",
    "Development Economics",
    "International Finance and Macroeconomics",
    "International Trade and Investment",
    "Monetary Economics",
    "Corporate Finance",
    "Asset Pricing",
    "Economics of Education",
    "Economics of Aging",
    "Children and Families",
    "Law and Economics",
    "Environment and Energy Economics",
    "Political Economy",
]

_TAG_RE = re.compile(r"<[^>]+>")


class NBERError(Exception):
    pass


class NBERRateLimitError(NBERError):
    """429：按策略立即停止。"""


def _strip_html(text):
    return re.sub(r"\s+", " ", _TAG_RE.sub("", text or "")).strip()


def _year_of(display_date):
    """'May 2023' / '2023' → 2023。"""
    if not display_date:
        return None
    m = re.search(r"(19|20)\d{2}", display_date)
    return int(m.group(0)) if m else None


def nber_doi(number):
    """w31201 → 10.3386/w31201。"""
    if not number:
        return ""
    num = str(number).lower()
    if num.startswith("w"):
        num = num[1:]
    return "10.3386/w%s" % num if num else ""


def nber_pdf_url(number):
    """w31201 → NBER 直链 PDF。"""
    if not number:
        return ""
    num = str(number).lower()
    if not num.startswith("w"):
        num = "w" + num
    return "%s/%s/%s.pdf" % (PDF_BASE, num, num)


def normalize(item):
    """NBER results[] 元素 → 统一记录。"""
    if not item:
        return None
    url = item.get("url") or ""
    number = url.rsplit("/", 1)[-1] if url else ""
    authors = []
    for raw in item.get("authors") or []:
        name = _strip_html(raw)
        if name:
            authors.append({"name": name})
    doi = nber_doi(number)
    ext = {}
    if doi:
        ext["DOI"] = doi
    if number:
        ext["NBER"] = number
    return {
        "paperId": ("NBER:" + number) if number else None,
        "title": item.get("title") or "",
        "year": _year_of(item.get("displaydate")),
        "venue": "NBER Working Paper",
        "authors": authors,
        "externalIds": ext,
        "citationCount": None,
        "publicationDate": item.get("displaydate") or "",
        "publicationTypes": ["working paper"],
        "abstract": _strip_html(item.get("abstract") or ""),
        "url": (PAPER_BASE + url) if url.startswith("/") else url,
        "pdfUrl": nber_pdf_url(number),
        "program": item.get("program") or "",
        "newThisWeek": bool(item.get("newthisweek")),
        "_meta": {"source": "nber"},
    }


class NBERClient(object):
    def __init__(self, timeout=60, proxy=None, trust_env=True, verbose=True,
                 min_interval=1.0):
        try:
            import requests
        except ImportError:
            raise SystemExit("缺少依赖：pip install requests")

        import s2api
        self._requests = requests
        self.timeout = timeout
        self.verbose = verbose
        self.min_interval = min_interval
        self._last = 0.0
        self.session = requests.Session()
        s2api.configure_session(self.session, proxy=proxy, trust_env=trust_env)
        self.session.headers["User-Agent"] = "lit-search/1.0 (skill)"

    def _log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    def _get(self, url, params):
        gap = time.time() - self._last
        if gap < self.min_interval:
            time.sleep(self.min_interval - gap)
        self._last = time.time()
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
        except self._requests.RequestException as exc:
            raise NBERError("网络请求失败：%s" % exc)
        if resp.status_code == 429:
            raise NBERRateLimitError(
                "HTTP 429：NBER 限流。已停止，不再重试。")
        if resp.status_code != 200:
            raise NBERError("HTTP %s：%s" % (resp.status_code, resp.text[:300]))
        try:
            return resp.json()
        except ValueError:
            raise NBERError("返回不是 JSON：%s" % resp.text[:200])

    def search(self, query="", program="", page=1, per_page=20,
               new_this_week=False):
        """搜索 NBER 工作论文。

        program 用完整项目名，如 'Labor Studies'。
        """
        if program:
            url = "%s/programs/%s/search" % (API, program.replace(" ", "+"))
        else:
            url = "%s/_/_/search" % API
        params = {"page": page, "perPage": min(per_page, 100)}
        if query:
            params["q"] = query
        if new_this_week:
            params["newThisWeek"] = "true"
        payload = self._get(url, params)
        records = []
        for item in payload.get("results") or []:
            rec = normalize(item)
            if rec:
                records.append(rec)
        total = payload.get("totalResults")
        self._log("  NBER 命中约 %s 条，取回 %d 条" % (total, len(records)))
        return records

    def paper_metadata(self, number):
        """取单篇的 citation_* meta 标签（更完整的题录 + DOI + PDF）。"""
        num = str(number).lower()
        if not num.startswith("w"):
            num = "w" + num
        url = "%s/papers/%s" % (PAPER_BASE, num)
        try:
            resp = self.session.get(url, timeout=self.timeout)
        except self._requests.RequestException as exc:
            raise NBERError("网络请求失败：%s" % exc)
        if resp.status_code == 429:
            raise NBERRateLimitError("HTTP 429：NBER 限流。已停止，不再重试。")
        if resp.status_code != 200:
            raise NBERError("HTTP %s：%s" % (resp.status_code, resp.text[:200]))
        meta = {}
        for m in re.finditer(
                r'<meta\s+name="citation_(\w+)"\s+content="([^"]*)"', resp.text):
            key, value = m.group(1), m.group(2)
            if key == "author":
                meta.setdefault("authors", []).append(value)
            else:
                meta[key] = value
        return meta
