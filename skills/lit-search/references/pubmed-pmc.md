# PubMed / PMC（NCBI E-utilities）

实现：`scripts/ncbi.py`；CLI：`litsearch.py pubmed` / `pmc` / `idconv`。

Base：`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

## 凭据与限速

| 项 | 值 |
|---|---|
| key | 可选 `NCBI_API_KEY`（有 key 10 req/s，无 key 3 req/s） |
| 邮箱 | `NCBI_EMAIL`（礼貌池，建议填真实邮箱） |
| 限速行为 | 遇 429 立即停止，不重试 |

## 端点

| 端点 | 用途 | 本 skill 封装 |
|---|---|---|
| `esearch.fcgi?db=pubmed&term=...&retmax=&retmode=json` | 检索，返回 PMID 列表 + 命中总数 | `NCBIClient.esearch()` |
| `efetch.fcgi?db=pubmed&id=...&retmode=xml` | 取完整题录 + 摘要 + 外部 ID | `efetch_pubmed()` / `search()` |
| `efetch.fcgi?db=pmc&id=...&retmode=xml` | PMC 全文 JATS XML | `pmc_fulltext()` / `pmc_sections()` |
| `elink.fcgi?dbfrom=pubmed&db=pubmed&linkname=pubmed_pubmed` | 相关文献 | `related()` |
| `elink.fcgi?...&linkname=pubmed_pubmed_citedin` | 被引文献 | `cited_by()` |
| `elink.fcgi?...&db=pmc&linkname=pubmed_pmc` | 对应 PMC ID | `pmc_ids()` |
| `https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/?ids=...` | ID 互转 | `idconv()` |
| `https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/<id>` | BioC 结构化全文 | `bioc()` |

## PubMed 检索语法要点

- 字段标签：`"advertising"[Title/Abstract]`、`"advertising"[TI]`、`"Smith J"[Author]`、`"Harvard"[Affiliation]`
- MeSH：`"Advertising"[MeSH Terms]`、`"Advertising"[MeSH Subheading]`；未标 MeSH 的新文献可用 `"term"[MeSH Terms] OR "term"[Title/Abstract]`
- 出版类型：`"Randomized Controlled Trial"[Publication Type]`、`"Review"[Publication Type]`
- 日期：`("2015"[Date - Publication] : "2024"[Date - Publication])`
- 布尔：`AND` / `OR` / `NOT`，括号分组；PubMed 会对常用词做自动词形还原

## 命令

```bash
python scripts/litsearch.py pubmed --query '"advertising"[Title/Abstract] AND "sales"[Title/Abstract]' \
    --limit 50 --date-range 2015:2024 --pub-type Review --out out/pubmed.jsonl --no-proxy

python scripts/litsearch.py pmc --pmid 32939066 --sections --out out/fulltext.md --no-proxy
python scripts/litsearch.py pmc --pmcid PMC7759461 --bioc --out out/bioc.json --no-proxy
python scripts/litsearch.py idconv --ids "10.1038/s41586-020-2649-2" --no-proxy
```

## 输出字段映射

`title / year / venue(期刊全名) / authors / externalIds{DOI,PMID,PMCID} / publicationTypes / abstract(带 ABSTRACT 分段标签) / volume / issue / pages`

PubMed 的摘要是分段的（BACKGROUND / METHODS / RESULTS 等），脚本按 `标签: 内容` 拼接。

## 注意

- PubMed 主题偏生物医学；经济/管理类文献多数不在库内。
- PMC 只收录有资助或作者自愿存档的全文；`elink` 返回空表示没有 PMC 版本。
- `idconv` 单次最多 200 个 ID；结果里的 `live` 字段为真表示当前可解析。
- 官方建议同时提供 `tool` 与 `email` 参数，脚本已自动附带 `tool=lit-search`。
