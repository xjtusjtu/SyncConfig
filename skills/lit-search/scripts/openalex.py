# -*- coding: utf-8 -*-
"""OpenAlex 客户端：works 检索、过滤、聚合、cursor 深翻页。

覆盖：
- /works: search / filter / sort / select / group_by / cursor
- 单条 work 详情
- 摘要还原（abstract_inverted_index → 正常文本）
- OA 状态、机构、主题标签

认证：OPENALEX_API_KEY 可选（建议配置，有配额）；OPENALEX_MAILTO 可选。
Python 3.7+，依赖 requests。
"""

from __future__ import print_function

import sys
import time

API = "https://api.openalex.org"

# 常用来源的 OpenAlex source id（可用 /sources?search=<刊名> 核实，不要猜）
# 2026-11-13 实测：SSRN S4210172589 = "SSRN Electronic Journal"（112 万条）；
# NBER S2809516038 = "National Bureau of Economic Research"（3.4 万条）。
SOURCE_IDS = {
    "ssrn": "S4210172589",
    "nber": "S2809516038",
    "aer": "S23254222",
    "econometrica": "S95464858",
    "qje": "S203860005",
    "jpe": "S95323914",
    "restud": "S88935262",
    "joe": "S127742747",
    "management-science": "S33323087",
    "smj": "S102949365",
    "org-science": "S206124708",
    "misq": "S57293258",
    "isr": "S202812398",
    "jmr": "S119950638",
    "journal-of-marketing": "S142990027",
    "marketing-science": "S163534328",
    "jfe": "S149240962",
    "rfs": "S170137484",
}


class OpenAlexError(Exception):
    pass


class OpenAlexRateLimitError(OpenAlexError):
    """429：按策略立即停止。"""


def _restore_abstract(inverted_index):
    """abstract_inverted_index: {word: [positions]} → 正常顺序文本。"""
    if not inverted_index:
        return ""
    positions = []
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def _work_key(work_id):
    """把 DOI / URL / W-id 归一成 OpenAlex 路径可用的标识。"""
    ident = str(work_id).strip()
    if ident.startswith("http"):
        ident = ident.rsplit("/", 1)[-1]
    if ident.lower().startswith("doi:"):
        ident = ident[4:]
    return ident


def _short_id(url):
    """https://openalex.org/W123 → W123"""
    if not url:
        return ""
    return str(url).rstrip("/").rsplit("/", 1)[-1]


