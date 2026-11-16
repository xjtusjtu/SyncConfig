# 批量检索工作流与复现清单

目标：从「一个研究问题」走到「一份可复查的文献集合」，每一步都能说清来源与排除理由。

## 1. 把问题拆成检索块

不要直接写一句自然语言丢给 API。先拆成 2–4 个概念块，每块列同义词：

| 块 | 示例（广告效果研究） |
|----|---------------------|
| 对象 | advertisement / advertising / commercial / ad |
| 交付特征 | delivery / voice / speech rate / loudness / verbal / acoustic |
| 结果 | sales / purchase / conversion / performance |
| 边界（可选） | short-form / video / TikTok / YouTube |

组合规则：

- 块内用 `(a | b | c)`
- 块间用 `+`
- 多词术语用 `"exact phrase"`
- 明确不想要的用 `-term`
- 每条检索式**只覆盖一个子问题**，便于归因

示例：

```
("advertising" | "advertisement" | "commercial") + ("voice" | "speech rate" | "loudness") + ("sales" | "purchase")
```

**两个实测提醒**

- 引号是严格短语，用之前先确认短语在库里真实存在（先跑不带 `+` 的短语检索看 total）。`"voice loudness"` 有 194 条，但加 `+advertising` 后是 0。
- bulk 结果里约 25%–30% 带摘要，因此**不要**把"标题+摘要里没有某个词"直接当作"该论文没有涉及这个概念"。检索式层面用 `+`/`-` 约束，筛题层面再靠人工读摘要。

## 2. 先验证召回，再扩量

```bash
python litsearch.py search --query '<检索式>' --max-results 100 --no-proxy --out out/pilot/
python litsearch.py export --in out/pilot/papers.jsonl --format md --out out/pilot/preview.md
```

看前 20 条：

- 有 3–5 篇明显相关 → 检索式可用
- 全是无关领域 → 多半是某个词太泛（如 `performance`），加限定或换词
- 一篇都没有 → 拆掉 `+` 逐个试，确认是哪个块过窄

**不要在未验证的情况下直接跑 5000 条**：额度有限，且大概率白跑。

## 3. 记录检索过程

`search` 会自动生成：

- `papers.jsonl`：原始结果，每条带 `_meta.query` / `_meta.run_id` / `_meta.retrieved_at`
- `state.json`：每个 query 的 token 与累计条数（断点续传）
- `manifest.json`：本次的 fields、sort、上限、各 query 命中数、耗时

另外建议手工维护一份 `screening.csv`：

```
paperId,title,year,decision,reason,decided_at
```

`decision` 取值固定：`include` / `exclude` / `maybe`。理由写具体（"样本是实验室刺激，非真实广告"），不要只写"不相关"。

## 4. 处理流程（顺序不要乱）

```
原始 JSONL
  → 去重（DOI → paperId → 标题+年份）
  → 机械筛选（年份、语言可得性、是否有摘要、venue）
  → 题录筛选（读标题+摘要）
  → 全文筛选（能拿到全文的子集）
  → 最终集合
```

每一步都记录数量：

| 阶段 | 条数 |
|------|------|
| 原始召回 | |
| 去重后 | |
| 机械筛选后 | |
| 题录筛选后 | |
| 全文筛选后 | |

`dedup` 会把「原始 / 规则筛除 / 去重 / 保留」打印到 stderr，直接抄进表里。若用了 `--require-term/--exclude-term`，它还会额外报告"无摘要、无法核验"的条数——这个数字要一起写进表里。

## 5. 引文补充的边界

- 前向引用（谁引用了种子）适合找后续验证研究；后向引用（种子引用了谁）适合找理论基础。
- 每一轮扩展都会引入大量低相关文献，**必须重新过一遍题录筛选**，不能直接并入最终集合。
- 深度 >1 时调用量按 frontier 大小指数增长；除非有明确理由，`--depth 1` 足够。
- 记录每条的 `_meta.relation` 与 `_meta.seed`，写作时可说明"通过引文追踪补充"。

## 6. 抽样质检

导出后随机抽 20 条，逐条核对：

- 标题、年份、venue 是否与 Semantic Scholar 页面一致
- DOI 是否能解析（`https://doi.org/<DOI>`）
- `year` 与 `publicationDate` 是否冲突（预印本常见）
- 摘要是否被截断

发现系统性错误（例如整批 venue 为空）时，先停下查原因，不要继续加工。

## 7. 交接给 Zotero / 写作

- BibTeX：`export --format bib`；导入 Zotero 后核对条目类型（preprint vs journal article）
- CSV：给 Excel / pandas 做后续统计
- Markdown：直接贴进笔记，但**保留 paperId/DOI**，避免日后无法回溯

