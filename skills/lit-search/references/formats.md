# 导出格式（薄导出层）

实现：`scripts/formats.py`；CLI：`litsearch.py export --format ...`。

## 定位

本层只做「记录 → 字符串」的一次性导出，**不是一等公民**，刻意不包含：

- 正文引用编号、重编号、幽灵引用清理
- 引文校验（DOI 可解析性、字段完整性、条目去重）
- Word / LaTeX 排版、投稿格式转换

这些属于下游 agent、其它 skill 或脚本。

## 支持格式

| `--format` | 说明 |
|---|---|
| `jsonl` | 原始统一记录（默认首选，下游可再加工） |
| `csv` | 表格化 |
| `md` | Markdown 表格 + 前 N 条详情 |
| `bib` | BibTeX |
| `ris` | RIS 交换格式 |
| `apa` | APA 单条字符串（每条一行） |
| `gbt` | GB/T 7714-2015 顺序编码制参考文献表 |

## BibTeX

优先级：

1. 记录里已有 `citationStyles.bibtex`（S2 批量接口提供）→ 直接用；
2. 没有 → 若有 S2 key，`export` 会先用 batch 补齐（可用 `DOI:` / `PMID:` / `ARXIV:` 前缀形式定位），再生成；
3. 仍没有 → **极简回退生成器**：类型由 `publicationTypes` / venue 推断，作者 `姓, 名`，key 为 `姓+年+标题首词`（重复自动加 a/b 后缀）。

```bash
python scripts/litsearch.py export --in out/papers.jsonl --format bib --out out/refs.bib --no-proxy
```

## RIS

标准字段：`TY / AU / TI / JO(期刊) 或 T2 / PY / DA / VL / IS / SP / EP / DO / UR / AB / ER`。页码 `12-30` 会拆成 `SP 12` + `EP 30`。

## APA

形如：`Smith, J., & Doe, J. (2020). Title. Journal, 57(2), 12-30. https://doi.org/...`
（作者首字母带点、末位作者前用 `, & `；超过 20 位作者时截断并加 `...`）

## GB/T 7714-2015

形如：`1. SMITH J, DOE J. Title[J]. Journal, 2020, 57(2): 12-30. DOI: ...`

规则：

| 项 | 处理 |
|---|---|
| 作者 | 西文：姓大写 + 名首字母（`SMITH J`）；中文：原样保留 |
| 作者 >3 | 前 3 位 + `等`（中文文献）/ `et al`（英文文献） |
| 类型标记 | `[J]` 期刊、`[C]` 会议、`[M]` 专著、`[D]` 学位论文、`[R]` 报告、`[Z/OL]` 预印本 |
| 期刊名 | 保留数据源返回的**原样**（不擅自缩写或展开） |
| 缺字段 | **只告警不编造**，stderr 列出条目编号与缺失项（如"缺少刊名""学位论文缺少授予单位"） |

未实现：著者-出版年制、期刊缩写↔全称展开表、专著出版地。中文文献的全角标点与「等」已处理，但**刊名全称/全角标点的严格排版仍需人工核对**。

## 完整性规则

所有格式都遵守：**不编造 PMID、DOI、作者、刊名、卷期页**。数据源没给的字段就留空并告警。