def normalize_work(work):
    """OpenAlex work → 统一记录。"""
    if not work:
        return None

    ids = work.get("ids") or {}
    doi = ""
    if work.get("doi"):
        doi = work["doi"].replace("https://doi.org/", "").strip()
    openalex_id = work.get("id") or ""
    openalex_short = openalex_id.rsplit("/", 1)[-1] if openalex_id else ""

    pmid = ""
    pmcid = ""
    for candidate in ids.get("pmid", "").split(";"):
        candidate = candidate.strip()
        if candidate.startswith("pmid:"):
            pmid = candidate[5:]
    for candidate in ids.get("pmcid", "").split(";"):
        candidate = candidate.strip()
        if candidate.startswith("pmcid:"):
            pmcid = candidate[6:]

    authors = []
    for a in work.get("authorships") or []:
        name = (a.get("author") or {}).get("display_name")
        if name:
            authors.append({"name": name})

    venue = ""
    primary = work.get("primary_location") or {}
    source = primary.get("source") or {}
    venue = source.get("display_name") or ""
    if not venue:
        for loc in work.get("locations") or []:
            src = loc.get("source") or {}
            if src.get("display_name"):
                venue = src["display_name"]
                break

    ext = {}
    if doi:
        ext["DOI"] = doi
    if pmid:
        ext["PMID"] = pmid
    if pmcid:
        ext["PMCID"] = pmcid
    if openalex_short:
        ext["OpenAlex"] = openalex_short
    if work.get("ids", {}).get("mag"):
        ext["MAG"] = work["ids"]["mag"]

    oa = work.get("open_access") or {}
    concepts = [c.get("display_name") for c in (work.get("concepts") or [])
                if c.get("display_name")]
    topics = [t.get("display_name") for t in (work.get("topics") or [])
              if t.get("display_name")]

    # PDF 直链：primary → best_oa → 其它 locations（第三方仓库镜像常在这里）
    pdf_urls = []
    best = work.get("best_oa_location") or {}
    for loc in [primary, best] + list(work.get("locations") or []):
        pdf = (loc or {}).get("pdf_url")
        if pdf and pdf not in pdf_urls:
            pdf_urls.append(pdf)
    oa_url = oa.get("oa_url")
    if oa_url and oa_url not in pdf_urls:
        pdf_urls.append(oa_url)

    return {
        "paperId": openalex_short or ("DOI:" + doi if doi else None),
        "title": work.get("display_name") or work.get("title") or "",
        "year": work.get("publication_year"),
        "venue": venue,
        "authors": authors,
        "externalIds": ext,
        "citationCount": work.get("cited_by_count"),
        "publicationDate": work.get("publication_date") or "",
        "publicationTypes": [work.get("type") or ""] if work.get("type") else [],
        "abstract": _restore_abstract(work.get("abstract_inverted_index")),
        "url": primary.get("landing_page_url") or openalex_id,
        "openAccess": {
            "oa_status": oa.get("oa_status"),
            "is_oa": oa.get("is_oa"),
            "oa_url": oa.get("oa_url"),
        },
        "pdfUrls": pdf_urls,
        "concepts": concepts,
        "topics": topics,
        "relatedWorks": [_short_id(x) for x in (work.get("related_works") or [])],
        "referencedWorks": [_short_id(x) for x in (work.get("referenced_works") or [])],
        "_meta": {"source": "openalex"},
    }


