# -*- coding: utf-8 -*-
"""NCBI E-utilities 客户端：PubMed 检索 + PMC 全文 + ID 互转 + BioC。

覆盖：
- PubMed：esearch / esummary / efetch / elink（相关文献、被引、PMC 链接）
- PMC：efetch 全文 JATS XML、BioC 结构化全文
- ID 转换器：PMID ↔ PMCID ↔ DOI ↔ MID

速率：无 key 3 req/s，有 key 10 req/s（NCBI_API_KEY）。
礼貌参数：tool + email（NCBI_EMAIL）。

Python 3.7+，依赖 requests；XML 解析用标准库。
"""

from __future__ import print_function

import os
import re
import sys
import time
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
BIOC = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi"
IDCONV = "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"


class NCBIError(Exception):
    pass


class NCBIRateLimitError(NCBIError):
    """429：按策略立即停止。"""


def _text(node, path, default=""):
    if node is None:
        return default
    found = node.find(path)
    if found is None or found.text is None:
        return default
    return found.text.strip()


def normalize_pubmed(article):
    """把 efetch 的 PubmedArticle 元素转成统一记录。"""
    medline = article.find("MedlineCitation")
    if medline is None:
        return None
    pmid = _text(medline, "PMID")
    art = medline.find("Article")
    title = _text(art, "ArticleTitle")
    journal = _text(art, "Journal/Title") or _text(art, "Journal/ISOAbbreviation")
    year = (_text(art, "Journal/JournalIssue/PubDate/Year")
            or _text(art, "Journal/JournalIssue/PubDate/MedlineDate")[:4])
    volume = _text(art, "Journal/JournalIssue/Volume")
    issue = _text(art, "Journal/JournalIssue/Issue")
    pages = _text(art, "Pagination/MedlinePgn")

    authors = []
    for a in art.findall("AuthorList/Author") if art is not None else []:
        last = _text(a, "LastName")
        fore = _text(a, "ForeName")
        collective = _text(a, "CollectiveName")
        name = (" ".join(x for x in [fore, last] if x)) or collective
        if name:
            authors.append({"name": name})

    abstract_parts = []
    if art is not None:
        for ab in art.findall("Abstract/AbstractText"):
            label = ab.get("Label")
            txt = "".join(ab.itertext()).strip()
            if txt:
                abstract_parts.append(("%s: %s" % (label, txt)) if label else txt)
    abstract = " ".join(abstract_parts)

    doi = ""
    pmcid = ""
    for aid in article.findall("PubmedData/ArticleIdList/ArticleId"):
        idtype = (aid.get("IdType") or "").lower()
        if idtype == "doi":
            doi = (aid.text or "").strip()
        elif idtype == "pmc":
            pmcid = (aid.text or "").strip()

    pub_types = []
    if art is not None:
        for pt in art.findall("PublicationTypeList/PublicationType"):
            if pt.text:
                pub_types.append(pt.text.strip())

    ext = {}
    if doi:
        ext["DOI"] = doi
    if pmid:
        ext["PMID"] = pmid
    if pmcid:
        ext["PMCID"] = pmcid

    return {
        "paperId": ("PMID:" + pmid) if pmid else None,
        "title": title,
        "year": int(year) if (year or "").isdigit() else None,
        "venue": journal,
        "authors": authors,
        "externalIds": ext,
        "citationCount": None,
        "publicationDate": "",
        "publicationTypes": pub_types,
        "abstract": abstract,
        "url": ("https://pubmed.ncbi.nlm.nih.gov/%s/" % pmid) if pmid else "",
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "_meta": {"source": "pubmed"},
    }


