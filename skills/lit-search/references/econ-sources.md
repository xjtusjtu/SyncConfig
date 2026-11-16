# 经济学文献：可用渠道与当前不可用渠道

实现：`scripts/econ_sources.py`、`scripts/nber.py`；CLI：`litsearch.py econ` / `nber` / `ssrn`。

## 当前状态一览（2026-11-13 实测）

| 渠道 | 状态 | 入口 | 说明 |
|---|---|---|---|
| **Crossref + ISSN 过滤** | ✅ 可用 | `econ --sources crossref` | 经济/管理期刊正式论文；实测返回相关论文 |
| **NBER 官方 API** | ✅ 可用 | `nber` | 免 key JSON API，3.4 万条工作论文；细节见 `references/nber.md` |
| **SSRN（经 OpenAlex 索引）** | ✅ 可用 | `ssrn`（OpenAlex source `S4210172589`，112 万条） | SSRN 站点不可直抓，但条目已被 OpenAlex 收录 |
| **SSRN（经 Crossref 前缀）** | ✅ 可用 | `ssrn --sources crossref`（前缀 `10.2139`，6.2 万条命中） | Crossref 有 SSRN 的 DOI 与题录（无摘要） |
| **OpenAlex `type:preprint`** | ✅ 可用 | `openalex --filter "type:preprint"` | 覆盖大量工作论文与预印本 |
| **Crossref `type:posted-content`** | ✅ 可用 | `crossref --filter type:posted-content` | 预印本型条目（accepted manuscript） |
| **RePEc / IDEAS 站点直抓** | ❌ 不可用 | `econ --sources ideas` | 已改版为前端渲染，纯 HTTP 只拿到 JS 外壳页 |
| **SSRN 站点直抓** | ❌ 不可用 | `econ --sources ssrn` | Cloudflare 人机校验（`Cf-Mitigated: challenge`） |

**要点**：SSRN/IDEAS **站点直抓**不可用，但 SSRN **内容**可从 OpenAlex 与 Crossref 拿到——经济学工作论文检索是可行的，只是不能走 SSRN 官网。

## 稳定层用法

```bash
# 经济/管理期刊正式论文（ISSN 种子表内置在 econ_sources.ISSN_SEEDS）
python scripts/litsearch.py econ --query "advertising intensity firm performance" \
    --sources crossref --limit 30 --no-proxy

# NBER 工作论文
python scripts/litsearch.py nber --query "advertising firm performance" --limit 20 --no-proxy
python scripts/litsearch.py nber --query "minimum wage" --program "Labor Studies" --no-proxy

# SSRN 工作论文（OpenAlex + Crossref 双路，按 DOI 去重）
python scripts/litsearch.py ssrn --query "advertising firm performance" --limit 20 --no-proxy

# 其它工作论文
python scripts/litsearch.py openalex --filter "type:preprint" --query "firm performance" \
    --sort cited_by_count:desc --limit 50 --no-proxy
```

ISSN 种子表覆盖 *Econometrica*、*AER*、*JPE*、*QJE*、*REStud*、*Econometric Journal*、*Journal of Econometrics*、*Management Science*、*SMJ*、*Organization Science*、*MISQ*、*ISR*、*Journal of Marketing*、*Marketing Science*、*JFE*、*RFS* 等 30 余种。扩充时改 `scripts/econ_sources.py` 的 `ISSN_SEEDS`；OpenAlex source id 与更多 ISSN 见 `references/journal-identifiers.md`。

## 站点直抓为何不可用（排查记录）

### 代理与连接

- 直连：IDEAS 返回 200 但只有 JS 外壳（无 `RePEc:`、无 `<dt>`）；SSRN 连接超时。
- 经 `socks5://127.0.0.1:10809`：IDEAS 仍为 JS 外壳；SSRN 在 requests/urllib3 下 TLS 握手被对端中断（`Connection aborted` / `OSError(0)`），用裸 socket + `ssl.create_default_context()` 握手可成功，但 HTTP 返回 **403 Cloudflare 人机校验页**（`Cf-Mitigated: challenge`，含 `challenges.cloudflare.com` CSP），即便伪装完整浏览器 UA 与 `sec-ch-ua` 头仍是挑战页，页面内 `abstract_id=` 出现 0 次。
- 结论：SSRN 是**反爬策略**（边缘节点按 TLS/HTTP 指纹拦截），不是网络或代理配置问题。

### 站点结构

- IDEAS 搜索表单已改为 POST `/cgi-bin/htsearch2` + 前端 JS 加载结果（页面含 `site-overlay`、`loadDoc()` XHR），旧的 `<dt>/<dd>` 服务端渲染结构不存在；GET/POST 均只拿到外壳页。

### 脚本行为

- 抓取失败只打印告警，**不抛异常中断批量任务**，并在记录上标 `_meta.fragile = true`；
- SSRN 连接失败会提示「边缘节点在 TLS 阶段重置非浏览器连接，需浏览器自动化访问」；
- IDEAS 检出 JS 外壳时提示改用 Crossref / OpenAlex / NBER；
- 不会静默返回空结果冒充「没有文献」。

## 待解决（后续再议）

| 方案 | 适用渠道 | 说明 |
|---|---|---|
| 浏览器自动化抓取 | SSRN、IDEAS 站点 | 按仓库 AGENTS.md 的网页降级策略：`playwright-cli` + `--persistent`（复用登录态），必要时 `--headed` 人工过 Cloudflare 验证；IDEAS 的 JS 外壳也必须靠浏览器渲染才有结果 |
| 找官方 API 替代 | IDEAS | IDEAS/RePEc 无公开 API；可考虑 OpenAlex/Crossref 收录 + DOI 回查补全 |

在上述方案落地前，**经济学检索的默认路径 = NBER API + Crossref(ISSN) + SSRN(OpenAlex/Crossref 索引) + OpenAlex(type:preprint)**。

## 记录字段

站点直抓记录通常只有标题与链接，缺作者/年份/摘要——这是抓取源的固有限制，**不要替它补全**。需要完整元数据时用 DOI 回查 Crossref 或 OpenAlex。
