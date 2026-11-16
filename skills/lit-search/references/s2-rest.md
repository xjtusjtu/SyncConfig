# Semantic Scholar REST 速查

来源：官方 Tutorial（`semanticscholar.org/product/api/tutorial`）与 API Docs（`api.semanticscholar.org/api-docs/`），
以及本 skill 脚本的实测行为。标注「实测」的条目来自脚本运行观察，官方文档未明写。

## 三个 base URL

| API | Base URL | 用途 |
|-----|----------|------|
| Academic Graph | `https://api.semanticscholar.org/graph/v1` | 论文、作者、引用、片段 |
| Recommendations | `https://api.semanticscholar.org/recommendations/v1` | 相似/推荐 |
| Datasets | `https://api.semanticscholar.org/datasets/v1` | 全库快照下载 |

## 认证与速率

- Header：`x-api-key: <KEY>`
- 官方口径：**个人 key 为 1 request/second（跨所有端点）**，部分申请经审核可略高；无 key 时与所有匿名用户共享池，可能低至 1 req/s 且不稳定。
- 脚本默认 `--rps 1`。不要假设更高额度。
- 429 会带 `Retry-After`（若服务端给出）。
- **本 skill 的默认策略：429 即停**（`retry_429=False`）。首个 429 直接抛 `S2RateLimitError`，`search`/`expand` 会终止整次运行并保留 `state.json` 供续传。`--retry-429` 才启用重试。

## key 的存放位置（与工作目录无关）

| 位置 | 说明 |
|------|------|
| 环境变量 `S2_API_KEY` | 最高优先级 |
| `<skill_dir>/.env` | 与 skill 绑定，**推荐**（跨机器拷 skill 即带走） |
| `~/.config/lit-search/.env` | 用户级，跨项目 |
| 当前工作目录及其上级 `.env` | 便利项（Obsidian 库里跑时会捡到库根 `.env`） |

## 端点

### 检索

| 端点 | 方法 | 关键参数 | 说明 |
|------|------|----------|------|
| `/paper/search/bulk` | GET | `query`(必填), `token`, `fields`, `sort`, `year`, `publicationDateOrYear`, `venue`, `fieldsOfStudy`, `minCitationCount`, `publicationTypes`, `openAccessPdf` | **大批量首选**。支持布尔语法；用 `token` 翻页 |
| `/paper/search` | GET | `query`, `fields`, `limit`(≤100), `offset`, 同上过滤项 | 相关度排序，单页 ≤100，成本高于 bulk |
| `/snippet/search` | GET | `query`, `fields`, `limit` | 返回约 500 词片段 + 所属论文 |

`sort` 取值：`paperId`、`publicationDate`、`citationCount`，可加 `:asc` / `:desc`。
穷举式检索建议 `paperId:asc`（分页稳定）；按影响力优先则 `citationCount:desc`。

### 详情与批量

| 端点 | 方法 | 说明 |
|------|------|------|
| `/paper/{paper_id}` | GET | 单篇。`paper_id` 支持 SHA / `DOI:` / `ARXIV:` / `PMID:` / `CorpusId:` / `URL:` 前缀 |
| `/paper/batch` | POST | body `{"ids":[...]}`，**≤500 个**；响应为数组，无法解析的 ID 返回 `null`（实测） |
| `/author/batch` | POST | body `{"ids":[...]}`，**≤1000 个** |

### 引文网络

| 端点 | 方法 | 说明 |
|------|------|------|
| `/paper/{id}/citations` | GET | 谁引用了它；正文在 `citingPaper` |
| `/paper/{id}/references` | GET | 它引用了谁；正文在 `citedPaper` |

两者都用 `limit` + `offset` 翻页（响应含 `next`）。**不要**用 `fields=citations` 取引用列表。

### 作者

| 端点 | 方法 | 说明 |
|------|------|------|
| `/author/search` | GET | `query`, `fields`, `limit` |
| `/author/{id}` | GET | 单作者 |
| `/author/{id}/papers` | GET | `limit` + `offset` 翻页 |

### 推荐

| 端点 | 方法 | 说明 |
|------|------|------|
| `/papers/forpaper/{id}` | GET | 单种子相似论文，`from=recent` 或 `all-cs` |
| `/papers/` | POST | body `{"positivePaperIds":[...], "negativePaperIds":[...]}`，`limit` ≤500 |

## fields 预设（脚本内置）

| 预设 | 内容 | 场景 |
|------|------|------|
| `minimal` | title,year,venue,externalIds | 只要题录 |
| `standard` | + authors,citationCount,publicationDate,publicationTypes,abstract | 默认 |
| `ranking` | + influentialCitationCount | 排序/筛选 |
| `export` | + url,openAccessPdf,fieldsOfStudy,journal | 导出 |
| `detail` | + tldr | 水合补全 |
| `bibtex` | title,year,venue,authors,externalIds,citationStyles | 导出 BibTeX |

**禁止**在 `fields` 里请求 `citations` / `references`：单篇高被引论文可返回 20 万字符以上。

## 分页差异

| 端点类型 | 机制 |
|----------|------|
| bulk search | 响应返回 `token`，下次请求带上；无 `token` 即结束 |
| relevance search / citations / references / author papers | `limit` + `offset`，响应含 `next` |

## Datasets API