本库已有 `cookjohn-zotero-mcp`，可走 MCP 写入；批量导入前先备份 Zotero 库。

## 8. 复现清单

一次可复现的检索至少留下：

- [ ] `queries.json`（检索式 + 各 query 的过滤条件）
- [ ] `manifest.json`（fields、sort、上限、命中数、时间）
- [ ] `papers.jsonl`（原始层）
- [ ] `screening.csv`（纳入/排除理由）
- [ ] 使用的通道与版本（S2 REST / Asta MCP；脚本改动需记 commit）
- [ ] 检索日期（数据库内容随时间变化，`retrieved_at` 已在 `_meta` 里）

缺少其中任何一项，别人（包括三个月后的自己）都无法复现这份文献集合。

## 9. 深度检索模式（两轮 + 饱和判据）

用于正式的系统检索/综述，而不是"搜一轮看看"。

**每个主题至少跑两轮**，第二轮必须基于第一轮学到的词：

1. **第一轮（探索）**：用宽检索式 + 语义通道，收集候选词与核心文献；
2. **第二轮（精确）**：用第一轮得到的真实术语、同义变体、作者、期刊重写检索式，再跑一次；
3. **补充轮**：对关键种子做引文扩展（前向 + 后向），补第一轮没覆盖到的。

**多库原则**：正式综述至少覆盖 **3 个互补库**（不是同一个库换检索式）。本 skill 的互补组合示例：

| 主题类型 | 组合 |
|---|---|
| 跨学科通用 | S2 bulk（穷举）+ OpenAlex（覆盖与统计）+ Crossref（核对 DOI） |
| 生物医学 | PubMed（MeSH）+ PMC（正文）+ OpenAlex（被引与 OA） |
| 经济管理 | NBER + Crossref(ISSN) + SSRN(OpenAlex/Crossref 索引) |
| CS/AI | arXiv + S2 bulk + Datasets（全库离线） |

**饱和判据**（满足任一即停）：

- 连续两轮新增的相关文献 < 5%；
- 新增文献全部来自已见过的参考文献表（说明已收敛）；
- 检索式命中数在 3 轮内波动 < 10%。

**证据等级**（标注每条结论的依据强度）：

| 等级 | 依据 |
|---|---|
| A | 系统综述 / 元分析 / 随机对照实验 |
| B | 大样本实证研究 |
| C | 小样本实证、准实验 |
| D | 案例研究、相关性分析 |
| E | 理论推演、观点文章、工作论文（未经审稿） |

**置信度标注**：结论旁注明「高/中/低」，依据是证据等级 + 证据条数 + 是否互相一致。互相矛盾的高等级证据要显式写出矛盾，而不是只挑支持自己的一方。

**停止规则**：宁可少收也不要为了凑数扩大范围；每轮都记 `_meta.run_id` 与本轮新增数，便于说明检索何时收敛。

## 10. 影响力度量与优先级（按发表年校正）

被引数必须**按年龄校正**再看，否则新文献永远排在后面。实用阈值：

| 发表年限 | 被引数 | 判断 |
|---|---|---|
| 0–3 年 | 20+ | 值得关注 |
| 0–3 年 | 100+ | 高影响力 |
| 3–7 年 | 100+ | 重要 |
| 3–7 年 | 500+ | 里程碑 |
| 7 年以上 | 500+ | 奠基性 |
| 7 年以上 | 1000+ | 经典 |

用法：在 `dedup` 用 `--sort citations` 排序时，同时看 `year`；或用 `--year-min` 分段比较，避免把新论文当低影响力。

## 11. 引文滚雪球的正确起点

从 **3–5 篇高度相关的论文**出发（优先本领域公认的高质量刊物），先取它们的参考文献表，找出**被多篇共同引用**的条目——这类往往是奠基性文献；再对这些新种子重复同样的步骤。

每一轮扩展都会引入大量低相关文献，**必须重新过一遍题录筛选**。记录每条的 `_meta.relation`（citations/references）与 `_meta.seed`。

## 12. 筛选矩阵（可选，用于组织证据）

题录筛选阶段可以维护一张「来源 × 主题」交叉表，把每篇文献标为支持/矛盾/未涉及：

```markdown
| Source | Year | Level | Theme A | Theme B | Theme C |
|--------|------|-------|---------|---------|---------|
| Author1 | 2024 | II | ✓ 支持 | — | ✗ 矛盾 |
| Author2 | 2023 | IV | ✓ 支持 | ✓ 支持 | — |
| **合计** | | | **2✓ 1✗** | **1✓ 0✗** | **0✓ 1✗** |
```

