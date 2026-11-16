# NBER 工作论文

实现：`scripts/nber.py`；CLI：`litsearch.py nber`。

| 项 | 值 |
|---|---|
| 凭据 | **不需要**（官方 JSON API，免注册） |
| 端点 | `https://www.nber.org/api/v1/working_page_listing/contentType/working_paper/...` |
| 限速 | 官方未公布限制；脚本按 ~1 req/s 节流 |
| 429 行为 | 立即停止，不重试 |

## 端点与参数

```
{base}/_/_/search?page=1&perPage=20&q=<关键词>
{base}/programs/<项目名>/search?page=1&perPage=20&q=<关键词>
```

| 参数 | 含义 |
|---|---|
| `q` | 关键词（省略则列全部） |
| `page` / `perPage` | 分页；**实测 perPage 最小生效值为 50**（传 3 仍回 50 条），脚本在本地按 `--limit` 截断 |
| `newThisWeek=true` | 只看本周新发布 |

项目名放在路径里（空格用 `+`），完整清单见 `scripts/nber.py` 的 `PROGRAMS`：Economic Fluctuations and Growth、Labor Studies、Industrial Organization、Public Economics、Economics of Health、Development Economics、International Finance and Macroeconomics、International Trade and Investment、Monetary Economics、Corporate Finance、Asset Pricing、Economics of Education、Economics of Aging、Children and Families、Law and Economics、Environment and Energy Economics、Political Economy。

## 字段要点（实测）

| 字段 | 注意 |
|---|---|
| `authors[]` | 含 HTML 锚点标签，脚本已清洗 |
| `abstract` | **只有前约 300 字符**——要完整摘要需另找渠道（OpenAlex 可能有更长版） |
| `displaydate` | 如 `May 2023`，脚本从中提取年份；API **无日期过滤参数**，按年筛需本地做 |
| `url` | `/papers/w31201` → 拼成 `https://www.nber.org/papers/w31201` |
| 排序 | 按相关度，不是时间 |

## ID 与直链构造（可跳过一次查询）

| 用途 | 规律 | 例 |
|---|---|---|
| DOI | `10.3386/w{number}` | w31201 → `10.3386/w31201` |
| PDF | `https://www.nber.org/system/files/working_papers/w{n}/w{n}.pdf` | → `.../w31201/w31201.pdf` |
| OpenAlex 收录 | source id `S2809516038`（"National Bureau of Economic Research"，3.4 万条） | `openalex --source nber` |

## 单篇完整题录

`https://www.nber.org/papers/w31201` 的 HTML 里有 `citation_*` meta 标签（`citation_title`、`citation_author`、`citation_doi`、`citation_publication_date`、`citation_pdf_url`），比列表接口更全：

```bash
python scripts/litsearch.py nber --paper w31201 --no-proxy
```

## 命令

```bash
python scripts/litsearch.py nber --query "advertising firm performance" --limit 20 --no-proxy
python scripts/litsearch.py nber --query "minimum wage" --program "Labor Studies" --limit 20 --no-proxy
python scripts/litsearch.py nber --new-this-week --limit 50 --no-proxy
python scripts/litsearch.py nber --query "..." --year-min 2020 --out out/nber.jsonl --no-proxy
```

## 互补渠道

NBER 只覆盖 NBER 自己的工作论文。其它经济学工作论文用：

- SSRN → `litsearch.py ssrn`（经 OpenAlex + Crossref 索引）
- 其它系列 → `openalex --filter "type:preprint"`、`crossref --filter type:posted-content`
