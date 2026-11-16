# 开放获取与全文：Unpaywall / CORE

实现：`scripts/oa_fulltext.py`；CLI：`litsearch.py unpaywall` / `core`。

## 下载必须先获批准（硬性流程）

本 skill 支持下载 PDF/全文，但**下载永不隐式执行**：

1. 先只出「下载计划」：条目、来源域名、URL、文件类型、目标目录；
2. 把计划**汇报给用户并取得批准**；
3. 批准后才加 `--confirm-download` 重跑。

```bash
# 1) 只看计划
python scripts/litsearch.py unpaywall --in out/papers.jsonl --out out/papers_oa.jsonl \
    --plan --dir downloads --no-proxy

# 2) 拿到用户批准后
python scripts/litsearch.py unpaywall --in out/papers_oa.jsonl --plan --dir downloads \
    --confirm-download --no-proxy
```

未加 `--confirm-download` 时，脚本只打印计划并返回 `awaiting_approval`，**不建目录、不发下载请求**。

## Unpaywall

Base：`https://api.unpaywall.org/v2/{doi}?email=...`

| 项 | 值 |
|---|---|
| 凭据 | `UNPAYWALL_EMAIL` **必需**（真实邮箱，脚本不校验格式但服务端会拒） |
| 限速 | 遇 429 立即停止 |

返回的 OA 信息：

| 字段 | 含义 |
|---|---|
| `oa_status` | `gold` / `hybrid` / `green` / `bronze` / `closed` |
| `is_oa` | 是否开放获取 |
| `best_oa_location.url_for_pdf` | 最佳 PDF 直链（没有则为 `url` 落地页） |
| `oa_locations[]` | 全部候选位置（版本可能是 publishedVersion / submittedVersion） |

脚本把结果写入记录的 `openAccess` 字段；批量给已有记录补字段用 `--in papers.jsonl --out papers_oa.jsonl`。

## CORE

Base：`https://api.core.ac.uk/v3/`

| 项 | 值 |
|---|---|
| 凭据 | `CORE_API_KEY*` **必需**；支持多个 key 轮流使用（见下） |
| 端点 | `GET /search/works?q=&limit=&offset=`、`GET /works/{id}` |
| 认证 | `Authorization: Bearer <key>` |

记录里的 `fullTextUrls` 是可下载的全文链接列表；`fullText` 是可直接读的全文字符串（部分记录有）。

### 多 key 轮流使用

.env 里可写多个 key，按前缀收集、名称自然排序：

```dotenv
CORE_API_KEY1=...
CORE_API_KEY2=...
```

也兼容单 key 写法 `CORE_API_KEY=...`，以及命令行 `--core-api-key "key1,key2"`。

规则：

- **分摊配额**：每次请求按顺序取下一个 key（轮转），避免单个 key 打到自己的限额；
- **401/403 自动换 key**：当前 key 无效或无权限时，换下一个重试（最多轮完一轮）；
- **429 立即停止**：不靠换 key 绕过限流——遇到 429 仍然停下并报错，这是本 skill 的硬规则；
- `litsearch.py check` 会显示 `CORE_API_KEY* 已配置 N 个（轮流使用）`。

实测（2026-11-13）：2 个 key 均可用，轮转正常；用一个无效 key 打头会自动切到第二个并成功返回。

## 其它全文途径（不属本 skill，但检索时值得先查）

- **PMC**：见 `references/pubmed-pmc.md`（`litsearch.py pmc --sections` 直接拿正文，最省事）
- **S2 片段检索**：`litsearch.py snippets` 给出原文片段，用于核对某句话
- **机构订阅 / 数据库**：本 skill 不涉及

## 注意

- Unpaywall 只覆盖有 DOI 的文献；无 DOI 记录需先从 Crossref/OpenAlex 补 DOI。
- OA 链接可能指向预印本版本，与正式版内容有差异，引用时留意版本。
- 下载内容仅供阅读使用，版权与授权以出版方许可为准。
