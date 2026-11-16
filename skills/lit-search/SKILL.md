---
name: lit-search
description: "多通道学术文献检索与证据核验，统一入口：Semantic Scholar REST（带 API key，适合大批量布尔检索、批量水合元数据、引文滚雪球、Datasets 下载）+ Ai2 Asta MCP（语义检索、标题匹配、引用网络、片段级证据）+ Crossref（免 key，DOI 题录与兜底）+ PubMed/PMC（生物医学题录、MeSH、免费全文）+ OpenAlex（跨学科、聚合统计、OA 状态、引文边、相关文献）+ arXiv/bioRxiv/medRxiv（预印本）+ Unpaywall/CORE（OA 全文，需批准下载）+ NBER 与 SSRN（经济学工作论文）+ OpenCitations（免 key 引用图谱：谁引用了它、它引用了谁）。当用户要求检索/调研文献、做系统综述式检索、批量拉取题录与摘要、追踪引用与互引关系、去重导出 BibTeX/RIS/CSV/Markdown，或提到 Semantic Scholar、S2、Asta、bulk search、PubMed、MeSH、PMC、arXiv、OpenAlex、Unpaywall、NBER、SSRN、文献综述、引文网络时使用。"
compatibility: opencode
---

# 多通道文献检索

一个入口，十条通道。本 skill 负责**选路、检索式、批量落盘、去重筛选、导出规范检索结果**。

| 通道 | 什么时候用 | key |
|------|-----------|-----|
| **S2** — `scripts/litsearch.py search` | 大批量穷举、批量水合元数据、引文网络、全库下载 | 可选（有 key 更稳） |
| **Asta** — MCP 工具，或 `scripts/asta_client.py` | 语义探索、片段级证据、按日期过滤的被引 | 需要 |
| **Crossref** — `litsearch.py crossref` | 查 DOI 题录、期刊全名与被引数核对、按 ISSN/前缀检索 | **不需要** |
| **PubMed / PMC** — `litsearch.py pubmed` / `pmc` | 生物医学主题、MeSH 检索、免费全文正文 | 可选 |
| **OpenAlex** — `litsearch.py openalex` | 跨学科覆盖、期刊/主题聚合、OA 状态、引文边 | 可选 |
| **预印本** — `litsearch.py arxiv` / `biorxiv` | arXiv、bioRxiv/medRxiv、预印本↔正式版 | **不需要** |
| **OA / 全文** — `litsearch.py unpaywall` / `core` | OA 状态、PDF 与全文获取（**下载需批准**） | 邮箱 / CORE key |
| **NBER** — `litsearch.py nber` | 经济学工作论文主源（官方 API，免 key） | **不需要** |
| **SSRN** — `litsearch.py ssrn` | 社科/经管工作论文（经 OpenAlex + Crossref 索引） | **不需要** |
| **OpenCitations** — `litsearch.py opencitations` | 引用关系：谁引用了它、它引用了谁、共同被引相似（免 key） | **不需要** |

一句话规则：**要"找全"用 S2；要"找像"或"找证据"用 Asta；S2 停手后补几条用 Crossref；生物医学走 PubMed；跨学科与统计走 OpenAlex；要读正文走 PMC/OA；经济学工作论文走 NBER + SSRN。**


## 何时使用

- 系统检索 / 综述：把某个题目的文献尽量找全
- 已有几十到几千篇题录，要补摘要、DOI、引用数
- 从一个种子文献做前向/后向引文扩展
- 结果要整理成 CSV / Markdown 表 / BibTeX / RIS 交给 Zotero 或写作
- 核对某篇论文里是否真的说了某句话 → 片段检索
- 摘要不够，需要读全文判断相关性

**不适用**：正文引用编号与重排、引文格式校验、Word/LaTeX 排版 → 交给 agent、其它 skill 或脚本。

## 快速开始

命令都在 **skill 目录内**用相对路径执行：

