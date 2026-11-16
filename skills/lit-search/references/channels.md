# 通道对比与选型细节

SKILL.md 只给"什么时候用哪条"；这里放具体的差别、实测数字与同类工具对照。

## 通道能力总表

| | S2 | Asta | Crossref | PubMed/PMC | OpenAlex | 预印本 | OA/全文 | NBER | SSRN | OpenCitations |
|---|---|---|---|---|---|---|---|---|---|---|
| 入口 | `litsearch.py search` | MCP / `asta_client.py` | `litsearch.py crossref` | `litsearch.py pubmed/pmc` | `litsearch.py openalex` | `litsearch.py arxiv/biorxiv` | `litsearch.py unpaywall/core` | `litsearch.py nber` | `litsearch.py ssrn` | `litsearch.py opencitations` |
| key | 可选 | 需要 | 不需要 | 可选 `NCBI_API_KEY` | 可选 `OPENALEX_API_KEY` | 不需要 | 邮箱 / CORE key | 不需要 | 不需要 | **不需要** |
| 匹配方式 | 关键词/布尔（标题+摘要） | 语义 | 模糊 bibliographic | MeSH + 字段标签 | 全文索引 + 过滤 | arXiv 语法 / 日期浏览 | 按 DOI | 关键词 + 项目过滤 | 索引检索（OpenAlex/Crossref） | 引用图谱（按 DOI） |
| 强项 | 大批量穷举、布尔精确 | 语义探索、片段证据 | DOI 题录、期刊全名 | 生物医学题录、MeSH、PMC 正文 | 跨学科覆盖、聚合统计、OA | 预印本 | PDF/全文获取 | 经济学工作论文主源 | 社科/经管工作论文 | **前向/后向引用、共被引相似** |
| 摘要覆盖 | 约 25%–30% | 同 S2 | 需 `has-abstract` 过滤 | 高（PubMed 多数有结构化摘要） | 约 20%–30% | 高 | 不提供 | 仅前约 300 字符 | OpenAlex 部分有 | 无（只有标识） |
| 引文网络 | 双向可翻页 | 仅前向，可按日期 | 仅参考文献列表 + 被引计数 | elink 相关/被引 | `cites:`/`cited_by:` 过滤 + `related_works` | 无 | 无 | 无 | 无 | **双向引用**（`similar` 未开放） |
| 网络 | 直连 + `--no-proxy` | 必须代理 + TUN | 直连 + `--no-proxy` | 直连可用 | 直连可用 | arXiv 常 429，需代理 | 直连；CORE 需 key | 直连可用 | 走索引，直连可用 | 直连可用 |

细节文件：`references/s2-rest.md`、`references/asta-mcp.md`、`references/crossref.md`、`references/pubmed-pmc.md`、`references/openalex.md`、`references/preprints.md`、`references/oa-fulltext.md`、`references/nber.md`、`references/econ-sources.md`、`references/journal-identifiers.md`、`references/opencitations.md`。


## S2 与 Asta 的匹配机制差异（会影响召回）

- **S2 bulk = 关键词/布尔匹配**（标题 + 摘要）。检索式里的词必须字面出现，`+`/`-`/引号都生效。
- **Asta = 语义匹配**。不要求字面命中。

实测对照（2026-11-13）：同一检索式 `advertising delivery intensity sales`，Asta 返回的是"广告强度 + 销售增长"类的税务/管理论文（主题相近但研究问题不同），S2 bulk 返回的是标题摘要里真正出现这些词的论文。

结论：**语义匹配用来探索与补漏，关键词匹配用来穷举与核查**。综述式检索不能只靠 Asta，也不能用一边的结果去"验证"另一边的检索式。

## MCP 工具 vs `asta_client.py`

不是两套服务，是同一服务的两条传输路径，**额度消耗相同**（不更省）。详细对照见 `references/asta-mcp.md` 的"工具 vs 脚本侧通道"一节。

选择规则：agent 在会话里做事 → MCP 工具；要成批落盘、接入自动化，或 MCP 路由不通 → 脚本。

## 小批量/普通检索怎么走

| 场景 | 用法 | key |
|------|------|-----|
| 查 1–3 篇、看主题 | Asta 语义检索（limit 5–10） | 需要 Asta key |
| DOI → 完整题录/期刊/被引数/参考文献 | `crossref --doi ...` | **不需要** |
| 关键词小批量题录 | `crossref --query ... --rows 20` | **不需要** |
| S2 少量查询 | `--anonymous` 或带 key | 可选 |
| 生物医学主题检索 | `pubmed --query '... [MeSH Terms]'` | 可选 |
| 跨学科题录 + OA 状态 | `openalex --query ...` | 可选 |
| 谁引用了这篇 / 它引用了谁 | `opencitations --direction citations/references` | **不需要** |
| 主题相近但未必互相引用 | `openalex --related`；Asta 语义检索；S2 recommendations |
 **不需要** |
| 要读正文 | `pmc --sections`（免费）或 Unpaywall/CORE（需批准下载） | 视渠道 |

S2 **没有 key 也能用**（匿名共享池），只是限流概率高，适合冒烟测试与零星查询。

## 渠道组合的常见配方

| 目标 | 配方 |
|---|---|
| 综述式穷举 | S2 bulk（布尔）→ Crossref 核对 DOI → OpenAlex 补 OA/跨学科 |
| 证据核验（某句话） | Asta 片段检索 或 S2 snippets → PMC/全文核对原句 |
| 生物医学主题 | PubMed（MeSH）→ PMC 读正文 → OpenAlex 补被引 |
| 经济管理主题 | NBER API + Crossref(ISSN) + SSRN(OpenAlex/Crossref 索引)；**SSRN/IDEAS 站点直抓不可用** |
| 已知种子做扩展 | S2 citations/references → Crossref 补全元数据 → Unpaywall 取全文 |
| 引用关系与共同引用 | OpenCitations（双向引用）→ OpenAlex（`--citations/--references/--related`）→ Crossref 核对出版商申报口径 |

## 外部同类 skill 与工具（本机 / 其他机器常见）

本 skill 现已内置上述常用库，**常规文献检索不再需要看其它 skill**。下列工具仅在超出本 skill 范围（读全文、PRISMA 筛选、问答、写作）时才需要：

| 工具 / skill | 何时仍需要它 | 说明 |
|---|---|---|
| `citation-management` | 引文格式校验、BibTeX 规范化、Google Scholar 抓取（本 skill 明确不做） | BibTeX 校验 + GS 抓取 |
| `academic-literature-search` | GB/T 7714 的严格排版校验（本 skill 只做薄导出） | 中文引用格式 |
| `research-lookup` | 实时网页/学术检索（Parallel / Perplexity，非结构化索引） | 需各自 key |
| `paper-analysis` | 单篇论文的深度阅读与批判（非检索） | 不需要 |
| ASReview / prismAId | 数千条摘要的 PRISMA 主动学习筛选 | 筛选环节 |
| MinerU / docling / marker | PDF → Markdown（喂给 LLM 读全文） | 全文解析 |
| PaperQA2 | 对一批 PDF 做带引证的问答 | 全文问答 |
| `paper-search-mcp` / `arxiv-mcp-server` | 想在 Claude/Cursor 里以 MCP 方式查文献 | MCP 接入 |
| `scholarly` / `pyalex` | 需要 Python 库直连 Google Scholar / OpenAlex | 本 skill 已内置 OpenAlex，GS 不建议 |

> 本 skill 定位是"大批量、可复现、带落盘与去重的多通道管线"；格式排版、引文校验、论文精读不在其范围内。

