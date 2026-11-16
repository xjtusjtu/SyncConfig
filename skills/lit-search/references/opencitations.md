# OpenCitations 通道（引用图谱，免 key）

OpenCitations Index API v2 提供**可查询的引用图谱**，正好补上 Crossref 没有的能力（见 `references/crossref.md` 的对照表）。

- 端点：`https://api.opencitations.net/index/v2`
- 认证：**不需要 key**（实测 2026-11-13 直连可用）
- 实现：`scripts/opencitations.py`，CLI：`python scripts/litsearch.py opencitations ...`

## 两个方向

| 方向 | 接口 | 含义 |
|------|------|------|
| `citations` | `/citations/{id}` | **谁引用了它**（前向引用） |
| `references` | `/references/{id}` | **它引用了谁**（后向引用） |

标识写法：`doi:10.1038/nature12373`（也可传 `pmid:`、`openalex:`、`omid:` 等前缀；不带前缀时默认按 DOI 处理）。

**共被引相似**（`similar`）、`metadata`、`author` 端点在公开 API 上实测返回 **404**，未开放；主题相近的文献改用 OpenAlex 的 `openalex --related`（`related_works` 字段）。

## 为什么这个通道值得单列

1. **交叉标识**：每条记录同时带 `doi` / `pmid` / `openalex` / `omid`，可以和 S2、PubMed、OpenAlex 的结果直接对齐去重；
2. **带时间**：`creation` 给出引用建立时间，`timespan` 给出时间跨度，可做"引用年份分布"；
3. **区分二手引用**：`journal_sc` / `author_sc` 标出是否来自二级引用（作者自引、期刊二次引用），可用于剔除噪声；
4. **不烧额度**：不需要 key，与 S2/Asta 的额度互不影响。

## 命令

```bash
# 谁引用了这篇
python scripts/litsearch.py opencitations --doi 10.1038/nature12373 --direction citations --limit 20 --no-proxy

# 这篇引用了谁
python scripts/litsearch.py opencitations --doi 10.1038/nature12373 --direction references --limit 20 --no-proxy

# 主题相近（OpenCitations 无 similar 端点，用 OpenAlex）
python scripts/litsearch.py openalex --doi 10.1038/nature12373 --related --limit 20 --no-proxy

# 落盘后与其它通道合并去重
python scripts/litsearch.py opencitations --doi 10.1038/nature12373 --direction citations --out cites.jsonl
python scripts/litsearch.py dedup cites.jsonl s2.jsonl --out merged.jsonl
```

## 输出结构

```json
{
  "paperId": "10.1103/physreva.87.032118",
  "externalIds": {"DOI": "10.1103/physreva.87.032118", "OpenAlex": "W2963941855"},
  "relation": {
    "direction": "references",
    "counterpart": {"DOI": "10.1038/nature12373", "PMID": "23903748", "OpenAlex": "W2159974629"},
    "oci": "06120344846-06101350332",
    "creation": "2013-07-31",
    "journal_sc": "no",
    "author_sc": "no"
  },
  "_meta": {"source": "opencitations"}
}
```

OpenCitations 只给标识与关系，**不给标题、摘要、期刊名**；需要题录时用 `externalIds.DOI` 回查 Crossref 或 OpenAlex。

## 实测（2026-11-13）

- `10.1038/nature12373`（Nature 量子纳米温度计）：`citations` 返回 1806 条，`references` 返回 30 条，`creation` 与 DOI 一一对应；
- `similar` / `metadata` / `author` 端点实测 404（公开 API 未开放），脚本对 `similar` 直接给出改用 OpenAlex 的提示；
- `references` 返回的每条 `counterpart` 都是目标文献本身（这是该接口的字段约定：一边是提问对象，一边是对端）；
- 记录里同时出现 `openalex:W…` 与 `pmid:…`，可直接与 OpenAlex/PubMed 通道对齐；
- 未配 key 时无需任何鉴权头；若出现 429，按本 skill 的硬规则**立即停止**。
- **Crossref Event Data（Scholix）不可用**：`api.eventdata.crossref.org` 在本机网络下连接超时（WinError 10060），暂不作为通道；需要时改用 OpenCitations。
