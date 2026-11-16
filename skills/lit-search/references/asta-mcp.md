# Asta MCP 速查

Asta 是 Ai2 的 Scientific Corpus Tool，把 Semantic Scholar 学术图谱以 MCP 暴露出来。

- **端点**：`https://asta-tools.allen.ai/mcp/v1`
- **认证**：`x-api-key` header（本机已配在 `opencode.json` 的 `mcp.asta`）
- **传输**：streamable HTTP
- **本 skill 不直接发 HTTP**：由 agent 调用 MCP 工具；脚本只负责 S2 REST 侧

## MCP 工具 vs 脚本侧通道

`scripts/asta_client.py` 与直接调用 MCP 工具**不是两套服务**，而是同一服务的两条传输路径：

| | 直接调 MCP 工具 | `scripts/asta_client.py` |
|---|---|---|
| 传输 | host 负责的 MCP 会话（streamable HTTP） | 脚本自己发同样的 MCP 消息 |
| 凭据 | host 的 `opencode.json` | 脚本读 `.env` 的 `ASTA_API_KEY` |
| 结果落盘 | 结果直接在会话里，需要时再写文件 | 直接写 JSONL，天然适合批量 |
| 路由控制 | 依赖 host 的网络配置 | `--proxy` / `--auto-proxy` 可显式指定 |
| 典型场景 | 交互式查询、片段证据、边聊边查 | 一次跑几十上百条、接入脚本流水线、MCP 挂掉时兜底 |
| 额度 | 同样消耗 Asta 额度 | 同样消耗 Asta 额度（**不更省**） |

选择规则：**agent 在会话里做事 → 用 MCP 工具**；**要成批落盘、要写进自动化 → 用脚本**。两者数据同源，可交叉验证。

## 前置条件：路由与 TUN（否则一律 403）

**调用前先确认 Asta 工具已注册**（host 里能看到 `asta__*` / `mcp__asta__*` 工具名）。看不到工具时：**不要退化成裸 HTTP 调用、不要自己发明结果**——先按下面的宿主配置注册 MCP 服务，重启/重载 host 后再调用。

各宿主的注册方式：

```bash
# Claude Code
claude mcp add -t http -s user asta https://asta-tools.allen.ai/mcp/v1 -H "x-api-key: $ASTA_API_KEY"

# Codex CLI（~/.codex/config.toml）
#   [mcp_servers.asta]
#   url = "https://asta-tools.allen.ai/mcp/v1"
#   env_http_headers = { "x-api-key" = "ASTA_API_KEY" }

# 通用 MCP 客户端
#   url = https://asta-tools.allen.ai/mcp/v1
#   header = { "x-api-key": "<ASTA_API_KEY>" }
```

`https://asta-tools.allen.ai/mcp/v1` 直连会被边缘 WAF 拦成 **403 HTML 页面**（不是 JSON 错误，也不是 key 问题）。

必须满足：

1. 代理软件（mihomo / clash）**自定义规则**里加入
   `DOMAIN,asta-tools.allen.ai,PROXY`，且该规则必须排在最终 `MATCH` 之前
2. 打开 **TUN 模式**，让所有应用（含 MCP 客户端与 Python）都走这条规则
3. 确认没有别的规则把该域名指回直连

满足后，任何进程直连该端点都会被代理接管。症状与判别：

| 现象 | 判别 | 处理 |
|------|------|------|
| 返回 `<!doctype html>...403 Forbidden` | 路由没生效 | 查上面 1–3；不要改检索式、不要换 key |
| 返回 JSON 的 `{"error": ...}` | 路由正常，API 层错误 | 按参数排查（见下） |
| `-32001 Request timed out` | 链路抖动 | 小 limit 重试；连续失败再查代理 |
| 工具列表为空 | MCP 服务未注册/未加载 | 检查 `opencode.json` 的 `mcp.asta` 配置 |

本机实测：直连 403；经 `socks5://127.0.0.1:10809` 可正常 `initialize` + `tools/call`（2026-11-13）。

## 脚本侧备用通道

`scripts/asta_client.py` 用同一套 MCP 协议（`initialize` → `notifications/initialized` → `tools/call`，
无 session id 要求），可在 MCP 工具不可用时从 Python 直接调用：

```bash
python asta_client.py tools --auto-proxy
python asta_client.py search --keyword "advertising sales" --limit 20 --fields "title,year,venue,externalIds,citationCount" --out r.jsonl
python asta_client.py paper --ids <paperId> <DOI:...> --fields "title,year,venue" --out p.jsonl
python asta_client.py citations --id <paperId> --limit 50 --date-range "2020-" --out c.jsonl
python asta_client.py snippets --query "..." --limit 10 --paper-ids a,b --out s.jsonl
python asta_client.py authors --name "..." --fields "name,paperCount,citationCount,hIndex,externalIds"
python asta_client.py author-papers --author-id <id> --limit 50 --paper-fields "title,year,venue,citationCount"
```

- `--auto-proxy`：直连失败后依次尝试 `socks5://127.0.0.1:10809` → `socks5h://…` → `http://…:10809` → `:10808`
- 返回解析：Asta 的 content blocks 中每段文本通常是一个 JSON 对象，脚本已拆成 JSONL
- 不可解析的 ID 会被静默丢弃（实测：`get_paper_batch` 传 2 个 ID，其中 1 个无效 → 只返回 1 条）

## 工具路由