class OpenAlexClient(object):
    def __init__(self, api_key=None, mailto=None, timeout=60, proxy=None,
                 trust_env=True, verbose=True):
        try:
            import requests
        except ImportError:
            raise SystemExit("缺少依赖：pip install requests")

        import s2api
        self._requests = requests
        self.api_key = api_key or s2api.resolve_key_from_env(("OPENALEX_API_KEY",))
        self.mailto = mailto or s2api.resolve_key_from_env(("OPENALEX_MAILTO",)) or ""
        self.timeout = timeout
        self.verbose = verbose
        self.session = requests.Session()
        import s2api
        s2api.configure_session(self.session, proxy=proxy, trust_env=trust_env)
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.session.headers["User-Agent"] = "lit-search/1.0 (skill)"

    def _log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    def _params(self, extra):
        params = dict(extra or {})
        if self.api_key:
            params["api_key"] = self.api_key
        if self.mailto:
            params["mailto"] = self.mailto
        return params

    def _get(self, url, params):
        try:
            resp = self.session.get(url, params=self._params(params), timeout=self.timeout)
        except self._requests.RequestException as exc:
            raise OpenAlexError("网络请求失败：%s" % exc)
        if resp.status_code == 429:
            raise OpenAlexRateLimitError(
                "HTTP 429：OpenAlex 限流。已停止，不再重试。%s" % resp.text[:200])
        if resp.status_code != 200:
            raise OpenAlexError("HTTP %s：%s" % (resp.status_code, resp.text[:300]))
        try:
            return resp.json()
        except ValueError:
            raise OpenAlexError("返回不是 JSON：%s" % resp.text[:200])

    # -- works ------------------------------------------------------------

    def works(self, search=None, filter=None, sort=None, per_page=25, page=None,
              cursor=None, select=None, group_by=None):
        params = {"per-page": per_page}
        if search:
            params["search"] = search
        if filter:
            params["filter"] = filter
        if sort:
            params["sort"] = sort
        if page:
            params["page"] = page
        if cursor:
            params["cursor"] = cursor
        if select:
            params["select"] = select
        if group_by:
            params["group_by"] = group_by
        payload = self._get(API + "/works", params)
        return payload

    def search(self, search=None, filter=None, sort=None, limit=25, cursor=False,
               select=None):
        """返回规范化记录列表。cursor=True 时深翻页直到 limit 满足。"""
        per_page = min(200, max(1, limit))
        records = []
        cursor_value = "*"
        while True:
            if cursor:
                payload = self.works(search=search, filter=filter, sort=sort,
                                     per_page=per_page, cursor=cursor_value,
                                     select=select)
            else:
                page = 1
                payload = self.works(search=search, filter=filter, sort=sort,
                                     per_page=per_page, page=page, select=select)
            for work in payload.get("results") or []:
                rec = normalize_work(work)
                if rec:
                    records.append(rec)
            if not cursor:
                break
            if len(records) >= limit:
                break
            cursor_value = ((payload.get("meta") or {}).get("next_cursor"))
            if not cursor_value:
                break
            per_page = min(200, limit - len(records))
            if per_page <= 0:
                break
        self._log("  OpenAlex 返回 %d 条" % len(records))
        return records[:limit] if limit else records

    def get_work(self, work_id):
        """work_id 形如 W2741809807 或 https://openalex.org/W... 或 DOI:10.x/..."""
        ident = str(work_id).strip()
        if ident.startswith("http"):
            ident = ident.rsplit("/", 1)[-1]
        if ident.lower().startswith("doi:"):
            ident = ident[4:]
        url = API + "/works/" + ident
        payload = self._get(url, {})
        return normalize_work(payload)

    def group_by_field(self, field, filter=None, search=None):
        """按字段聚合（如 publication_year、primary_topic）。"""
        payload = self.works(search=search, filter=filter, group_by=field,
                             per_page=200)
        return payload.get("group_by") or []

    def doi_to_work(self, doi):
        return self.get_work("doi:" + doi)

    # -- 引文边（S2 不可用时的稳定替代） --------------------------------

    def citations(self, work_id, limit=50, cursor=None):
        """谁引用了这篇（filter=cites:W...）。返回规范化记录列表。"""
        payload = self._edge("cites", work_id, limit, cursor)
        return [normalize_work(w) for w in payload.get("results") or [] if w]

    def references(self, work_id, limit=50, cursor=None):
        """这篇引用了谁（filter=cited_by:W...）。"""
        payload = self._edge("cited_by", work_id, limit, cursor)
        return [normalize_work(w) for w in payload.get("results") or [] if w]

    def related(self, work_id, limit=25):
        """相关文献（OpenAlex 的 related_works 字段，不是引用边）。"""
        work = self.get_work(_work_key(work_id))
        if not work:
            raise OpenAlexError("未找到作品：%s" % work_id)
        ids = work.get("relatedWorks") or []
        rows = []
        for wid in ids[:limit]:
            try:
                rec = self.get_work(wid)
            except Exception:
                continue
            if rec:
                rows.append(rec)
        return rows

    def _edge(self, field, work_id, limit, cursor):
        """OpenAlex 没有 /works/{id}/cited_by 路径，用 filter 实现。

        cites:W…    → 引用了 W… 的论文
        cited_by:W… → W… 引用的论文
        """
        ident = _work_key(work_id)
        if not ident.upper().startswith("W"):
            work = self.get_work(ident)
            ident = ((work or {}).get("externalIds") or {}).get("OpenAlex") or ""
            if not ident:
                raise OpenAlexError("无法把标识解析为 OpenAlex work id：%s" % work_id)
        params = {"filter": "%s:%s" % (field, ident), "per-page": min(200, max(1, limit))}
        if cursor:
            params["cursor"] = cursor
        return self._get(API + "/works", params)

    # -- 来源 ------------------------------------------------------------

    def source(self, source_id):
        """查 source 元信息（用 /sources?search= 找 id，不要猜）。"""
        if str(source_id).startswith("http"):
            source_id = str(source_id).rsplit("/", 1)[-1]
        return self._get(API + "/sources/" + source_id, {})

    def find_source(self, name):
        """按名称查 source id。"""
        payload = self._get(API + "/sources", {"search": name, "per-page": 5})
        return payload.get("results") or []
