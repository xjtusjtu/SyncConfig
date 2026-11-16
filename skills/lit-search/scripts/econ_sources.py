# -*- coding: utf-8 -*-
"""经济学预印本与工作论文渠道：RePEc/IDEAS + SSRN（网页抓取）。

脆弱性说明（重要）
--------------------
本模块依赖第三方网页 HTML 结构，**随时可能因改版失效**：
- IDEAS：https://ideas.repec.org/cgi-bin/htsearch
- SSRN： https://papers.ssrn.com/sol3/results.cfm
两者均为公开页面抓取，无官方开放 API，可能触发限流或验证码。
解析失败时返回空结果并告警，不抛异常中断批量任务。

补充渠道：Crossref 按 ISSN 过滤（用本模块内置的经济学 ISSN 种子表），
这一路是官方 API、稳定，**优先于网页抓取**。

Python 3.7+，依赖 requests；HTML 解析用标准库 re / html。
"""

from __future__ import print_function

import re
import sys
from html import unescape

IDEAS_URL = "https://ideas.repec.org/cgi-bin/htsearch"
IDEAS_URL2 = "https://ideas.repec.org/cgi-bin/htsearch2"
SSRN_URL = "https://papers.ssrn.com/sol3/results.cfm"

# 常用经济学/管理学期刊 ISSN 种子表（用于 Crossref 过滤，稳定可靠）
ISSN_SEEDS = {
    "0304-4076": "Journal of Econometrics",
    "0012-9682": "Econometrica",
    "0002-8282": "American Economic Review",
    "2640-205X": "American Economic Review: Insights",
    "0034-6527": "Review of Economic Studies",
    "0013-0133": "Economic Journal",
    "0741-6261": "RAND Journal of Economics",
    "0022-3808": "Journal of Political Economy",
    "0033-5533": "Quarterly Journal of Economics",
    "0025-1909": "Management Science",
    "0022-1082": "Journal of Finance",
    "0304-405X": "Journal of Financial Economics",
    "0893-9454": "Review of Financial Studies",
    "0004-3688": "Journal of Business",
    "0022-1529": "Journal of Marketing",
    "0147-2096": "Marketing Science",
    "1047-9037": "Information Systems Research",
    "0276-7783": "MIS Quarterly",
    "0143-2095": "Strategic Management Journal",
    "1047-7039": "Organization Science",
    "0022-1360": "Journal of International Business Studies",
    "0034-6535": "Review of Economics and Statistics",
    "0047-2727": "Journal of Public Economics",
    "0734-306X": "Journal of Labor Economics",
    "0022-166X": "Journal of Human Resources",
    "0735-0015": "Journal of Business & Economic Statistics",
    "1368-422X": "Econometrics Journal",
    "1945-7782": "American Economic Journal: Applied Economics",
    "1945-7707": "American Economic Journal: Economic Policy",
    "1945-7669": "American Economic Journal: Macroeconomics",
    "1945-7782 ": "",
    "1468-0262": "Review of Finance",
    "1540-6261": "Review of Economic Studies (ISSN)",
    "1573-4416": "Economics Letters",
    "1468-2354": "Journal of Economic Behavior & Organization",
}

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _strip_html(text):
    return _WS_RE.sub(" ", unescape(_TAG_RE.sub(" ", text or ""))).strip()


class EconSourcesError(Exception):
    pass