```bash
cd <skill_dir>

python scripts/litsearch.py check                      # 自检（不发请求）
python scripts/litsearch.py check --live --no-proxy    # 验证 key（消耗 1 次额度）

# 批量检索（推荐先 100 条验证召回，再扩量）
python scripts/litsearch.py search --queries-file queries.json \
    --max-results 2000 --no-proxy --out out/ads/

python scripts/litsearch.py hydrate --in out/ads/papers.jsonl --out out/ads/full.jsonl --no-proxy
python scripts/litsearch.py dedup   --in out/ads/full.jsonl --year-min 2015 --out out/ads/screened.csv
python scripts/litsearch.py export  --in out/ads/full.jsonl --format bib --out out/ads/refs.bib --no-proxy

# 小批量追问（免 key）
python scripts/litsearch.py crossref --doi 10.1038/nature12373
python scripts/litsearch.py pubmed  --query '"advertising"[Title/Abstract]' --limit 20 --no-proxy
python scripts/litsearch.py openalex --query "advertising" --limit 20 --no-proxy
python scripts/litsearch.py opencitations --doi 10.1038/nature12373 --direction citations --limit 20 --no-proxy
python scripts/litsearch.py nber    --query "advertising firm performance" --limit 20 --no-proxy
python scripts/litsearch.py ssrn    --query "advertising firm performance" --limit 20 --no-proxy
```

`queries.json`：字符串数组，或带覆盖参数的对象数组。

```json
[
  "advertising +sales +video",
  {"name": "loudness", "query": "\"voice loudness\" +advertising", "year": "2010-"}
]
```

## 选路

| 要做的事 | 用哪个 |
|----------|--------|
| 一个题目尽可能找全 | **S2 bulk**（布尔/短语/通配，token 翻页） |
| 只有模糊描述，先看看有什么 | **Asta 语义检索**（limit 5–20） |
| 已知标题找准确条目 | **Asta 标题匹配** 或 S2 `match` |
| 已知 DOI/arXiv/PMID | **Asta `get_paper`** 或 S2 单篇 |
| 几十上百个 ID 的详情 | **S2 batch**（≤500/次） |
| 谁引用了 X / X 引用了谁 | **S2 citations/references**（两向可翻页）；只要前向+日期过滤用 Asta |
| 某句话在哪些论文里出现 | **Asta 片段检索** / S2 `snippets` |
| 要 DOI、期刊全名、被引数 | **Crossref** |
| 生物医学主题 / MeSH 检索 | **PubMed** |
| 要读免费正文 | **PMC**（`pmc --sections`） |
| 跨学科覆盖、期刊/主题统计、OA 状态 | **OpenAlex** |
| 预印本、预印本↔正式版 | **arXiv / bioRxiv / medRxiv** |
| 要 PDF / 全文（需批准下载） | **Unpaywall / CORE** |
| 谁引用了这篇 / 它引用了谁 | **OpenCitations**（免 key，双向）；OpenAlex `--citations/--references` |
| 主题相近但未必互相引用 | **OpenAlex `--related`**；Asta 语义检索；S2 recommendations |
| 经济学工作论文 | **NBER**（官方 API）；SSRN 用 `ssrn`（OpenAlex/Crossref 索引） |
| 经济管理期刊正式论文 | **econ**（Crossref+ISSN 稳定；SSRN/IDEAS 站点直抓不可用） |
| 全库级离线分析 | **S2 Datasets** |
| 找作者及其论文 | **Asta** 作者工具 |

细节对比（匹配机制差异、各库端点与限制、外部同类 skill 对照）见 `references/channels.md`。

## 凭据

| 变量 | 用途 | 需要 |
|---|---|---|
| `S2_API_KEY` | S2 批量检索 | 可选 |
| `ASTA_API_KEY` | Asta MCP / 脚本 | 必需（用 Asta 时） |
| `OPENALEX_API_KEY` | OpenAlex 配额 | 可选（建议） |
| `NCBI_API_KEY` | PubMed 10 req/s | 可选 |
| `NCBI_EMAIL` | NCBI 礼貌池 | 建议 |
| `UNPAYWALL_EMAIL` | Unpaywall | 必需（用 Unpaywall 时） |
| `CORE_API_KEY*` | CORE 全文 | 必需（可写多个：`CORE_API_KEY1`、`CORE_API_KEY2`，轮流使用分摊配额） |

