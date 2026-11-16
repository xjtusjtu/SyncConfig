# -*- coding: utf-8 -*-
"""Semantic Scholar REST client，面向大批量检索。

设计取舍：
- 只做 REST，不做 MCP。Asta MCP 由 agent 直接调工具，不走本模块。
- 批量优先：bulk search（token 续取）+ paper/batch（一次 500 个 ID）。
- 可恢复：调用方保存每页返回的 token，下次从 token 继续。
- 速率：个人 API key 官方口径是 1 req/s，默认按 1 rps 限速，可调。
- 网络：Windows 上 requests 会读取系统代理（注册表），失败时用 --no-proxy
  或 --proxy 显式指定。

Python 3.7+，依赖 requests。
"""

from __future__ import print_function

import json
import os
import re
import sys
import time

GRAPH = "https://api.semanticscholar.org/graph/v1"
RECS = "https://api.semanticscholar.org/recommendations/v1"
DATASETS = "https://api.semanticscholar.org/datasets/v1"

# fields 预设。bulk search 不支持 tldr（既有实践记录，未在官方参数表中列出），
# 需要 tldr 时用 hydrate（batch）再补。
FIELD_PRESETS = {
    "minimal": "title,year,venue,externalIds",
    "standard": (
        "title,year,venue,authors,externalIds,citationCount,"
        "publicationDate,publicationTypes,abstract"
    ),
    "ranking": (
        "title,year,venue,authors,externalIds,citationCount,"
        "influentialCitationCount,publicationDate,abstract"
    ),
    "export": (
        "title,year,venue,authors,externalIds,citationCount,abstract,url,"
        "openAccessPdf,publicationDate,publicationTypes,fieldsOfStudy,journal"
    ),
    "detail": (
        "title,year,venue,authors,externalIds,citationCount,abstract,url,"
        "openAccessPdf,publicationDate,publicationTypes,fieldsOfStudy,journal,tldr"
    ),
    "bibtex": "title,year,venue,authors,externalIds,citationStyles",
}

ENV_NAMES = ("S2_API_KEY", "SEMANTIC_SCHOLAR_API_KEY")

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class S2Error(Exception):
    """API 调用失败（可重试已耗尽，或参数/权限问题）。"""


class S2AuthError(S2Error):
    """401/403：key 缺失、无效或无权限。"""


class S2RateLimitError(S2Error):
    """429：按策略立即停止，不再重试、不再继续后续请求。"""


# --------------------------------------------------------------------------
# key 解析
# --------------------------------------------------------------------------

def _parse_env_file(path):
    """极简 .env 解析：KEY=VALUE，忽略注释与引号。不覆盖已有环境变量。"""
    pairs = []
    if not path or not os.path.isfile(path):
        return pairs
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and v:
                    pairs.append((k, v))
    except (OSError, UnicodeDecodeError):
        pass
    return pairs


def env_candidates():
    """可能存放 S2_API_KEY 的 .env 路径，按优先级排列。

    优先用与 skill 绑定、与工作目录无关的位置，便于把 skill 整体拷到别的机器：
      1. <skill_dir>/.env
      2. ~/.config/lit-search/.env
      3. 当前工作目录及其上级（仅作便利项；在 Obsidian 库里跑时能捡到库根 .env）
    """
    paths = []
    paths.append(os.path.join(SKILL_DIR, ".env"))
    paths.append(os.path.join(os.path.expanduser("~"), ".config", "lit-search", ".env"))

    cur = os.getcwd()
    while True:
        paths.append(os.path.join(cur, ".env"))
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent

    # 去重且保持顺序
    seen, out = set(), []
    for p in paths:
        p = os.path.abspath(p)
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def configure_session(session, proxy=None, trust_env=True):
    """统一配置 requests.Session 的代理与信任设置。

    要点：Windows 注册表里的系统代理会被 requests 自动读取，并**覆盖**
    session 级代理（表现 socks5/http 代理被无视或连错端口）。因此显式传入
    proxy 时关闭 trust_env，保证显式代理优先；同时保留 CA 包自定义
    （REQUESTS_CA_BUNDLE / SSL_CERT_FILE），以适配做 TLS 中间人的代理。
    """
    session.trust_env = trust_env and not proxy
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}
        for var in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE"):
            value = os.environ.get(var)
            if value and os.path.isfile(value):
                session.verify = value
                break
    return session


