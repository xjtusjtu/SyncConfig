# 预印本：arXiv / bioRxiv / medRxiv

实现：`scripts/preprints.py`；CLI：`litsearch.py arxiv` / `biorxiv`。

## arXiv（Atom XML，标准库解析）

Base：`https://export.arxiv.org/api/query`

| 项 | 值 |
|---|---|
| key | 不需要 |
| 限速 | 官方建议 **3 秒/请求**，脚本已内置节流 |
| 429 行为 | 立即停止，不重试 |

检索式用 arXiv 语法：

| 语法 | 含义 |
|---|---|
| `all:keyword` | 任意字段 |
| `ti:` / `au:` / `abs:` / `cat:` / `jr:` / `co:` / `rn:` | 标题/作者/摘要/分类/期刊/评论/报告号 |
| `AND` `OR` `ANDNOT` | 布尔 |
| `submittedDate:[202001010000 TO 202412312359]` | 日期区间 |

命令：

```bash
python scripts/litsearch.py arxiv --query 'all:advertising AND cat:econ.GN' --limit 50 --no-proxy
python scripts/litsearch.py arxiv --query 'ti:"speech rate"' --categories econ.GN,cs.LG \
    --date-range 2020-01-01:2024-12-31 --sort-by submittedDate --out out/arxiv.jsonl --no-proxy
```

### 分类过滤不可靠（实测提醒）

arXiv 的 `cat:` 过滤**并不总是严格生效**，可能混进其它学科的论文。加 `--strict-category` 让脚本按记录里的 `categories` 本地复核一遍并报告剔除条数：

```bash
python scripts/litsearch.py arxiv --query 'all:econ' --categories econ.GN --strict-category --limit 50
```

### PDF 下载

arXiv 全文免费开放，PDF 直链规律为 `https://arxiv.org/pdf/{id}`。下载同样走「先出计划、获批准再执行」：

```bash
python scripts/litsearch.py arxiv --query 'ti:"speech rate"' --limit 5 --plan --dir downloads --no-proxy
python scripts/litsearch.py arxiv --query 'ti:"speech rate"' --limit 5 --plan --dir downloads \
    --confirm-download --no-proxy
```

### 实测注意

部分网络出口 IP 会被 arXiv 直接返回 **429**（本机直连即如此）。此时：

1. 脚本按策略立即停止并报错，不重试、不空转；
2. **换出口 IP 即可恢复**：加 `--proxy socks5://127.0.0.1:10809` 后实测命中 18287 条、正常返回（2026-11-13）；
3. 换渠道：`openalex --filter "type:preprint"` 或 `crossref --filter type:posted-content` 都能覆盖大部分 arXiv 预印本。

> 注意：Windows 注册表里的系统代理会被 `requests` 自动读取并**覆盖**显式指定的代理。脚本已处理：只要传了 `--proxy`，就关闭 `trust_env`，保证显式代理优先。

## bioRxiv / medRxiv（JSON API）

| 端点 | 用途 |
|---|---|
| `https://api.biorxiv.org/details/{server}/{interval}/{cursor}/json` | 按日期区间浏览预印本 |
| `https://api.biorxiv.org/pubs/{server}/{interval}/{cursor}/json` | 预印本 → 正式发表版的对应关系 |

- `server`：`biorxiv` 或 `medrxiv`
- `interval`：`2024-01-01/2024-12-31`（日区间）或 `2024-01/2024-12`（月区间）
- `cursor`：翻页游标，返回体里的 `next_cursor`

**这两个源没有关键词检索接口**，只能按日期浏览后在本地做标题/摘要关键词过滤（脚本的 `_filter_keywords` 做了这件事，匹配所有关键词才算命中）。

命令：

```bash
python scripts/litsearch.py biorxiv --server biorxiv --date-range 2024-01-01:2024-03-31 --limit 100 --no-proxy
python scripts/litsearch.py biorxiv --server medrxiv --date-range 2024-01-01:2024-03-31 --published --no-proxy
```

`--published` 返回的记录里带 `publishedDoi` / `publishedJournal`，用于把预印本对应到正式版（正式版优先用于引用）。

## 预印本与正式版的关系

- 检索预印本时记录 `externalIds.DOI`（预印本 DOI，通常 `10.1101/...`）与 `publishedDoi`（正式版 DOI）
- 引用时应优先使用**正式版** DOI；本 skill 只做标注与关联，不替你决定引用哪一版