解析顺序：环境变量 → `<skill_dir>/.env` → `~/.config/lit-search/.env` → 当前目录及各级上级（便利项）。推荐写在 skill 目录，随 skill 一起搬走。

## 五条硬性约束

1. **429 即停**：默认遇到 429 立刻停止，不重试、不发后续请求；重跑同命令自动续传。确实要重试才加 `--retry-429`。
2. **代理**：S2/Crossref/NCBI/OpenAlex 直连加 `--no-proxy`（Windows 注册表代理会报 `ProxyError`）；**传了 `--proxy` 即自动优先于注册表代理**（例如 `--proxy socks5://127.0.0.1:10809`）；Asta 必须先配代理规则 + TUN 模式，否则一律 403；arXiv 直连易 429，走代理可解。
3. **下载需批准**：Unpaywall/CORE 的 PDF 下载永不隐式执行——先出下载计划，汇报给用户并获批准后，才加 `--confirm-download`。
4. **不编造**：PMID、DOI、作者、刊名、卷期页一律来自实时响应；缺失只告警、不补全。
5. **多 key 只用于分摊配额**：CORE 的多个 key 轮流使用；401/403 自动换下一个 key，但**429 仍立即停止**，不靠换 key 绕过限流。

各条的原因与排查步骤见 `references/s2-rest.md`、`references/asta-mcp.md`、`references/oa-fulltext.md`。

## 批量检索五步

1. 写 `queries.json`，先 `--max-results 100` 验证召回，确认没跑偏
2. `search` 落盘 → `papers.jsonl`（原始层）/ `state.json`（断点续传）/ `manifest.json`（本次参数）
3. `hydrate` 补摘要与 tldr（可选）
4. `dedup` 去重（DOI → paperId → 标题+年份）+ 规则筛选
5. `export` 成 md / csv / bib / ris / apa / gbt

引文扩展用 `expand`（先 `--max-per-seed 20` 试跑）。深度检索的两轮协议、饱和判据、证据等级、筛题理由、复现清单见 `references/workflows.md`。

## 交付给用户时

- 说明用了哪条通道与关键参数
- 给出各 query 命中数、去重前后条数
- 区分「检索到的」与「筛过后认为相关的」，不要把召回量说成相关文献量
- 结果为空时先放宽检索式或去掉年份限制，不要直接断言"没有研究"
- 导出格式（bib/ris/apa/gbt）只是薄导出，格式的严格排版由下游负责

## 相关文件

- `references/channels.md` — 各通道详细对比、匹配机制差异、组合配方
- `references/s2-rest.md` — S2 端点、参数、字段预设、分页、限流实测与布尔语法实测
- `references/asta-mcp.md` — Asta 工具路由、参数例外、路由前置条件与排障
- `references/crossref.md` — Crossref 通道用法与字段规范化
- `references/pubmed-pmc.md` — PubMed/PMC 端点、MeSH 语法、ID 互转、BioC
- `references/openalex.md` — OpenAlex 过滤表达式、cursor 深翻页、字段映射、引文边
- `references/preprints.md` — arXiv 语法、分类校验、bioRxiv/medRxiv 接口、429 实测
- `references/oa-fulltext.md` — Unpaywall/CORE 用法与下载批准流程
- `references/nber.md` — NBER 官方 API、参数、字段限制与直链构造
- `references/opencitations.md` — 引用图谱通道：前向/后向引用、共被引相似、交叉标识
- `references/econ-sources.md` — 经济学各渠道状态与站点直抓不可用的排查记录
- `references/journal-identifiers.md` — 常用刊物的 OpenAlex source id 与 Crossref ISSN
- `references/formats.md` — bib/ris/apa/gbt 导出规则与边界
- `references/workflows.md` — 检索式设计、深度检索协议、影响力度量、筛选矩阵、抽样质检、复现清单
- `scripts/` — `s2api.py`（S2 客户端）、`litsearch.py`（CLI）、`crossref.py`、`ncbi.py`、`openalex.py`、`preprints.py`、`oa_fulltext.py`、`nber.py`、`econ_sources.py`、`opencitations.py`、`formats.py`、`asta_client.py`（Asta 脚本侧备用通道）、`selftest.py`（离线自检，不联网，`python scripts/selftest.py`）