def resolve_key_from_env(names, explicit=None):
    """按 显式参数 -> 环境变量 -> .env 的顺序取 key。找不到返回 None。"""
    if explicit:
        return explicit.strip()

    for name in names:
        val = os.environ.get(name)
        if val and val.strip():
            return val.strip()

    for path in env_candidates():
        for k, v in _parse_env_file(path):
            if k in names:
                os.environ[k] = v
                return v
    return None


def resolve_keys_from_env(names, explicit=None):
    """按 显式参数 -> 环境变量 -> .env 的顺序取**一组** key。

    names 里既可以写固定名（CORE_API_KEY），也可以写前缀式（CORE_API_KEY*），
    前缀式会收集 CORE_API_KEY、CORE_API_KEY1、CORE_API_KEY2 … 所有匹配项，
    按名称自然顺序返回，供轮流使用分摊配额。
    """
    if explicit:
        values = [v.strip() for v in re.split(r"[,;\s]+", explicit) if v.strip()]
        if values:
            return values

    for name in names:
        val = os.environ.get(name)
        if val and val.strip():
            return [val.strip()]

    for path in env_candidates():
        for k, v in _parse_env_file(path):
            if k in names:
                os.environ[k] = v
                return [v]
    return []


def resolve_prefixed_keys(prefix, explicit=None):
    """收集前缀命中的所有 key（如 CORE_API_KEY1、CORE_API_KEY2），按名称排序。"""
    if explicit:
        values = [v.strip() for v in re.split(r"[,;\s]+", explicit) if v.strip()]
        if values:
            return values

    found = {}
    for name in list(os.environ.keys()):
        if name == prefix or name.startswith(prefix):
            val = (os.environ.get(name) or "").strip()
            if val:
                found[name] = val

    for path in env_candidates():
        for k, v in _parse_env_file(path):
            if k == prefix or k.startswith(prefix):
                os.environ.setdefault(k, v)
                found[k] = v.strip()

    def sort_key(name):
        suffix = name[len(prefix):].strip()
        return (0, int(suffix), "") if suffix.isdigit() else (1, 0, name)

    return [found[name] for name in sorted(found, key=sort_key)]


def resolve_api_key(explicit=None):
    """Semantic Scholar key 的解析入口。"""
    return resolve_key_from_env(ENV_NAMES, explicit)


def key_status():
    """不泄露 key 本身，只报告来源与掩码。"""
    for name in ENV_NAMES:
        if os.environ.get(name):
            val = os.environ[name]
            return {"present": True, "source": "env:" + name, "masked": _mask(val)}
    for path in env_candidates():
        for k, v in _parse_env_file(path):
            if k in ENV_NAMES:
                return {"present": True, "source": path, "masked": _mask(v)}
    return {"present": False, "source": None, "masked": None}


def _mask(val):
    if len(val) <= 8:
        return "*" * len(val)
    return val[:4] + "*" * (len(val) - 8) + val[-4:]


# --------------------------------------------------------------------------
# 工具函数
# --------------------------------------------------------------------------

def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def norm_title(title):
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def paper_doi(paper):
    ext = (paper or {}).get("externalIds") or {}
    return (ext.get("DOI") or "").strip().lower()


def dedup_key(paper):
    """DOI 优先，其次 paperId，最后标题+年份。"""
    doi = paper_doi(paper)
    if doi:
        return "doi:" + doi
    pid = (paper or {}).get("paperId")
    if pid:
        return "pid:" + pid
    return "title:%s|%s" % (norm_title((paper or {}).get("title")), (paper or {}).get("year"))