| 意图 | 工具 | 关键参数 |
|------|------|----------|
| 主题检索 | `search_papers_by_relevance` | `keyword`, `fields`, `limit`, `publication_date_range`, `venues` |
| 已知标题 | `search_paper_by_title` | `title`, `fields`, `venues`, `publication_date_range` |
| 已知 ID | `get_paper` | `paper_id`（支持 `DOI:`/`ARXIV:`/`PMID:`/`CorpusId:`/`URL:` 前缀） |
| 多个 ID | `get_paper_batch` | `ids` 为 **JSON 数组** |
| 谁引用了它 | `get_citations` | `paper_id`, `fields`, `limit`(默认 100), `publication_date_range` |
| 找作者 | `search_authors_by_name` | `name`, `fields`, `limit` |
| 作者论文 | `get_author_papers` | `author_id`, **`paper_fields`**, `limit`(默认 1000) |
| 片段证据 | `snippet_search` | `query`, `limit`(默认 20), `venues`, `paper_ids`(逗号分隔), `inserted_before` |

## 参数例外（最容易踩）

- `get_author_papers` 的字段参数叫 **`paper_fields`**；传 `fields` 会被静默忽略，只返回标题。
- `get_author_papers` **不支持** `venues` 过滤，需客户端按主题/venue 再筛。
- **`get_author_papers` 的日期过滤在分页之后才应用**，会把范围内但落在当前页之外的论文丢掉（实测：知名作者 `2024:2024` 过滤返回空）。因此不要只靠它的日期参数，拿到列表后在客户端按年份与主题再筛一遍。
- `get_citations` 支持 `publication_date_range`，但**不支持** `venues`。
- `snippet_search` **既不支持** `fields` 也不支持 `publication_date_range`；它用 `inserted_before`、`paper_ids`、`venues`。
- `get_paper_batch` 的 `ids` 是 JSON 数组；`snippet_search` 的 `paper_ids` 是逗号分隔字符串（≤100 个）。两者格式不同。
- `get_paper_batch` 对**无法解析的 ID 静默丢弃**（不报错、不返回 null）。批量调用后必须把返回的 `paperId` 与请求清单**回对账**，缺哪一条要单独补查。
- `search_authors_by_name` 默认 `fields="name"`，只返回 `name` + `authorId`；要排序必须显式请求 `affiliations,paperCount,citationCount,hIndex,externalIds`。
- `publication_date_range` 格式为 `YYYY-MM-DD:YYYY-MM-DD`，支持简写：`"2021:"`（2021 年至今）、`":2015-01"`（2015-01 之前）、`"2015:2020"`。
- `venues` 匹配 Semantic Scholar 的**精确** venue 字符串，"NeurIPS" 这类简称可能匹配不到。

## fields 与上下文控制

- **不要**在 `fields` 里请求 `citations` / `references`：单篇高被引论文可返回 20 万字符以上，直接撑爆上下文。前向引用用 `get_citations`（自带分页）。
- Asta 没有独立的 `get_references` 工具；取参考文献列表只能用 `get_paper(fields=references)`，且仅限参考文献数较少的论文。
- `externalIds`、`citationCount`、`influentialCitationCount` 不在官方 `fields` 列表里，但会透传到 Semantic Scholar 并生效（best-effort，未来可能失效）。

常用预设：

```
元数据:   title,year,authors,venue,tldr,url,abstract
排序表:   title,year,authors,venue,tldr,url,abstract,citationCount,influentialCitationCount
DOI 交接: title,year,authors,venue,tldr,url,externalIds
```

## 默认 limit（容易一次拉太多）

| 工具 | 默认 | 建议 |
|------|------|------|
| `get_author_papers` | 1000 | 显式设 50 左右 |
| `get_citations` | 100 | 20–50 |
| `search_papers_by_relevance` | 50 | 10–20 |
| `snippet_search` | 20 | 5–10（每条约 500 词，最重） |

## 与 S2 / Crossref 的分工

跨通道的能力对比与匹配机制差异（含实测）统一放在 `references/channels.md`，此处不重复。

要点一句话：**S2 关键词匹配用来穷举，Asta 语义匹配用来探索与找证据；Asta 只有前向引用，后向（参考文献）用 S2。**

## 输出与交互规则

- **报告用了哪个工具**；只有工具确实暴露总数时才报"共 N 篇"，否则只报"返回 N 条 / 每页 N 条"，不要让用户误以为是全库总量。
- 结果先给**不超过 10 条的表格**（标题、年份、刊物、被引数若已取），再展开最相关的几条。
- 用户用中文提问时用中文写摘要，**文献标题保留原文**。
- 结果后面给可选后续动作：**详述 / 收窄 / 引文 / 片段 / 导出 / 结束**。
- 绝不猜 ID：用户给的是模糊标题时先 `search_paper_by_title`，再 `get_paper`。
- 字段缺失就明说缺失（`abstract`、`venue` 为 null 时照实说），不要编造。

## 排障

- **`-32001` 超时**：先用 `limit=1` 探活再重试；偶发超时后重试通常成功（实测）。连续失败按网络/代理问题处理。
- **工具不可见**：说明 MCP 服务未启用或未加载；不要退化成裸 HTTP 调用，也不要编造结果。
- **空 `abstract`**：语料中并非所有论文都有全文；改用 `snippet_search` 或退回 title + tldr。
- **venue 匹配**：`venues` 匹配 Semantic Scholar 的**精确** venue 字符串；"NeurIPS" 这类俗称可能匹配不到，改用日期/关键词过滤。
- **日期过滤的边界**：`publication_date_range` 可能返回 `publicationDate` 为 null 的记录（只有 `year` 保证存在），未知日期按当年 1 月 1 日处理，边界年份是近似值。
- **额度**：Asta 有额度/速率限制，批量前先小样本试跑；不要把它当无限爬虫。