class EconSourcesClient(object):
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
            "Mozilla/5.0 (compatible; lit-search/1.0; research retrieval)")
        self.session.headers["Accept-Language"] = "en-US,en;q=0.9"

    def _log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    def _fetch(self, url, params, method="GET", data=None):
        try:
            if method == "POST":
                resp = self.session.post(url, data=data, timeout=self.timeout)
            else:
                resp = self.session.get(url, params=params, timeout=self.timeout)
        except self._requests.RequestException as exc:
            hint = ""
            if "ssrn" in url:
                hint = ("；SSRN 的边缘节点会在 TLS 阶段重置非浏览器连接，"
                        "属反爬策略，需浏览器自动化访问")
            self._log("  [脆弱渠道] 请求失败 %s：%s%s" % (url, exc, hint))
            return ""
        if resp.status_code == 429:
            self._log("  [脆弱渠道] HTTP 429，已停止该渠道的请求")
            return ""
        if resp.status_code in (403, 503):
            self._log("  [脆弱渠道] HTTP %s（可能是 Cloudflare 人机校验 / 反爬；"
                      "该源需浏览器自动化访问，脚本无法直取）" % resp.status_code)
            return ""
        if resp.status_code != 200:
            self._log("  [脆弱渠道] HTTP %s（页面结构可能已变化）" % resp.status_code)
            return ""
        return resp.text

    # -- RePEc / IDEAS ----------------------------------------------------

    def ideas_search(self, query, limit=20):
        params = {
            "q": query, "cmd": "Search!", "m": "all", "fmt": "long",
            "wm": "wrd", "sp": "1", "sy": "1", "dt": "range",
            "ul": "", "de": "",
        }
        html = self._fetch(IDEAS_URL2, params, method="POST", data={"q": query})
        if not html or "RePEc:" not in html:
            fallback = self._fetch(IDEAS_URL, params)
            if fallback and "RePEc:" in fallback:
                html = fallback
        if not html:
            return []
        if "RePEc:" not in html:
            self._log("  [脆弱渠道] IDEAS 返回的是 JS 外壳页（未渲染结果）。"
                      "IDEAS 已改版，纯 HTTP 抓取可能取不到结果："
                      "改用 crossref（稳定）或 openalex(type:preprint)，"
                      "或用浏览器自动化访问。")
            return []
        blocks = re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", html,
                            re.S | re.I)
        records = []
        for dt, dd in blocks[: limit * 2]:
            link = re.search(r'href="([^"]+)"[^>]*>(.*?)</a>', dt, re.S | re.I)
            if not link:
                continue
            url = link.group(1)
            title = _strip_html(link.group(2))
            body = _strip_html(dd)
            handle = ""
            m = re.search(r"RePEc:\s*([A-Za-z0-9:_\-\.]+)", body)
            if m:
                handle = m.group(1)
            year = ""
            ym = re.search(r"\b(19|20)\d{2}\b", body)
            if ym:
                year = ym.group(0)
            authors = []
            am = re.search(r"Author\(s\):\s*(.+?)(?:\s+Date:|\s+Abstract:|$)",
                           body, re.I)
            if am:
                for a in re.split(r",\s*|\s+and\s+", am.group(1)):
                    a = a.strip()
                    if a and not a.lower().startswith("download"):
                        authors.append({"name": a})
            if url.startswith("/"):
                url = "https://ideas.repec.org" + url
            records.append({
                "paperId": handle or url,
                "title": title,
                "year": int(year) if year else None,
                "venue": "RePEc working paper",
                "authors": authors,
                "externalIds": {"RePEc": handle} if handle else {},
                "citationCount": None,
                "publicationDate": "",
                "publicationTypes": ["working paper"],
                "abstract": body,
                "url": url,
                "_meta": {"source": "ideas", "fragile": True},
            })
        self._log("  IDEAS 返回 %d 条（网页抓取，结构可能变化）" % len(records))
        return records[:limit]

    # -- SSRN -------------------------------------------------------------

    def ssrn_search(self, query, limit=20):
        params = {
            "RequestTimeout": "50000000",
            "txtKey_Words": query,
            "sort": "ab_agn",
            "sortOrder": "desc",
        }
        html = self._fetch(SSRN_URL, params)
        if not html:
            return []
        hits = re.findall(
            r'href="(/sol3/papers\.cfm\?abstract_id=(\d+))"[^>]*>(.*?)</a>',
            html, re.S | re.I)
        records = []
        seen = set()
        for path, aid, title in hits:
            if aid in seen:
                continue
            seen.add(aid)
            clean_title = _strip_html(title)
            if not clean_title:
                continue
            records.append({
                "paperId": "SSRN:" + aid,
                "title": clean_title,
                "year": None,
                "venue": "SSRN working paper",
                "authors": [],
                "externalIds": {"SSRN": aid},
                "citationCount": None,
                "publicationDate": "",
                "publicationTypes": ["working paper"],
                "abstract": "",
                "url": "https://papers.ssrn.com" + path,
                "_meta": {"source": "ssrn", "fragile": True},
            })
        self._log("  SSRN 返回 %d 条（网页抓取，结构可能变化）" % len(records))
        return records[:limit]

    # -- Crossref（稳定替代） --------------------------------------------

    def crossref_issn_filter(self, issns=None):
        """生成 Crossref 的 ISSN 过滤串（稳定渠道，优先使用）。"""
        keys = issns or list(k for k in ISSN_SEEDS if k.strip())
        return ",".join("issn:%s" % k.strip() for k in keys)

    def crossref_search(self, query, limit=20, issns=None, types=None):
        """Crossref 检索（官方 API，稳定）。返回统一记录。

        types 例：["posted-content"] 取预印本；["journal-article"] 取期刊论文。
        """
        import crossref as crossref_mod
        filters = []
        issn_filter = self.crossref_issn_filter(issns)
        if issn_filter:
            filters.append(issn_filter)
        for t in (types or []):
            filters.append("type:%s" % t)
        client = crossref_mod.CrossrefClient(timeout=60, verbose=False)
        items, total = client.search(query=query, rows=min(limit, 100),
                                     filters=",".join(filters) if filters else None)
        records = [crossref_mod.normalize(item) for item in items]
        records = [r for r in records if r]
        for rec in records:
            rec.setdefault("_meta", {})["source"] = "crossref"
        self._log("  Crossref(ISSN 过滤) 返回 %d 条" % len(records))
        return records[:limit]

    # -- 统一入口 ---------------------------------------------------------

    def search(self, query, limit=20, sources=("crossref", "ideas", "ssrn")):
        """多源检索。crossref 为稳定渠道；ideas/ssrn 为脆弱网页抓取。"""
        records = []
        if "crossref" in sources:
            try:
                records.extend(self.crossref_search(query, limit=limit))
            except Exception as exc:
                self._log("  Crossref 失败：%s" % exc)
        for source in ("ideas", "ssrn"):
            if source not in sources:
                continue
            try:
                records.extend(getattr(self, "%s_search" % source)(query, limit=limit))
            except Exception as exc:
                self._log("  %s 失败：%s" % (source, exc))
        return records