def dedup(papers):
    """返回 (唯一记录列表, 重复数)。保序。"""
    seen = set()
    out = []
    dup = 0
    for p in papers:
        if not isinstance(p, dict):
            continue
        k = dedup_key(p)
        if k in seen:
            dup += 1
            continue
        seen.add(k)
        out.append(p)
    return out, dup


def build_bool_query(terms=None, phrases=None, required=None, excluded=None,
                     alternatives=None, field=None, fuzzy=False,
                     wildcards=False, boost=None):
    """构造 Semantic Scholar 布尔查询串。

    语法要点：`+词` 必须命中；`-词` 必须不命中；`"短语"` 精确短语；
    `|` 或；空格默认或；`~` 模糊；`*` 词尾通配；`^n` 权重提升。

    terms        普通词（以空格并列，命中任一即可）
    phrases      精确短语列表（整体作为一组）
    required     必须命中的词/短语
    excluded     必须排除的词
    alternatives 备选组列表，每个元素是「词或短语列表」，组内或、组间与
    field        限定字段（如 title、abstract、venue、author）
    """
    def fmt(text):
        text = str(text).strip()
        if not text:
            return ""
        if text.startswith(("+", "-", '"', "(")):
            return text
        if " " in text:
            return '"%s"' % text
        if fuzzy:
            return "%s~" % text
        if wildcards:
            return "%s*" % text
        return text

    parts = []
    for phrase in (phrases or []):
        parts.append('"%s"' % str(phrase).strip())
    for group in (alternatives or []):
        if isinstance(group, str):
            group = [group]
        rendered = " | ".join(fmt(g) for g in group if str(g).strip())
        if rendered:
            parts.append("(%s)" % rendered)
    for term in (terms or []):
        parts.append(fmt(term))
    for term in (required or []):
        rendered = fmt(term)
        if rendered and not rendered.startswith("+"):
            rendered = "+" + rendered
        if rendered:
            parts.append(rendered)
    for term in (excluded or []):
        rendered = fmt(term)
        if rendered and not rendered.startswith("-"):
            rendered = "-" + rendered
        if rendered:
            parts.append(rendered)

    query = " ".join(p for p in parts if p)
    if field:
        query = "%s:%s" % (field, query) if query else "%s:*" % field
    if boost:
        query = "%s^%s" % (query, boost)
    return query