```
GET /datasets/v1/release/                          # 所有 release 日期
GET /datasets/v1/release/{release_id}              # 该 release 的 dataset 列表（release_id 可用 latest）
GET /datasets/v1/release/{release_id}/dataset/{name}   # 预签名下载链接（需 key）
GET /datasets/v1/diffs/{start}/to/{end}/{name}     # 增量 diff（需 key）
```

- 数据为 JSONL（每行一个 JSON 对象），适合 pandas / Spark 本地处理。
- 下载链接是**临时预签名 URL**，过期需重新获取。
- 适用场景：需要远超 API 速率的全库查询、embedding、citation graph 离线分析。

## 错误码

| 码 | 含义 | 处理 |
|----|------|------|
| 400 | 参数不合法（query 过长、sort 值错、fields 拼错） | 改参数，不要重试 |
| 401/403 | key 缺失/无效/无权限 | 检查 `S2_API_KEY`；Datasets 下载链接必须带 key |
| 404 | 资源不存在 | `get_paper` 返回 None；DOI 查询偶发 not found，改用标题检索 |
| 429 | 超速 | **默认立即停止**（抛 `S2RateLimitError`，终止整次运行）；`--retry-429` 才重试 |
| 500/502/503/504 | 服务端 | 指数退避重试 |

## 实测补充

- bulk search 不返回 `tldr`（官方参数表未列 `tldr` 于 bulk 场景）。
- `externalIds`、`citationCount`、`influentialCitationCount` 在 bulk 中可用。
- Windows 上 `requests` 会读取系统代理（注册表），导致 `ProxyError: Cannot connect to proxy`；用 `--no-proxy`（`trust_env=False`）可直连成功。
- **代理优先级（2026-11-13 实测并已修复）**：注册表里的系统代理会被 `requests` 自动读取，并**覆盖** session 级代理——即使显式设置 `session.proxies` 为 socks5 地址，实际仍会去连注册表里的 HTTP 代理端口，表现为 `ProxyError` 或 TLS 握手被中断。实测对照：请求级 `proxies=` 正常、session 级 + `trust_env=True` 失败、session 级 + `trust_env=False` 正常。脚本现统一走 `s2api.configure_session()`：**只要传了 `--proxy` 就关闭 `trust_env`**，保证显式代理优先；同时保留 `REQUESTS_CA_BUNDLE`（应对做 TLS 中间人的代理）。
- 直连可用（2026-11-13 实测）：`GET /paper/search/bulk?query=advertising sales` 返回 `total` + `token` + `data`。
- 匿名共享池会 429（`Too many requests ... apply for a key for higher rate limits`）。
- **配了个人 key 仍会 429**：实测（2026-11-13，本机 key）429 是**间歇性随机拒绝**，6 秒一次请求时 8 次里失败 2 次（bulk、batch、citations 三个端点表现一致），且**立即返回**（0.2–1.0 s），不是"配额窗口耗尽"式的长等待。
- 应对：**快速退避重试**最有效（2/4/8/16/32s）。实测同一批任务，退避设为 8/16/32/64/120s 时耗时 247 s 仍失败；改为 2/4/8/16/32s 后 39 s 成功。
- 单次响应耗时波动大：0.3–30 s。
- `--anonymous` 可显式允许无 key 运行（走匿名池，速率低）。
- `batch_papers` 的 `citationStyles` 在**无 key 时也能返回** BibTeX（实测）；`get_paper` 的 `fields` 里加 `citationStyles` 同理。

## 实测：布尔语义与元数据覆盖（2026-11-13，key 已配置）

### 语法语义（与官方文档一致，实测可复现）

| 检索式 | total | 结论 |
|--------|-------|------|
| `"speech rate"` | 5346 | 引号 = **严格短语** |
| `speech rate` | 75451 | 无引号 = 各词可分散出现，量级差 14 倍 |
| `"voice loudness"` | 194 | 同上（短语在库中确实存在） |
| `voice loudness` | 6818 | 短语 vs 散词：35 倍差 |
| `"speech rate" +advertising` | 12 | 短语 + 必含词**同时**生效 |
| `"voice loudness" +advertising` | 0 | 短语存在但与 `advertising` 共现为零 |

推论：

- 引号是**严格短语**，不是"词序忽略"。用引号前先确认该短语在语料里真实存在（先跑不带 `+` 的短语检索看 total）。
- `+`（必含）在**有摘要的记录上 100% 成立**：实测 `advertising +sales` 取回 1000 条，其中有摘要的 161 条里，100% 同时含 "sales" 和 "advertising"。
- `-`（排除）有效：实测 `advertising -privacy` 取回 1000 条，含 "privacy" 的 0 条。

### ⚠️ 元数据缺失是最大的坑

bulk 返回的记录里**只有约 25%–30% 带摘要**（实测多个检索式：无引号 1000 条中仅 259–264 条有摘要；带引号 194 条中 75 条有摘要）。

后果：

1. 用标题+摘要做词项后筛，会**漏掉大量真正相关的论文**，同时保留无法核验的记录。
2. 无法核验的记录**不要默认丢弃**——脚本的 `--require-term/--exclude-term` 只在有摘要的记录上判定，无摘要的保留并在 stderr 报告数量。
3. `hydrate` 能补 `tldr`、`openAccessPdf`、完整字段，但**补不出库里本来就没有的摘要**。
4. 涉及摘要的结论（"摘要提到 X"）必须区分"没有摘要"与"摘要里没有 X"。
