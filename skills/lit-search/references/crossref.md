# Crossref 通道（无需 API key）

Crossref 是 DOI 注册机构元数据的权威来源，公开 REST API，**不需要任何 key**。

- 端点：`https://api.crossref.org/works`
- 礼貌池：带 `mailto` 参数（或 `Mailto` 头）响应更快更稳
- 本 skill 的实现：`scripts/crossref.py`，CLI 入口 `python scripts/litsearch.py crossref ...`

## 何时用它

| 场景 | 说明 |
|------|------|
| **S2 被限流停下后的兜底** | 429 即停策略下，还想再查几条题录用 Crossref |
| DOI 解析 | 拿到 DOI → 完整题录、期刊全名、作者、被引数、参考文献列表 |
| 核对元数据 | 期刊全名（Crossref 的 `container-title` 是全称）、出版商、ISSN |
| 参考文献列表 | `work["reference"]` 里有被引文献的 DOI 线索 |
| 小批量关键词检索 | 可以，但很弱（见下） |

## 不适合

- 语义检索、主题摸底 → 用 Asta
- 大批量穷举 → 用 S2 bulk
- 全文 → Crossref 只给题录

## Crossref 与"文献关系"：能知道什么，不能知道什么

常见误解：Crossref 官方定位是"DOI 注册机构 + 元数据"，其前身 CiteSeer 的"文献图谱"商业业务早已停止；**当前的 Crossref REST API 没有可查询的引文图谱**。它能提供的是"每篇文献自己申报的关系"：

| 关系 | Crossref 字段 | 方向 | 限制 |
|------|--------------|------|------|
| 参考文献 | `reference[]`（含 `DOI`、`unstructured`、`key`） | 这篇引用了谁（后向） | 由出版商申报；老文献常只有 `unstructured` 文本；部分期刊不申报 |
| 被引计数 | `is-referenced-by-count` | 被引数 | **只有计数，没有列表**，无法反查"谁引了它" |
| 版本关系 | `relation`（`is-preprint-of` / `is-version-of` / `has-preprint` / `is-identical-to`） | 预印本↔正式版 | 依赖出版商申报，覆盖不全 |
| 更新关系 | `update-to`（撤稿、更正、补充） | 正式版→更新 | 同上 |
| 全文/TDM 链接 | `link[]`（`content-type: application/pdf`、`intended-application: text-mining`） | 全文入口 | 只给出版商允许的链接，不保证公开 |

可用于筛选的过滤器：`has-references:true`、`has-update:true`、`has-relation:true`、`reference-visibility:open`。

**结论**：要查"谁引用了 X""X 与 Y 是否互相引用""哪些文献与 X 主题相近"，Crossref 不是对应工具。分工如下：

| 需求 | 用什么（本 skill 已内置） |
|------|------------------------|
| 谁引用了 X（前向引用） | `opencitations --direction citations`；OpenAlex `openalex --citations`；S2/Asta |
| X 引用了谁（后向引用） | `opencitations --direction references`；OpenAlex `openalex --references`；Crossref `--references`（出版商申报口径） |
| 两篇是否互相引用 | 各自跑一次前/后向，交叉比对 DOI；OpenCitations 的 `oci` 编号直接标出方向 |
| 共同引用（co-citation）/ 相似文献 | OpenAlex `openalex --related`；S2 recommendations / Asta 语义检索（OpenCitations 的 `similar` 端点未开放） |
| 预印本与正式版的对应关系 | Crossref `relation`；OpenAlex `locations`；PubMed `pubmed`→`pmc`/`idconv` |

## 命令

```bash
# 模糊关键词检索（默认按相关性排序）
python scripts/litsearch.py crossref --query "advertising sales" --rows 20 --no-proxy

# 精确一些：限定标题 / 作者
python scripts/litsearch.py crossref --title "short video advertising" --author "Wang" --rows 10

# 按影响力排序
python scripts/litsearch.py crossref --query "advertising" --rows 20 \
    --sort is-referenced-by-count --order desc

# 时间与类型过滤
python scripts/litsearch.py crossref --query "advertising" \
    --filter "from-pub-date:2020-01-01,type:journal-article" --rows 30

# DOI 单条解析
python scripts/litsearch.py crossref --doi 10.1038/nature12373

# DOI + 它的参考文献列表
python scripts/litsearch.py crossref --doi 10.1038/nature12373 --references --out ref.jsonl

# 进入礼貌池（推荐长期使用）
python scripts/litsearch.py crossref --query "..." --mailto you@example.com
```

## 参数要点

| 参数 | 说明 |
|------|------|
| `--query` | 走 `query.bibliographic`（模糊匹配） |
| `--title` / `--author` | 走 `query.title` / `query.author`，比 `--query` 准 |
| `--rows` | 返回条数（上限 1000） |
| `--filter` | Crossref 过滤语法，如 `from-pub-date:2020-01-01`、`type:journal-article`、`has-abstract:true` |
| `--sort` | `relevance`（默认）、`published`、`is-referenced-by-count` |
| `--order` | `asc` / `desc` |
| `--select` | 限定返回字段，减少响应体 |
| `--mailto` | 进礼貌池 |

## 字段规范化（与 S2 合并去重）

`crossref.normalize()` 把 Crossref work 记录转成与 S2 相近的字段，便于直接合并：

| 统一字段 | Crossref 来源 |
|---------|---------------|
| `paperId` | `DOI:<doi>` |
| `externalIds.DOI` | `DOI`（小写） |
| `title` | `title[0]` |
| `year` | `published-print` / `published-online` / `issued` |
| `venue` | `container-title[0]`（期刊**全名**） |
| `authors` | `author[].given + family` |
| `citationCount` | `is-referenced-by-count` |
| `url` | `URL` 或 `https://doi.org/<doi>` |
| `_meta.source` | `crossref` |

因为去重键是 **DOI → paperId → 标题+年份**，Crossref 结果可以直接和 S2 结果一起丢进 `dedup` 合并。

## 实测（2026-11-13）

- 免 key 直连可用（同样需要 `--no-proxy` 绕开 Windows 注册表代理）
- `query="advertising sales"` 命中 `total-results` 约 24 万条，默认相关性排序返回的是书籍章节（`Building sales: advertising and...`）——**关键词质量明显低于 S2 bulk**，所以 Crossref 只作为兜底与元数据核对通道
- 429 同样是"立即停止"策略（`CrossrefRateLimitError`）