class NCBIClient(object):
    def __init__(self, api_key=None, email=None, tool="lit-search", timeout=60,
                 proxy=None, trust_env=True, verbose=True):
        try:
            import requests
        except ImportError:
            raise SystemExit("缺少依赖：pip install requests")

        import s2api
        self._requests = requests
        self.api_key = api_key or s2api.resolve_key_from_env(("NCBI_API_KEY",))
        self.email = email or s2api.resolve_key_from_env(("NCBI_EMAIL",)) or ""
        self.tool = tool
        self.timeout = timeout
        self.verbose = verbose
        self.rps = 10.0 if self.api_key else 3.0
        self._last = 0.0

        self.session = requests.Session()
        import s2api
        s2api.configure_session(self.session, proxy=proxy, trust_env=trust_env)
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.session.headers["User-Agent"] = "lit-search/1.0 (skill)"

    def _log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    def _throttle(self):
        gap = 1.0 / self.rps
        elapsed = time.time() - self._last
        if elapsed < gap:
            time.sleep(gap - elapsed)
        self._last = time.time()

    def _params(self, extra):
        params = dict(extra or {})
        if self.api_key:
            params["api_key"] = self.api_key
        if self.email:
            params["email"] = self.email
        if self.tool:
            params["tool"] = self.tool
        return params

    def _get(self, url, params, expect_json=True):
        self._throttle()
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
        except self._requests.RequestException as exc:
            raise NCBIError("网络请求失败：%s" % exc)
        if resp.status_code == 429:
            raise NCBIRateLimitError(
                "HTTP 429：NCBI 限流。已停止，不再重试。%s" % resp.text[:200])
        if resp.status_code != 200:
            raise NCBIError("HTTP %s：%s" % (resp.status_code, resp.text[:300]))
        if expect_json:
            try:
                return resp.json()
            except ValueError:
                raise NCBIError("返回不是 JSON：%s" % resp.text[:200])
        return resp.text

    # -- PubMed -----------------------------------------------------------

    def esearch(self, term, db="pubmed", retmax=20, retstart=0, sort="relevance",
                datetype=None, mindate=None, maxdate=None):
        params = self._params({
            "db": db, "term": term, "retmax": retmax, "retstart": retstart,
            "retmode": "json",
        })
        if sort:
            params["sort"] = sort
        if datetype:
            params["datetype"] = datetype
        if mindate:
            params["mindate"] = mindate
        if maxdate:
            params["maxdate"] = maxdate
        payload = self._get(EUTILS + "/esearch.fcgi", params)
        result = (payload or {}).get("esearchresult") or {}
        return result.get("idlist") or [], int(result.get("count") or 0)

    def efetch_pubmed(self, pmids):
        if not pmids:
            return []
        xml_text = self._get(EUTILS + "/efetch.fcgi", self._params({
            "db": "pubmed", "id": ",".join(str(x) for x in pmids),
            "retmode": "xml",
        }), expect_json=False)
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            raise NCBIError("PubMed XML 解析失败：%s" % exc)
        out = []
        for article in root.findall("PubmedArticle"):
            rec = normalize_pubmed(article)
            if rec:
                out.append(rec)
        return out

    def search(self, term, retmax=20, sort="relevance", date_range=None,
               pub_types=None):
        """检索并返回带摘要的规范化记录。

        date_range: (mindate, maxdate)，格式 YYYY/MM/DD 或 YYYY。
        pub_types: 如 ["Review", "Randomized Controlled Trial"]，会拼进 term。
        """
        full_term = term
        if pub_types:
            clause = " OR ".join('"%s"[Publication Type]' % p for p in pub_types)
            full_term = "(%s) AND (%s)" % (term, clause)
        mindate = maxdate = None
        if date_range:
            mindate, maxdate = date_range
        ids, total = self.esearch(full_term, retmax=retmax, sort=sort,
                                  datetype="pdat" if (mindate or maxdate) else None,
                                  mindate=mindate, maxdate=maxdate)
        self._log("  PubMed 命中约 %d 条，取回 %d 个 PMID" % (total, len(ids)))
        return self.efetch_pubmed(ids)

    def elink(self, pmid, linkname="pubmed_pubmed", db="pubmed", dbfrom="pubmed"):
        payload = self._get(EUTILS + "/elink.fcgi", self._params({
            "dbfrom": dbfrom, "db": db, "id": pmid, "linkname": linkname,
            "retmode": "json",
        }))
        ids = []
        for linkset in (payload or {}).get("linksets") or []:
            for db_links in linkset.get("linksetdbs") or []:
                ids.extend(db_links.get("links") or [])
        return ids

    def related(self, pmid, limit=20):
        return self.elink(pmid, "pubmed_pubmed")[:limit]

    def cited_by(self, pmid, limit=20):
        return self.elink(pmid, "pubmed_pubmed_citedin")[:limit]

    def pmc_ids(self, pmid):
        return self.elink(pmid, "pubmed_pmc", db="pmc")

    # -- PMC --------------------------------------------------------------

    def pmc_fulltext(self, pmcid):
        """返回 PMC 全文 JATS XML 字符串。pmcid 形如 PMC7029759 或纯数字。"""
        numeric = re.sub(r"^PMC", "", str(pmcid), flags=re.I)
        return self._get(EUTILS + "/efetch.fcgi", self._params({
            "db": "pmc", "id": numeric, "retmode": "xml",
        }), expect_json=False)

    def pmc_sections(self, pmcid):
        """把 JATS 全文拆成 {section_title: text}。"""
        xml_text = self.pmc_fulltext(pmcid)
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            raise NCBIError("PMC XML 解析失败：%s" % exc)
        sections = {}
        body = root.find(".//body")
        if body is None:
            return sections
        for sec in body.findall("sec"):
            title = _text(sec, "title") or "(untitled)"
            parts = []
            for p in sec.iter("p"):
                txt = "".join(p.itertext()).strip()
                if txt:
                    parts.append(txt)
            sections[title] = "\n".join(parts)
        return sections

    def bioc(self, identifier, fmt="json", unicode_ok=True):
        """BioC 结构化全文（段落带 TITLE/ABSTRACT/METHODS/RESULTS 等标签）。"""
        url = "%s/BioC_%s/%s/%s" % (BIOC, fmt, identifier,
                                    "unicode" if unicode_ok else "ascii")
        text = self._get(url, self._params({}), expect_json=(fmt == "json"))
        return text

    # -- ID 转换 ----------------------------------------------------------

    def idconv(self, ids, idtype=None, fmt="json"):
        """PMID ↔ PMCID ↔ DOI ↔ MID 互转。ids 最多 200 个。"""
        params = {"ids": ",".join(str(x) for x in ids), "format": fmt}
        if idtype:
            params["idtype"] = idtype
        if self.email:
            params["email"] = self.email
        if self.tool:
            params["tool"] = self.tool
        return self._get(IDCONV, params, expect_json=(fmt == "json"))