用法：合计支持/反对数 → 判断该主题是「强一致」「有争议」还是「空白（gap）」；有争议的主题要在综述里两边都写，空白主题可作为研究缺口讨论。Level 用上面第 9 节的证据等级。

## 13. 引用关系检索（互相引用、共同引用、相关）

需要回答"谁在引用我关心的这篇""这两篇是否互相引用""哪些文献与它主题相近"时：

| 问题 | 命令 | 通道口径 |
|------|------|----------|
| 谁引用了 X | `opencitations --doi <doi> --direction citations` | OpenCitations：跨 DOI/PMID/OpenAlex 交叉标识 |
| X 引用了谁 | `opencitations --doi <doi> --direction references` | OpenCitations |
| X 与 Y 是否互相引用 | 分别查 X 的 citations、Y 的 citations，再查 X 的 references 是否含 Y | 交叉比对 DOI |
| 共同引用（co-citation）/ 主题相近 | `openalex --doi <doi> --related`；Asta 语义检索；S2 recommendations（OpenCitations 的 `similar` 端点未开放） |
| 主题相近 | `openalex --doi <doi> --related` | OpenAlex `related_works` |
| 出版商申报的参考文献 | `crossref --doi <doi> --references` | 出版商口径，可能不完整 |

注意三个通道的口径不同：OpenAlex 的 `cites:`/`cited_by:` 过滤是全库索引口径；Crossref 的 `reference[]` 是出版商申报口径（会漏、也有未结构化的 `unstructured` 文本）；OpenCitations 是第三方引用数据源。**报告关系时要说明用的是哪个口径**，不要把不同口径的数字直接相加。

共同引用与共同被引的典型用法：取 3–5 篇种子文献，用 OpenAlex 的 `--related` 取各自的相关列表，取交集，交集中的文献是"该小领域的枢纽文献"；再对枢纽文献跑前向引用，看它把研究引向哪里。

## 14. 全文筛选的边界（下载需批准）

- 摘要不够时确实需要读全文，这是检索流程的一部分，不是越界；
- 但**下载动作要单独汇报并取得批准**：先出下载计划（条目、域名、URL、目标目录），用户同意后再执行；
- PMC 有免费全文，优先用 `pmc --sections`，不涉及下载；
- Unpaywall/CORE/arXiv 的 OA 文件在 `references/oa-fulltext.md` 的流程里执行。

## 15. 常见失败模式

| 现象 | 多半原因 | 处理 |
|------|----------|------|
| 命中数几万，前 100 条都不相关 | 检索式太宽 / 单词歧义 | 加 `+` 限定、用短语、加 `-` 排除 |
| 命中数为 0 | 某个块过窄，或短语不存在于语料 | 逐块拆开试；去掉引号再试一次 |
| 同一篇反复出现 | 多 query 重叠 | 正常，dedup 处理；不要因此在检索式里删词 |
| 频繁 429 | S2 侧随机限流（约 30%），与是否带 key 无关 | 快速退避重试（脚本默认已如此）；降 `--rps`；减少请求总数 |
| venue 全空 | S2 元数据缺失 | 用 `externalIds` + DOI 回查，或改从 Crossref 补 |
| 摘要大量为空 | 语料未收录全文（bulk 里约 70% 无摘要） | 接受缺失并在报告中标注条数；不要据此下"没有提到"的结论 |
| Asta 调用超时 | 网络/代理/额度 | 小 limit 探活、重试；持续失败则改用 S2 REST |
| Asta 返回 403 HTML | 代理规则/TUN 未生效 | 见 references/asta-mcp.md 的前置条件 |
| BibTeX 条目缺失 | 部分论文无 `citationStyles` | 正常；`export --format bib` 会自动走回退生成器补齐 |
| arXiv 返回 429 | 出口 IP 被 arXiv 限流（本机直连即如此） | 立即停止；加 `--proxy socks5://127.0.0.1:10809` 换出口即可恢复（实测命中 18287 条）；或改用 `openalex --filter type:preprint` |
| IDEAS / SSRN 站点直抓不到 | **当前状态：不可用**——IDEAS 改为 JS 渲染，SSRN 走 Cloudflare 人机校验（详见 `references/econ-sources.md`） | 改用 NBER API + Crossref(ISSN) + `ssrn`（OpenAlex/Crossref 索引）；确需官网内容时走浏览器自动化 |
| PubMed 检索为 0 | 主题不在库内，或 MeSH/字段标签写错 | 去掉字段标签试裸词；确认学科是否属于生物医学 |
| CORE 报缺 key | `CORE_API_KEY` 未配置 | 该渠道当前不可用；改用 Unpaywall / PMC |
