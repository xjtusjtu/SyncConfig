# OpenAlex

实现：`scripts/openalex.py`；CLI：`litsearch.py openalex`。

Base：`https://api.openalex.org`

## 凭据与限速

| 项 | 值 |
|---|---|
| key | 可选 `OPENALEX_API_KEY`（建议配置，官方对匿名请求限速较紧） |
| 邮箱 | 可选 `OPENALEX_MAILTO`（礼貌池） |
| 限速行为 | 遇 429 立即停止，不重试 |

## 能力

| 能力 | 参数 | 说明 |
|---|---|---|
| 关键词检索 | `--query` | 映射到 `search=` |
| 过滤 | `--filter` | OpenAlex 过滤表达式，见下 |
| 限定来源 | `--source ssrn\|nber\|aer\|...` | 脚本内置别名（见 `references/journal-identifiers.md`） |
| 排序 | `--sort` | 如 `publication_year:desc`、`cited_by_count:desc` |
| 深翻页 | `--cursor` | `cursor=*` 起翻，单页 200 条，突破 offset 10000 限制 |
| 字段裁剪 | `select=` | 只取需要的字段，省流量 |
| 聚合 | `group_by=` | 如 `publication_year`、`primary_topic` |
| 被引 / 参考 | `--citations` / `--references` | 配 `--doi` 或 `--work-id`；S2 不可用时的稳定替代。实现走 filter（`cites:W…` / `cited_by:W…`），**没有** `/works/{id}/cited_by` 这种路径 |
| 主题相近 | `--related` | OpenAlex 的 `related_works` 字段（不是引用边）；规范化记录中的 `relatedWorks` / `referencedWorks` |

> OpenAlex 的引文边用 filter 表达：`cites:W123` = 引用了 W123 的论文；`cited_by:W123` = W123 引用的论文。传 DOI 时脚本先解析成 W-id 再查。

常用 filter 片段：

```
from_publication_date:2020-01-01,to_publication_date:2024-12-31
type:article                      # article / preprint / book-chapter / dataset
is_oa:true
primary_location.source.id:S23254222          # 按刊物
authorships.author.id:A123456789
host_venue:https://doi.org/10.1000/xxx
```

> OpenAlex 的 `select` 只支持根级字段，`abstract` / `abstract_inverted_index` 不可被 select；要用摘要就别加 select。
> ORCID 过滤要用**裸值**（`author.orcid:0000-0002-3141-5845`），不是 `https://orcid.org/...` 形式。

## 字段映射

| OpenAlex | 统一记录 |
|---|---|
| `display_name` | `title` |
| `publication_year` / `publication_date` | `year` / `publicationDate` |
| `primary_location.source.display_name` | `venue` |
| `authorships[].author.display_name` | `authors[].name` |
| `doi`（去掉 `https://doi.org/` 前缀） | `externalIds.DOI` |
| `ids.pmid` / `ids.pmcid` | `externalIds.PMID` / `PMCID` |
| `cited_by_count` | `citationCount` |
| `open_access` | `openAccess{oa_status,is_oa,oa_url}` |
| `primary_location.pdf_url` + `best_oa_location.pdf_url` + 各 `locations[].pdf_url` | `pdfUrls[]`（按 primary → best_oa → 其它 locations 去重） |
| `concepts` / `topics` | `concepts` / `topics` |

**摘要还原**：OpenAlex 用 `abstract_inverted_index`（词 → 位置数组）存储，脚本按位置排序还原成正常文本；约 20%–30% 的记录有摘要。

**PDF 直链价值**：`primary_location.pdf_url` 对 SSRN 这类站点常为空，但 `locations[]` 里常有第三方仓库镜像（EconStor、IZA、机构库），脚本已一并收集到 `pdfUrls`，可直接进下载计划。

## 命令

```bash
python scripts/litsearch.py openalex --query "advertising" --limit 50 --no-proxy
python scripts/litsearch.py openalex --source ssrn --query "advertising" --limit 30 --no-proxy
python scripts/litsearch.py openalex --filter "type:preprint,from_publication_date:2023-01-01" \
    --sort cited_by_count:desc --cursor --limit 200 --out out/oa.jsonl --no-proxy
python scripts/litsearch.py openalex --doi 10.1038/s41586-020-2649-2 --citations --limit 20 --no-proxy
```

## 何时用 OpenAlex 而不是 S2

- 需要**跨学科覆盖**（OpenAlex 收录全部学科，S2 偏 CS/生物医学）
- 需要**期刊/机构/主题维度的聚合统计**
- 需要 **OA 状态**与出版社信息
- S2 遇到 429 停手后的稳定替代渠道
