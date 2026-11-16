# 期刊标识表：OpenAlex source id 与 Crossref ISSN

用途：按刊物限定检索（`openalex --source <key>`、`crossref --journal <issn>`），或按 ISSN 过滤（`crossref --filter issn:...`）。

## 使用注意

- **OpenAlex source id 不可猜测**：新增刊物前先用 `GET https://api.openalex.org/sources?search=<刊名>` 查 id。
- 本表 2026-11-13 实测校验了两个关键 id：
  - `S4210172589` = **SSRN Electronic Journal**（ISSN 1556-5068，112 万条作品）
  - `S2809516038` = **National Bureau of Economic Research**（3.4 万条）
  - 注意：网上流传的 `S4210174556` 并非 NBER（实测为 "Metal Working and Material Science"），**别直接抄**。
- Crossref 的 ISSN 是权威且稳定的，优先用 ISSN 过滤；OpenAlex id 适合需要主题/机构维度时使用。

## 脚本内置别名

`scripts/openalex.py` 的 `SOURCE_IDS` 提供以下别名，可直接 `--source` 使用：

| 别名 | OpenAlex id | 刊物 |
|---|---|---|
| `ssrn` | S4210172589 | SSRN Electronic Journal |
| `nber` | S2809516038 | NBER Working Papers |
| `aer` | S23254222 | American Economic Review |
| `econometrica` | S95464858 | Econometrica |
| `qje` | S203860005 | Quarterly Journal of Economics |
| `jpe` | S95323914 | Journal of Political Economy |
| `restud` | S88935262 | Review of Economic Studies |
| `joe` | S127742747 | Journal of Econometrics |
| `management-science` | S33323087 | Management Science |
| `smj` | S102949365 | Strategic Management Journal |
| `org-science` | S206124708 | Organization Science |
| `misq` | S57293258 | MIS Quarterly |
| `isr` | S202812398 | Information Systems Research |
| `jmr` | S119950638 | Journal of Marketing Research |
| `journal-of-marketing` | S142990027 | Journal of Marketing |
| `marketing-science` | S163534328 | Marketing Science |
| `jfe` | S149240962 | Journal of Financial Economics |
| `rfs` | S170137484 | Review of Financial Studies |

## 常用期刊 ISSN（Crossref）

| 领域 | 刊物 | ISSN |
|---|---|---|
| 经济学综合 | American Economic Review | 0002-8282 |
| | Econometrica | 0012-9682 |
| | Quarterly Journal of Economics | 0033-5533 |
| | Journal of Political Economy | 0022-3808 |
| | Review of Economic Studies | 0034-6527 |
| | Economic Journal | 0013-0133 |
| | Journal of Econometrics | 0304-4076 |
| | RAND Journal of Economics | 0741-6261 |
| | Review of Economics and Statistics | 0034-6535 |
| | Journal of Public Economics | 0047-2727 |
| | Journal of Labor Economics | 0734-306X |
| | Journal of Human Resources | 0022-166X |
| | Econometrics Journal | 1368-422X |
| | Journal of Business & Economic Statistics | 0735-0015 |
| AEA | AER: Insights | 2640-205X |
| | AEJ: Applied / Economic Policy / Macro / Micro | 1945-7782 / 1945-7731 / 1945-7707 / 1945-7669 |
| 金融 | Journal of Finance | 0022-1082 |
| | Journal of Financial Economics | 0304-405X |
| | Review of Financial Studies | 0893-9454 |
| 管理 | Management Science | 0025-1909 |
| | Strategic Management Journal | 0143-2095 |
| | Organization Science | 1047-7039 |
| | Journal of International Business Studies | 0022-1360 |
| 营销 | Journal of Marketing | 0022-1529 |
| | Journal of Marketing Research | 0022-2437 |
| | Marketing Science | 0147-2096 |
| 信息系统 | MIS Quarterly | 0276-7783 |
| | Information Systems Research | 1047-9037 |
| 会计 | The Accounting Review | 0001-4826 |
| | Journal of Accounting Research | 0021-8456 |

## 用法

```bash
# 在 AER 内检索
python scripts/litsearch.py openalex --source aer --query "auction mechanism" --limit 20 --no-proxy
python scripts/litsearch.py crossref --journal 0002-8282 --query "auction mechanism" --rows 20 --no-proxy

# 多刊合并（OpenAlex 的 source 过滤支持 | 分隔）
python scripts/litsearch.py openalex --filter "primary_location.source.id:S23254222|S95464858|S203860005" \
    --query "network formation" --limit 25 --no-proxy
```