def read_jsonl(path):
    rows = []
    # utf-8-sig 兼容 Windows 编辑器写出的 BOM
    with open(path, "r", encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows, append=False):
    mode = "a" if append else "w"
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with open(path, mode, encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------
# 客户端
# --------------------------------------------------------------------------

class S2Client(object):
    """Semantic Scholar Academic Graph / Recommendations / Datasets 客户端。"""

    def __init__(self, api_key=None, rps=1.0, timeout=60, proxy=None,
                 trust_env=True, max_retries=8, verbose=True, backoff_base=2,
                 backoff_cap=60, retry_429=False):
        try:
            import requests
        except ImportError:
            raise SystemExit("缺少依赖：pip install requests")

        self._requests = requests
        self.api_key = api_key if api_key is not None else resolve_api_key()
        self.rps = float(rps) if rps and rps > 0 else 1.0
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_cap = backoff_cap
        self.retry_429 = retry_429
        self.verbose = verbose
        self._last_call = 0.0

        self.session = requests.Session()
        configure_session(self.session, proxy=proxy, trust_env=trust_env)
        self.session.headers["User-Agent"] = "lit-search/1.0 (skill)"
        if self.api_key:
            self.session.headers["x-api-key"] = self.api_key

    # -- 基础设施 ---------------------------------------------------------

    def _log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    def _throttle(self):
        gap = 1.0 / self.rps
        elapsed = time.time() - self._last_call
        if elapsed < gap:
            time.sleep(gap - elapsed)
        self._last_call = time.time()

    @staticmethod
    def _retry_after(resp):
        try:
            return float(resp.headers.get("Retry-After"))
        except (TypeError, ValueError):
            return None

    def _request(self, method, url, params=None, json_body=None, allow_404=False):
        attempt = 0
        while True:
            self._throttle()
            try:
                if method == "GET":
                    resp = self.session.get(url, params=params, timeout=self.timeout)
                else:
                    resp = self.session.post(url, params=params, json=json_body,
                                             timeout=self.timeout)
            except self._requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise S2Error(
                        "网络请求失败：%s\n提示：若本机走代理，试 --proxy http://127.0.0.1:端口；"
                        "若代理反而不可用，试 --no-proxy。" % exc
                    )
                self._sleep(attempt)
                attempt += 1
                continue

            if resp.status_code == 200:
                try:
                    return resp.json()
                except ValueError:
                    raise S2Error("返回内容不是 JSON：%s" % resp.text[:300])

            if resp.status_code == 404 and allow_404:
                return None

            if resp.status_code == 429:
                # 策略：429 立即停止，不再重试、不再发后续请求（避免继续消耗额度）。
                # 需要"再试一次"时显式传 retry_429=True / --retry-429。
                if not self.retry_429:
                    raise S2RateLimitError(
                        "HTTP 429：速率限制。已按策略立即停止本次检索，"
                        "不再重试、不再发送后续请求。\n"
                        "服务端信息：%s\n"
                        "可选做法：稍后再试、把任务拆小、或改用 --retry-429 允许重试"
                        "（实测 429 属随机拒绝，重试通常可恢复，但会继续消耗额度）。"
                        % resp.text[:200]
                    )
                if attempt >= self.max_retries:
                    raise S2RateLimitError(
                        "HTTP 429，重试 %s 次后放弃：%s" % (attempt, resp.text[:200]))
                wait = self._retry_after(resp) or min(
                    self.backoff_base ** (attempt + 1), self.backoff_cap)
                self._log("  [HTTP 429] %ss 后重试（%s/%s）"
                          % (wait, attempt + 1, self.max_retries))
                time.sleep(wait)
                attempt += 1
                continue

            if resp.status_code in (500, 502, 503, 504):
                if attempt >= self.max_retries:
                    raise S2Error("HTTP %s，重试 %s 次后放弃：%s"
                                  % (resp.status_code, attempt, resp.text[:300]))
                wait = self._retry_after(resp) or min(
                    self.backoff_base ** (attempt + 2), self.backoff_cap)
                self._log("  [HTTP %s] %ss 后重试（%s/%s）"
                          % (resp.status_code, wait, attempt + 1, self.max_retries))
                time.sleep(wait)
                attempt += 1
                continue

            if resp.status_code in (401, 403):
                raise S2AuthError(
                    "HTTP %s：key 缺失、无效或无权限。\n"
                    "检查 S2_API_KEY 是否写入 .env 或环境变量。接口返回：%s"
                    % (resp.status_code, resp.text[:200])
                )
            if resp.status_code == 400:
                raise S2Error(
                    "HTTP 400：参数不合法（常见原因：query 过长、sort 值错误、"
                    "fields 名称拼错）。接口返回：%s" % resp.text[:300]
                )
            raise S2Error("HTTP %s：%s" % (resp.status_code, resp.text[:500]))

    def _sleep(self, attempt):
        wait = min(self.backoff_base ** (attempt + 1), self.backoff_cap)
        self._log("  [network] %ss 后重试（%s/%s）" % (wait, attempt + 1, self.max_retries))
        time.sleep(wait)

    # -- 检索 -------------------------------------------------------------

    def bulk_search(self, query, fields=None, sort="citationCount:desc",
                    max_results=1000, start_token=None, on_page=None, **filters):
        """bulk search，token 续取。生成器，逐条 yield。

        on_page(papers, next_token, total, fetched_so_far) 在每页抓取后调用，
        便于调用方落盘 token 做断点续传。
        """
        params = {
            "query": query,
            "fields": fields or FIELD_PRESETS["standard"],
            "sort": sort,
        }
        params.update(clean_filters(filters))

        token = start_token
        fetched = 0
        while True:
            if token:
                params["token"] = token
            else:
                params.pop("token", None)

            payload = self._request("GET", GRAPH + "/paper/search/bulk", params=params)
            data = payload.get("data") or []
            token = payload.get("token")
            total = payload.get("total")
            fetched += len(data)

            if on_page:
                on_page(data, token, total, fetched)

            for paper in data:
                yield paper

            if not token or fetched >= max_results:
                break

    def search_relevance(self, query, fields=None, max_results=100, offset=0, **filters):
        """relevance search。单页最多 100，超出需 offset 翻页，成本高于 bulk。"""
        remaining = max_results
        out = []
        while remaining > 0:
            params = {
                "query": query,
                "fields": fields or FIELD_PRESETS["standard"],
                "limit": min(100, remaining),
                "offset": offset,
            }
            params.update(clean_filters(filters))
            payload = self._request("GET", GRAPH + "/paper/search", params=params)
            data = payload.get("data") or []
            out.extend(data)
            if len(data) < params["limit"]:
                break
            offset += len(data)
            remaining -= len(data)
        return out[:max_results]

    def snippet_search(self, query, fields=None, limit=10, **filters):
        """片段检索。返回 [{snippet:{text,...}, paper:{...}}]。"""
        params = {
            "query": query,
            "fields": fields or (
                "snippet.text,snippet.snippetKind,snippet.section,"
                "paper.paperId,paper.title,paper.year,paper.venue,paper.externalIds"
            ),
            "limit": min(limit, 100),
        }
        params.update(clean_filters(filters))
        return self._request("GET", GRAPH + "/snippet/search", params=params).get("data", [])[:limit]

    def match_paper(self, title, fields=None, limit=5):
        """按标题精确匹配（/paper/search/match）。返回候选列表。

        用途：已知标题时定位唯一 paperId，比关键词检索更准。
        """
        params = {
            "query": title,
            "fields": fields or "title,year,venue,authors,externalIds,citationCount",
        }
        if limit:
            params["limit"] = min(100, limit)
        payload = self._request("GET", GRAPH + "/paper/search/match", params=params)
        return (payload.get("data") or [])[:limit]

    # -- 详情与批量水合 ----------------------------------------------------

    def get_paper(self, paper_id, fields=None):
        return self._request(
            "GET", GRAPH + "/paper/" + paper_id,
            params={"fields": fields or FIELD_PRESETS["detail"]},
            allow_404=True,
        )

    def batch_papers(self, ids, fields=None):
        """POST /paper/batch，一次最多 500 个 ID。

        返回列表与 ids 尽量对齐；无法解析的 ID 在响应里是 null。
        调用方可用 align_batch() 还原对应关系。
        """
        ids = [i for i in ids if i]
        out = []
        for chunk in chunks(ids, 500):
            payload = self._request(
                "POST", GRAPH + "/paper/batch",
                params={"fields": fields or FIELD_PRESETS["detail"]},
                json_body={"ids": chunk},
            )
            if isinstance(payload, list):
                out.extend(payload)
            else:
                out.extend([None] * len(chunk))
        return out

    @staticmethod
    def align_batch(ids, rows):
        """把 batch 返回（可能含 null）还原为 [(id, paper|None), ...]。"""
        pairs = []
        for idx, pid in enumerate(ids):
            paper = rows[idx] if idx < len(rows) else None
            pairs.append((pid, paper))
        return pairs

    # -- 引文网络 ---------------------------------------------------------

    def citations(self, paper_id, fields=None, max_results=1000, offset=0):
        """被引：谁引用了这篇。返回 wrapper 列表，正文在 citingPaper。"""
        return self._paginate_edges(
            GRAPH + "/paper/" + paper_id + "/citations",
            fields or "title,year,venue,authors,externalIds,citationCount",
            max_results, offset,
        )

    def references(self, paper_id, fields=None, max_results=1000, offset=0):
        """参考文献：这篇引用了谁。正文在 citedPaper。"""
        return self._paginate_edges(
            GRAPH + "/paper/" + paper_id + "/references",
            fields or "title,year,venue,authors,externalIds,citationCount",
            max_results, offset,
        )

    def _paginate_edges(self, url, fields, max_results, offset):
        out = []
        while len(out) < max_results:
            limit = min(1000, max_results - len(out))
            payload = self._request("GET", url, params={
                "fields": fields, "limit": limit, "offset": offset,
            })
            data = payload.get("data") or []
            out.extend(data)
            if not payload.get("next") or not data:
                break
            offset = payload.get("next")
        return out[:max_results]

    # -- 推荐 -------------------------------------------------------------

    def recommendations_for_paper(self, paper_id, fields=None, limit=50, pool="recent"):
        payload = self._request("GET", RECS + "/papers/forpaper/" + paper_id, params={
            "fields": fields or FIELD_PRESETS["standard"],
            "limit": min(limit, 500),
            "from": pool,
        })
        return payload.get("recommendedPapers", [])[:limit]

    def recommend(self, positive_ids, negative_ids=None, fields=None, limit=50):
        body = {"positivePaperIds": positive_ids}
        if negative_ids:
            body["negativePaperIds"] = negative_ids
        payload = self._request(
            "POST", RECS + "/papers",
            params={"fields": fields or FIELD_PRESETS["standard"],
                    "limit": min(limit, 500)},
            json_body=body,
        )
        return payload.get("recommendedPapers", [])[:limit]

    # -- 作者 -------------------------------------------------------------

    def search_authors(self, query, fields=None, limit=20):
        payload = self._request("GET", GRAPH + "/author/search", params={
            "query": query,
            "fields": fields or "name,affiliations,paperCount,citationCount,hIndex,externalIds",
            "limit": min(limit, 1000),
        })
        return payload.get("data", [])[:limit]

    def get_author_papers(self, author_id, fields=None, max_results=100, offset=0):
        out = []
        while len(out) < max_results:
            limit = min(1000, max_results - len(out))
            payload = self._request("GET", GRAPH + "/author/" + author_id + "/papers", params={
                "fields": fields or FIELD_PRESETS["standard"],
                "limit": limit,
                "offset": offset,
            })
            data = payload.get("data") or []
            out.extend(data)
            if len(data) < limit:
                break
            offset += len(data)
        return out[:max_results]

    # -- Datasets ---------------------------------------------------------

    def dataset_releases(self):
        return self._request("GET", DATASETS + "/release/")

    def dataset_release(self, release_id="latest"):
        return self._request("GET", DATASETS + "/release/" + str(release_id))

    def dataset_download_links(self, release_id, dataset_name):
        """返回预签名下载链接。此接口需要 API key。"""
        return self._request(
            "GET", DATASETS + "/release/%s/dataset/%s" % (release_id, dataset_name)
        )

    def dataset_diffs(self, start_release, end_release, dataset_name):
        return self._request(
            "GET", DATASETS + "/diffs/%s/to/%s/%s"
            % (start_release, end_release, dataset_name)
        )


def clean_filters(filters):
    """把 Python 风格参数名映射为 API 参数名，去掉空值。"""
    mapping = {
        "year": "year",
        "publication_date": "publicationDateOrYear",
        "venue": "venue",
        "fields_of_study": "fieldsOfStudy",
        "min_citations": "minCitationCount",
        "pub_types": "publicationTypes",
    }
    out = {}
    for key, val in (filters or {}).items():
        if val is None or val is False or val == "" or val == []:
            continue
        api_key = mapping.get(key, key)
        if isinstance(val, (list, tuple)):
            val = ",".join(str(x) for x in val)
        elif api_key == "minCitationCount":
            val = str(val)
        out[api_key] = val
    if filters.get("open_access") or filters.get("open_access_pdf"):
        out["openAccessPdf"] = ""
    return out


# --------------------------------------------------------------------------
# 导出
# --------------------------------------------------------------------------

def paper_authors(paper):
    names = []
    for a in (paper.get("authors") or []):
        if isinstance(a, dict) and a.get("name"):
            names.append(a["name"])
        elif isinstance(a, str):
            names.append(a)
    return names


def to_csv(rows, path):
    import csv

    cols = [
        ("paperId", lambda p: p.get("paperId") or ""),
        ("title", lambda p: p.get("title") or ""),
        ("year", lambda p: p.get("year") or ""),
        ("venue", lambda p: p.get("venue") or ""),
        ("authors", lambda p: "; ".join(paper_authors(p))),
        ("doi", paper_doi),
        ("url", lambda p: p.get("url") or ""),
        ("citationCount", lambda p: p.get("citationCount") or 0),
        ("publicationDate", lambda p: p.get("publicationDate") or ""),
        ("publicationTypes", lambda p: ",".join(p.get("publicationTypes") or [])),
        ("openAccessPdf", lambda p: ((p.get("openAccessPdf") or {}).get("url") or "")),
        ("abstract", lambda p: (p.get("abstract") or "").replace("\n", " ")),
        ("query", lambda p: ((p.get("_meta") or {}).get("query") or "")),
    ]
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([c[0] for c in cols])
        for row in rows:
            writer.writerow([fn(row) for _, fn in cols])
    return path


def to_markdown(rows, limit=50, details=10):
    lines = []
    lines.append("| # | Title | Year | Venue | Cites | DOI |")
    lines.append("|---|-------|------|-------|-------|-----|")
    for i, p in enumerate(rows[:limit], 1):
        title = (p.get("title") or "").replace("|", "\\|")
        lines.append("| %d | %s | %s | %s | %s | %s |" % (
            i, title[:100], p.get("year") or "",
            (p.get("venue") or "").replace("|", "\\|")[:40],
            p.get("citationCount") or 0, paper_doi(p),
        ))

    if details:
        lines.append("")
        lines.append("## Top %d 详情" % min(details, len(rows)))
        for i, p in enumerate(rows[:details], 1):
            authors = paper_authors(p)
            byline = ", ".join(authors[:5]) + (" et al." if len(authors) > 5 else "")
            lines.append("")
            lines.append("### %d. %s (%s)" % (i, p.get("title") or "Untitled", p.get("year") or "?"))
            if byline:
                lines.append("**Authors:** " + byline)
            meta = ["Cites: %s" % (p.get("citationCount") or 0)]
            if paper_doi(p):
                meta.append("DOI: " + paper_doi(p))
            lines.append("**%s**" % " | ".join(meta))
            abstract = (p.get("abstract") or "").strip()
            if abstract:
                lines.append("")
                lines.append(abstract[:500] + ("..." if len(abstract) > 500 else ""))
    return "\n".join(lines) + "\n"


def export_bibtex(client, rows, path):
    """优先用已有 citationStyles，缺失的走 batch 补。"""
    ids = [p.get("paperId") for p in rows if p.get("paperId")]
    styles = {}
    for p in rows:
        bib = ((p.get("citationStyles") or {}).get("bibtex") or "").strip()
        if p.get("paperId") and bib:
            styles[p["paperId"]] = bib

    missing = [pid for pid in ids if pid not in styles]
    if missing and client is not None:
        for batch in chunks(missing, 500):
            data = client.batch_papers(batch, fields=FIELD_PRESETS["bibtex"])
            for pid, paper in client.align_batch(batch, data):
                if paper:
                    bib = ((paper.get("citationStyles") or {}).get("bibtex") or "").strip()
                    if bib:
                        styles[pid] = bib

    order = [p.get("paperId") for p in rows if p.get("paperId") in styles]
    seen, entries = set(), []
    for pid in order:
        if pid in seen:
            continue
        seen.add(pid)
        entries.append(styles[pid])

    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n\n".join(entries) + ("\n" if entries else ""))
    return path, len(entries)


def describe_client(client):
    status = key_status() if client is None else {
        "present": bool(client.api_key),
        "source": "client",
        "masked": _mask(client.api_key) if client.api_key else None,
    }
    return status
