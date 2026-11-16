#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lit-search CLI —— 批量文献检索、水合、引文扩展、筛选与导出。

子命令：
  check      检查 API key 与配置（可选 --live 发一个最小请求）
  search     bulk 检索（支持多 query、断点续传、JSONL 落盘）
  hydrate    用 batch 补齐元数据/摘要/tldr
  expand     引文滚雪球（citations / references，BFS）
  dedup      去重 + 规则筛选，输出 CSV / JSONL
  export     导出 Markdown / CSV / JSONL / BibTeX / RIS / APA / GB-T 7714
  datasets   列出 Semantic Scholar Datasets 与下载链接
  snippets   片段检索（S2 snippet search）
  crossref   Crossref 检索（免 key，支持 --journal ISSN / --prefix 前缀）
  match      按标题精确匹配（S2 match 接口）
  pubmed     PubMed 检索（NCBI E-utilities）
  pmc        PMC 全文（JATS XML / 分节 / BioC）
  idconv     ID 互转 PMID / PMCID / DOI / MID
  openalex   OpenAlex works 检索（--source 限定来源；--citations/--references 引文边）
  arxiv      arXiv 预印本检索（--strict-category 本地复核分类）
  biorxiv    bioRxiv / medRxiv 日期浏览
  unpaywall  Unpaywall OA 状态与 PDF 链接（下载需批准）
  core       CORE 全文检索（下载需批准）
  nber       NBER 工作论文检索（免费 JSON API，无需 key）
  ssrn       SSRN 工作论文（经 OpenAlex + Crossref 索引）
  econ       经济学期刊（Crossref + ISSN 过滤；SSRN/IDEAS 站点直抓不可用）

示例：
  python litsearch.py check
  python litsearch.py search --query "advertising sales" --year 2015- --out out/
  python litsearch.py search --queries-file queries.json --max-results 3000 --out out/
  python litsearch.py expand --in out/papers.jsonl --direction citations --depth 1 --out out/cites.jsonl
  python litsearch.py dedup --in out/cites.jsonl --year-min 2015 --out out/screened.csv
  python litsearch.py export --in out/cites.jsonl --format bib --out out/refs.bib
  python litsearch.py pubmed --query '"advertising"[Title/Abstract]' --limit 20 --out out/pm.jsonl
  python litsearch.py openalex --query "advertising" --limit 50 --out out/oa.jsonl

退出码：0 成功；1 一般错误；2 认证错误；3 网络/依赖/限流错误。
"""

from __future__ import print_function

import argparse
import json
import os
import sys
import time
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import s2api  # noqa: E402
import crossref as crossref_mod  # noqa: E402


# --------------------------------------------------------------------------
# 通用
# --------------------------------------------------------------------------

def setup_io():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


def now_iso():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def resolve_fields(value):
    if not value:
        return None
    preset = s2api.FIELD_PRESETS.get(value)
    return preset if preset else value


def make_client(args):
    return s2api.S2Client(
        api_key=args.api_key,
        rps=args.rps,
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        max_retries=getattr(args, "max_retries", 8),
        retry_429=getattr(args, "retry_429", False),
        verbose=(not args.quiet),
    )


def load_state(path):
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    return {"run_id": None, "created_at": None, "queries": {}}


def save_state(path, state):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def ensure_dir(path):
    if path and not os.path.isdir(path):
        os.makedirs(path)


# --------------------------------------------------------------------------
# query 计划
# --------------------------------------------------------------------------

def build_query_plan(args):
    """把 --query / --queries-file 统一成 [{'name','query',...filters}]。"""
    plan = []
    for i, text in enumerate(args.query or [], 1):
        plan.append({"name": "q%d" % i, "query": text})

    if args.queries_file:
        with open(args.queries_file, "r", encoding="utf-8-sig") as fh:
            raw = json.load(fh)
        if not isinstance(raw, list):
            raise ValueError("queries-file 必须是 JSON 数组")
        for i, item in enumerate(raw, 1):
            if isinstance(item, str):
                plan.append({"name": "f%d" % i, "query": item})
            elif isinstance(item, dict):
                if not item.get("query"):
                    raise ValueError("第 %d 项缺少 query 字段" % i)
                entry = dict(item)
                entry.setdefault("name", "f%d" % i)
                plan.append(entry)
            else:
                raise ValueError("第 %d 项类型不支持（应为字符串或对象）" % i)

    if not plan:
        raise ValueError("没有 query：用 --query 或 --queries-file 指定")

    for entry in plan:
        # 单 query 覆盖 CLI 默认值
        for key in ("year", "publication_date", "venue", "fields_of_study",
                    "min_citations", "pub_types", "open_access"):
            if key in entry and entry[key] not in (None, "", []):
                continue
            if getattr(args, key, None) not in (None, "", []):
                entry[key] = getattr(args, key)
    return plan


def plan_filters(entry):
    return {
        "year": entry.get("year"),
        "publication_date": entry.get("publication_date"),
        "venue": entry.get("venue"),
        "fields_of_study": entry.get("fields_of_study"),
        "min_citations": entry.get("min_citations"),
        "pub_types": entry.get("pub_types"),
        "open_access": entry.get("open_access"),
    }


# --------------------------------------------------------------------------
# 子命令
# --------------------------------------------------------------------------

def cmd_check(args):
    status = s2api.key_status()
    print("S2 API key: %s" % ("已配置" if status["present"] else "未找到"))
    if status["present"]:
        print("  来源: %s" % status["source"])
        print("  掩码: %s" % status["masked"])
    else:
        print("  期望位置: 环境变量 S2_API_KEY，或 .env（<skill_dir>/.env → "
              "~/.config/lit-search/.env → 当前目录及上级）")

    print("\n其它渠道凭据：")
    for name, note in (
        ("ASTA_API_KEY", "Asta MCP（agent 侧配置）"),
        ("OPENALEX_API_KEY", "OpenAlex"),
        ("NCBI_API_KEY", "PubMed/PMC"),
        ("NCBI_EMAIL", "NCBI 礼貌池"),
        ("UNPAYWALL_EMAIL", "Unpaywall"),
        ("OPENALEX_MAILTO", "OpenAlex 礼貌池"),
    ):
        value = s2api.resolve_key_from_env((name,))
        if value:
            if "EMAIL" in name or "MAILTO" in name:
                print("  %-18s 已配置（不显示）        %s" % (name, note))
            else:
                print("  %-18s 已配置（掩码 %s）  %s"
                      % (name, s2api._mask(value), note))
        else:
            print("  %-18s 未配置            %s" % (name, note))

    core_keys = s2api.resolve_prefixed_keys("CORE_API_KEY")
    if core_keys:
        if len(core_keys) == 1:
            print("  %-18s 已配置（掩码 %s）  %s"
                  % ("CORE_API_KEY", s2api._mask(core_keys[0]), "CORE 全文"))
        else:
            print("  %-18s 已配置 %d 个（轮流使用） %s"
                  % ("CORE_API_KEY*", len(core_keys), "CORE 全文"))
    else:
        print("  %-18s 未配置            %s" % ("CORE_API_KEY*", "CORE 全文"))

    print("\nAsta MCP: 由 agent 侧配置，不在本脚本检查范围（见 references/asta-mcp.md）")

    if args.live:
        if not status["present"]:
            print("\n--live 需要一个有效 key。")
            return 2
        client = make_client(args)
        try:
            payload = client._request("GET", s2api.GRAPH + "/paper/search", params={
                "query": "semantic scholar", "fields": "title", "limit": 1,
            })
            print("\n接口连通：OK，返回 %d 条样例。" % len(payload.get("data") or []))
        except s2api.S2AuthError as exc:
            print("\n接口连通：认证失败 —— %s" % exc)
            return 2
        except s2api.S2Error as exc:
            print("\n接口连通：失败 —— %s" % exc)
            return 3
    return 0


def cmd_search(args):
    ensure_dir(args.out)
    papers_path = os.path.join(args.out, "papers.jsonl")
    state_path = os.path.join(args.out, "state.json")
    manifest_path = os.path.join(args.out, "manifest.json")

    plan = build_query_plan(args)
    fields = resolve_fields(args.fields) or s2api.FIELD_PRESETS["standard"]

    if args.plan:
        print(json.dumps({
            "queries": plan,
            "fields": fields,
            "sort": args.sort,
            "max_results_per_query": args.max_results,
            "max_results_semantics": "每 query 累计上限；翻页由 token 控制",
            "estimated_calls": "未知（需按 total 估算），单页通常 1000 条",
        }, ensure_ascii=False, indent=2))
        return 0

    state = load_state(state_path)
    if args.restart or not state.get("run_id"):
        if args.restart and os.path.isfile(papers_path):
            bak = papers_path + ".bak-" + time.strftime("%Y%m%d-%H%M%S")
            os.replace(papers_path, bak)
            print("[restart] 旧结果已改名：%s" % bak, file=sys.stderr)
        state = {"run_id": now_iso(), "created_at": now_iso(), "queries": {}}
    save_state(state_path, state)

    client = make_client(args)
    if not client.api_key:
        if not args.anonymous:
            print("未找到 S2_API_KEY。先在 .env 写 S2_API_KEY=... 或设置环境变量；"
                  "或加 --anonymous 走匿名共享池。", file=sys.stderr)
            return 2
        print("[warn] 无 API key，使用匿名共享池（速率低、可能 429）。", file=sys.stderr)

    started = time.time()
    summary = []

    for entry in plan:
        name = entry["name"]
        qstate = state["queries"].setdefault(name, {"token": None, "fetched": 0, "done": False})
        if qstate.get("done") and not args.restart:
            print("[skip] %s 已完成（%d 条）" % (name, qstate["fetched"]), file=sys.stderr)
            summary.append({"name": name, "query": entry["query"],
                            "fetched": qstate["fetched"], "status": "skipped"})
            continue

        remaining = max(0, int(args.max_results) - int(qstate.get("fetched") or 0))
        if remaining <= 0:
            qstate["done"] = True
            save_state(state_path, state)
            continue

        print("[query] %s: %s" % (name, entry["query"]), file=sys.stderr)

        run_id = state["run_id"]
        page_meta = {"query": name, "query_text": entry["query"], "run_id": run_id}

        def on_page(papers, next_token, total, fetched_this_call, _name=name,
                    _entry=entry, _meta=page_meta, _q=qstate):
            rows = []
            for paper in papers:
                row = dict(paper)
                row["_meta"] = dict(_meta)
                row["_meta"]["retrieved_at"] = now_iso()
                rows.append(row)
            s2api.write_jsonl(papers_path, rows, append=True)
            _q["token"] = next_token
            _q["fetched"] = int(_q.get("fetched") or 0) + len(rows)
            _q["total"] = total
            _q["done"] = (next_token is None) or (_q["fetched"] >= int(args.max_results))
            save_state(state_path, state)
            print("  +%d（累计 %d%s）" % (
                len(rows), _q["fetched"],
                "" if total is None else " / 约 %d" % total,
            ), file=sys.stderr)

        try:
            for _ in client.bulk_search(
                entry["query"],
                fields=fields,
                sort=entry.get("sort") or args.sort,
                max_results=remaining,
                start_token=qstate.get("token"),
                on_page=on_page,
                **plan_filters(entry)
            ):
                pass
        except s2api.S2AuthError as exc:
            print("认证失败：%s" % exc, file=sys.stderr)
            return 2
        except s2api.S2RateLimitError as exc:
            # 策略：429 立即终止整次运行，不再处理后续 query
            print("速率限制，已停止（未处理的后续 query 不再执行）：%s" % exc, file=sys.stderr)
            print("state 已保存，稍后重跑同一条命令会从断点续传。", file=sys.stderr)
            return 3
        except s2api.S2Error as exc:
            print("检索失败（%s）：%s" % (name, exc), file=sys.stderr)
            summary.append({"name": name, "query": entry["query"],
                            "fetched": qstate["fetched"], "status": "error"})
            if args.fail_fast:
                return 3
            continue

        summary.append({"name": name, "query": entry["query"],
                        "fetched": qstate["fetched"],
                        "status": "done" if qstate.get("done") else "partial"})

    elapsed = round(time.time() - started, 1)
    manifest = {
        "run_id": state["run_id"],
        "generated_at": now_iso(),
        "elapsed_sec": elapsed,
        "fields": fields,
        "sort": args.sort,
        "max_results_per_query": args.max_results,
        "queries": summary,
        "output": os.path.abspath(papers_path),
        "rate_limit_rps": client.rps,
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    total = sum(s["fetched"] for s in summary)
    print("\n完成：%d 条（原始记录，可能含跨 query 重复）→ %s" % (total, papers_path))
    print("清单：%s" % manifest_path)
    return 0


def cmd_hydrate(args):
    rows = s2api.read_jsonl(args.input)
    ids, key_of = [], {}
    for row in rows:
        pid = row.get("paperId")
        if not pid and s2api.paper_doi(row):
            pid = "DOI:" + s2api.paper_doi(row)
        if pid and pid not in key_of:
            key_of[pid] = row.get("paperId") or pid
            ids.append(pid)

    if not ids:
        print("输入里没有可用 ID。", file=sys.stderr)
        return 1

    client = make_client(args)
    fields = resolve_fields(args.fields) or s2api.FIELD_PRESETS["detail"]
    print("水合 %d 个唯一 ID，fields=%s" % (len(ids), fields), file=sys.stderr)

    out_rows = []
    try:
        for batch in s2api.chunks(ids, 500):
            data = client.batch_papers(batch, fields=fields)
            for pid, paper in client.align_batch(batch, data):
                if paper:
                    paper["_meta"] = {"source": "hydrate", "input_id": pid,
                                      "retrieved_at": now_iso()}
                    out_rows.append(paper)
                else:
                    print("  [unresolved] %s" % pid, file=sys.stderr)
    except s2api.S2AuthError as exc:
        print("认证失败：%s" % exc, file=sys.stderr)
        return 2
    except s2api.S2Error as exc:
        print("水合失败：%s" % exc, file=sys.stderr)
        return 3

    s2api.write_jsonl(args.out, out_rows, append=False)
    print("完成：%d/%d 个 ID 解析成功 → %s" % (len(out_rows), len(ids), args.out))
    return 0


def _edge_paper(item, direction):
    if direction == "citations":
        return (item or {}).get("citingPaper") or {}
    return (item or {}).get("citedPaper") or {}


def cmd_expand(args):
    seeds = s2api.read_jsonl(args.input)
    seed_ids = []
    for row in seeds:
        pid = row.get("paperId")
        if pid and pid not in seed_ids:
            seed_ids.append(pid)
    if not seed_ids:
        print("输入里没有 paperId。", file=sys.stderr)
        return 1

    client = make_client(args)
    if not client.api_key:
        if not args.anonymous:
            print("未找到 S2_API_KEY。先在 .env 写 S2_API_KEY=... 或设置环境变量；"
                  "或加 --anonymous 走匿名共享池。", file=sys.stderr)
            return 2
        print("[warn] 无 API key，使用匿名共享池（速率低、可能 429）。", file=sys.stderr)

    fields = resolve_fields(args.fields) or "title,year,venue,authors,externalIds,citationCount,abstract"
    directions = ["citations", "references"] if args.direction == "both" else [args.direction]

    seen = set(seed_ids)
    frontier = seed_ids[:args.max_frontier]
    written = 0

    print("种子 %d 篇；方向=%s；深度=%d；每个种子上限 %d"
          % (len(seed_ids), ",".join(directions), args.depth, args.max_per_seed), file=sys.stderr)

    for depth in range(1, args.depth + 1):
        next_frontier = []
        for pid in frontier:
            for direction in directions:
                if written >= args.max_total:
                    break
                try:
                    if direction == "citations":
                        items = client.citations(pid, fields=fields, max_results=args.max_per_seed)
                    else:
                        items = client.references(pid, fields=fields, max_results=args.max_per_seed)
                except s2api.S2AuthError as exc:
                    print("认证失败：%s" % exc, file=sys.stderr)
                    return 2
                except s2api.S2RateLimitError as exc:
                    print("速率限制，已停止（不再扩展剩余种子）：%s" % exc, file=sys.stderr)
                    return 3
                except s2api.S2Error as exc:
                    print("  [skip] %s %s：%s" % (pid, direction, exc), file=sys.stderr)
                    continue

                rows = []
                for item in items:
                    paper = _edge_paper(item, direction)
                    new_pid = paper.get("paperId")
                    if not new_pid or new_pid in seen:
                        continue
                    seen.add(new_pid)
                    paper["_meta"] = {
                        "source": "expand",
                        "relation": direction,
                        "seed": pid,
                        "depth": depth,
                        "retrieved_at": now_iso(),
                    }
                    rows.append(paper)
                    next_frontier.append(new_pid)
                    if written + len(rows) >= args.max_total:
                        break

                if rows:
                    s2api.write_jsonl(args.out, rows, append=True)
                    written += len(rows)
                print("  [d%d] %s %s：新增 %d" % (depth, pid[:12], direction, len(rows)),
                      file=sys.stderr)

            if written >= args.max_total:
                break

        frontier = next_frontier[:args.max_frontier]
        if not frontier:
            break

    print("\n完成：新增 %d 条 → %s" % (written, args.out))
    return 0


def _text_of(row):
    return ((row.get("title") or "") + " " + (row.get("abstract") or "")).lower()


def _has_abstract(row):
    return len((row.get("abstract") or "").strip()) > 50


def _screen(row, args):
    year = row.get("year")
    if args.year_min is not None and (year is None or year < args.year_min):
        return False
    if args.year_max is not None and (year is None or year > args.year_max):
        return False
    if args.min_citations is not None and (row.get("citationCount") or 0) < args.min_citations:
        return False
    if args.venue_regex:
        import re
        if not re.search(args.venue_regex, row.get("venue") or "", re.I):
            return False
    if args.require_abstract and not (row.get("abstract") or "").strip():
        return False
    if args.require_doi and not s2api.paper_doi(row):
        return False

    # 词项约束只在有摘要的记录上判定；无摘要记录无法核验，默认保留
    require = getattr(args, "require_term", None) or []
    exclude = getattr(args, "exclude_term", None) or []
    if require or exclude:
        if _has_abstract(row):
            text = _text_of(row)
            if require and not all(t.lower() in text for t in require):
                return False
            if exclude and any(t.lower() in text for t in exclude):
                return False
    return True


def cmd_dedup(args):
    rows = s2api.read_jsonl(args.input)
    raw = len(rows)
    kept = [r for r in rows if _screen(r, args)]
    screened_out = raw - len(kept)

    require = getattr(args, "require_term", None) or []
    exclude = getattr(args, "exclude_term", None) or []
    unverifiable = 0
    if require or exclude:
        unverifiable = sum(1 for r in kept if not _has_abstract(r))

    unique, dup = s2api.dedup(kept)
    if args.sort == "citations":
        unique.sort(key=lambda p: p.get("citationCount") or 0, reverse=True)
    elif args.sort == "year":
        unique.sort(key=lambda p: p.get("year") or 0, reverse=True)

    out = args.out or os.path.splitext(args.input)[0] + "_dedup.csv"
    s2api.to_csv(unique, out)
    if args.out_jsonl:
        s2api.write_jsonl(args.out_jsonl, unique)

    print("原始 %d → 规则筛除 %d → 去重 %d → 保留 %d"
          % (raw, screened_out, dup, len(unique)), file=sys.stderr)
    if require or exclude:
        print("词项约束：必含 %s；排除 %s" % (require or "—", exclude or "—"), file=sys.stderr)
        if unverifiable:
            print("注意：%d 条无摘要，词项约束无法核验（已保留）。"
                  "S2 bulk 大量记录不含摘要，这是正常的元数据缺失。"
                  % unverifiable, file=sys.stderr)
    print("输出：%s" % out)
    return 0


def _s2_batch_id(rec):
    """给 S2 batch 用的可解析 ID：paperId 优先，其次 DOI:/PMID:/ArXiv: 前缀形式。"""
    if rec.get("paperId") and not str(rec["paperId"]).startswith(("DOI:", "PMID:", "PMCID:")):
        return rec["paperId"]
    ext = rec.get("externalIds") or {}
    if ext.get("DOI"):
        return "DOI:" + ext["DOI"]
    if ext.get("PMID"):
        return "PMID:" + ext["PMID"]
    if ext.get("ArXiv"):
        return "ARXIV:" + ext["ArXiv"]
    return None


def _ensure_citation_styles(args, rows):
    """给缺 citationStyles 的记录补齐（有 S2 key 时走 batch）。"""
    missing_idx = [i for i, r in enumerate(rows)
                   if not ((r.get("citationStyles") or {}).get("bibtex") or "").strip()]
    if not missing_idx:
        return rows
    client = make_client(args)
    if not client.api_key:
        print("[warn] %d 条缺 citationStyles，且无 S2 key：改用极简 BibTeX 生成器。"
              % len(missing_idx), file=sys.stderr)
        return rows
    ids = []
    for i in missing_idx:
        sid = _s2_batch_id(rows[i])
        if sid:
            ids.append((i, sid))
    try:
        for chunk in s2api.chunks(ids, 500):
            chunk_ids = [sid for _, sid in chunk]
            data = client.batch_papers(chunk_ids, fields=s2api.FIELD_PRESETS["bibtex"])
            for (idx, sid), paper in zip(chunk, data):
                if not paper:
                    continue
                bib = ((paper.get("citationStyles") or {}).get("bibtex") or "").strip()
                if bib:
                    rows[idx].setdefault("citationStyles", {})["bibtex"] = bib
    except s2api.S2Error as exc:
        print("[warn] citationStyles 补齐失败，改用极简生成器：%s" % exc, file=sys.stderr)
    return rows


def cmd_export(args):
    if args.input.lower().endswith(".csv"):
        print("export 需要 JSONL 输入（CSV 已丢失摘要等字段）。请传 papers.jsonl。", file=sys.stderr)
        return 1
    rows = s2api.read_jsonl(args.input)

    if args.format == "jsonl":
        s2api.write_jsonl(args.out, rows)
        print("导出 %d 条 → %s" % (len(rows), args.out))
        return 0

    if args.format == "csv":
        s2api.to_csv(rows, args.out)
        print("导出 %d 条 → %s" % (len(rows), args.out))
        return 0

    if args.format == "md":
        md = s2api.to_markdown(rows, limit=args.limit, details=args.details)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(md)
        print("导出 %d 条（表格前 %d）→ %s" % (len(rows), args.limit, args.out))
        return 0

    if args.format in ("ris", "apa", "gbt", "gbt7714"):
        import formats
        try:
            text, warnings = formats.export_records(rows, args.format)
        except ValueError as exc:
            print("导出失败：%s" % exc, file=sys.stderr)
            return 1
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("导出 %d 条 → %s" % (len(rows), args.out))
        for warning in warnings:
            print("[warn] %s" % warning, file=sys.stderr)
        return 0

    if args.format == "bib":
        import formats
        rows = _ensure_citation_styles(args, rows)
        text = formats.to_bibtex(rows)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + ("\n" if text else ""))
        print("导出 %d 条 BibTeX → %s" % (len(rows), args.out))
        return 0

    print("未知格式：%s" % args.format, file=sys.stderr)
    return 1


def cmd_datasets(args):
    client = make_client(args)
    if not client.api_key:
        print("Datasets 下载链接接口需要 API key。", file=sys.stderr)

    try:
        if not args.dataset:
            payload = client.dataset_release(args.release)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        payload = client.dataset_download_links(args.release, args.dataset)
    except s2api.S2AuthError as exc:
        print("认证失败：%s" % exc, file=sys.stderr)
        return 2
    except s2api.S2Error as exc:
        print("失败：%s" % exc, file=sys.stderr)
        return 3

    files = payload.get("files") or []
    print("dataset=%s release=%s files=%d" % (args.dataset, args.release, len(files)))
    for i, item in enumerate(files, 1):
        name = item.get("name") or ("part-%d" % i)
        size = item.get("size") or "?"
        print("  %d) %s  %s bytes" % (i, name, size))
        print("     %s" % (item.get("url") or ""))

    if args.download_dir:
        ensure_dir(args.download_dir)
        import requests
        for item in files:
            url = item.get("url")
            if not url:
                continue
            name = item.get("name") or os.path.basename(url.split("?")[0])
            target = os.path.join(args.download_dir, name)
            print("下载 %s ..." % name, file=sys.stderr)
            with requests.get(url, stream=True, timeout=args.timeout) as resp:
                resp.raise_for_status()
                with open(target, "wb") as fh:
                    for chunk in resp.iter_content(1024 * 1024):
                        fh.write(chunk)
            print("  → %s" % target, file=sys.stderr)
    return 0


def cmd_snippets(args):
    client = make_client(args)
    try:
        data = client.snippet_search(args.query, limit=args.limit,
                                     fields=resolve_fields(args.fields))
    except s2api.S2AuthError as exc:
        print("认证失败：%s" % exc, file=sys.stderr)
        return 2
    except s2api.S2Error as exc:
        print("失败：%s" % exc, file=sys.stderr)
        return 3

    if args.out:
        s2api.write_jsonl(args.out, data)
        print("保存 %d 条片段 → %s" % (len(data), args.out))
        return 0

    for i, item in enumerate(data, 1):
        snippet = item.get("snippet") or {}
        paper = item.get("paper") or {}
        text = (snippet.get("text") or "").strip().replace("\n", " ")
        print("\n[%d] %s (%s)" % (i, paper.get("title") or "?", paper.get("year") or "?"))
        if paper.get("paperId"):
            print("    paperId: %s" % paper["paperId"])
        print("    %s" % text[:600])
    print("\n共 %d 条。" % len(data))
    return 0


def cmd_crossref(args):
    """Crossref 检索（无需 API key）。"""
    client = crossref_mod.CrossrefClient(
        mailto=args.mailto,
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    try:
        if args.doi:
            work = client.get_work(args.doi)
            if not work:
                print("DOI 未查到：%s" % args.doi, file=sys.stderr)
                return 1
            rec = crossref_mod.normalize(work)
            rec["_meta"]["doi_lookup"] = True
            rows = [rec]
            if args.references:
                for ref in client.references(args.doi):
                    rows.append({"reference": ref, "_meta": {"source": "crossref-reference",
                                                             "doi_lookup": True}})
        else:
            if args.journal:
                items, total = client.journal_works(
                    args.journal, query=args.query or args.title, rows=args.rows,
                    filters=args.filter, sort=args.sort, order=args.order,
                    select=args.select)
            elif args.prefix:
                items, total = client.prefix_works(
                    args.prefix, query=args.query or args.title, rows=args.rows,
                    filters=args.filter, sort=args.sort, order=args.order,
                    select=args.select)
            else:
                items, total = client.search(
                    query=args.query, title=args.title, author=args.author,
                    rows=args.rows, filters=args.filter, sort=args.sort,
                    order=args.order, select=args.select,
                )
            rows = [crossref_mod.normalize(x) for x in items]
            print("Crossref 命中约 %s 条，返回 %d 条" % (total, len(rows)), file=sys.stderr)
    except crossref_mod.CrossrefRateLimitError as exc:
        print("Crossref 限流，已停止：%s" % exc, file=sys.stderr)
        return 3
    except crossref_mod.CrossrefError as exc:
        print("Crossref 失败：%s" % exc, file=sys.stderr)
        return 3

    if args.out:
        s2api.write_jsonl(args.out, rows, append=False)
        print("保存 %d 条 → %s" % (len(rows), args.out), file=sys.stderr)
    else:
        for rec in rows[:20]:
            if "reference" in rec:
                r = rec["reference"]
                print("- %s (%s) %s" % (r.get("title") or "(无标题)", r.get("year") or "?", r.get("doi") or ""))
            else:
                print("- %s (%s) %s | %s | cites=%s"
                      % (rec.get("title") or "?", rec.get("year") or "?",
                         rec.get("venue") or "", rec.get("externalIds", {}).get("DOI") or "",
                         rec.get("citationCount")))
    print("共 %d 条。" % len(rows), file=sys.stderr)
    return 0


# --------------------------------------------------------------------------
# 其它数据源（PubMed / PMC / OpenAlex / 预印本 / OA / 经济学）
# --------------------------------------------------------------------------

def parse_date_range(text):
    """'2020-01-01:2024-12-31' 或 '2020:2024' → (start, end)。"""
    if not text:
        return None
    if ":" in text:
        start, end = text.split(":", 1)
    else:
        start, end = text, text
    return (start.strip() or None, end.strip() or None)


def add_net(parser):
    """非 S2 渠道共用的网络参数。"""
    parser.add_argument("--timeout", type=int, default=60, help="单请求超时秒数")
    parser.add_argument("--proxy", help="显式代理，如 http://127.0.0.1:7890")
    parser.add_argument("--no-proxy", action="store_true",
                        help="忽略环境/系统代理（Windows 注册表代理常导致 ProxyError）")
    parser.add_argument("--quiet", action="store_true", help="不打印进度")


def _emit_rows(rows, out=None, show=20):
    if out:
        s2api.write_jsonl(out, rows, append=False)
        print("保存 %d 条 → %s" % (len(rows), out), file=sys.stderr)
    for rec in rows[:show]:
        if "reference" in rec:
            r = rec["reference"]
            print("- %s (%s) %s" % (r.get("title") or "(无标题)", r.get("year") or "?",
                                    r.get("doi") or ""))
        else:
            ext = rec.get("externalIds") or {}
            title = rec.get("title") or ""
            if not title:
                title = ext.get("DOI") or ext.get("OpenAlex") or rec.get("paperId") or "?"
            print("- %s (%s) %s | %s" % (
                title, rec.get("year") or "?",
                rec.get("venue") or "",
                ext.get("DOI") or ext.get("PMID") or ext.get("ArXiv") or rec.get("paperId") or ""))
    print("共 %d 条。" % len(rows), file=sys.stderr)


def cmd_pubmed(args):
    """PubMed 检索（NCBI E-utilities）。"""
    import ncbi
    client = ncbi.NCBIClient(
        email=args.email,
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    rows = []
    for query in (args.query or []):
        rows.extend(client.search(
            query,
            retmax=args.limit,
            sort=args.sort,
            date_range=parse_date_range(args.date_range),
            pub_types=args.pub_type,
        ))
    _emit_rows(rows, args.out)
    return 0


def cmd_pmc(args):
    """PMC 全文：JATS XML / 分节文本 / BioC。"""
    import ncbi
    client = ncbi.NCBIClient(
        email=args.email,
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    pmcid = args.pmcid
    if not pmcid and args.pmid:
        links = client.pmc_ids(args.pmid)
        if not links:
            print("该 PMID 没有 PMC 全文（可能未收录于 PMC）。", file=sys.stderr)
            return 1
        pmcid = links[0]
        print("PMID %s → %s" % (args.pmid, pmcid), file=sys.stderr)

    if args.bioc:
        payload = client.bioc(pmcid, fmt="json")
        text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, indent=2)
    elif args.sections:
        sections = client.pmc_sections(pmcid)
        text = "\n\n".join("## %s\n%s" % (k, v) for k, v in sections.items())
    else:
        text = client.pmc_fulltext(pmcid)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("全文已保存 → %s（%d 字符）" % (args.out, len(text)), file=sys.stderr)
    else:
        print(text[:20000])
    return 0


def cmd_idconv(args):
    """ID 互转：PMID ↔ PMCID ↔ DOI ↔ MID。"""
    import ncbi
    client = ncbi.NCBIClient(
        email=args.email,
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    ids = []
    for item in (args.ids or []):
        ids.extend([x.strip() for x in item.split(",") if x.strip()])
    if args.input:
        for row in s2api.read_jsonl(args.input):
            ext = row.get("externalIds") or {}
            for key in ("PMID", "PMCID", "DOI"):
                if ext.get(key):
                    ids.append(ext[key])
    if not ids:
        print("未提供任何 ID。", file=sys.stderr)
        return 1
    payload = client.idconv(ids[:200], idtype=args.idtype)
    records = payload.get("records") or []
    for rec in records:
        print("%s | %s | %s | %s" % (rec.get("pmid") or "-", rec.get("pmcid") or "-",
                                     rec.get("doi") or "-", rec.get("live") or ""))
    print("共 %d 条。" % len(records), file=sys.stderr)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print("保存 → %s" % args.out, file=sys.stderr)
    return 0


def cmd_nber(args):
    """NBER 工作论文检索（免费 JSON API，无需 key）。"""
    import nber as nber_mod
    client = nber_mod.NBERClient(
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    if args.paper:
        meta = client.paper_metadata(args.paper)
        print("标题: %s" % meta.get("title"))
        print("作者: %s" % "; ".join(meta.get("authors") or []))
        print("日期: %s" % meta.get("publication_date"))
        print("DOI: %s" % meta.get("doi"))
        print("PDF: %s" % meta.get("pdf_url"))
        return 0
    rows = []
    for query in (args.query or []):
        found = client.search(
            query,
            program=args.program or "",
            page=args.page,
            per_page=args.limit,
            new_this_week=args.new_this_week,
        )
        rows.extend(found[:args.limit])
    if args.year_min or args.year_max:
        rows = [r for r in rows
                if (not args.year_min or (r.get("year") or 0) >= args.year_min)
                and (not args.year_max or (r.get("year") or 9999) <= args.year_max)]
    _emit_rows(rows, args.out)
    return 0


def cmd_ssrn(args):
    """SSRN 工作论文：经 OpenAlex（source S4210172589）+ Crossref（前缀 10.2139）检索。

    SSRN 站点本身有 Cloudflare 校验，无法直抓；其条目已被两大索引收录。
    """
    import openalex as oa
    import crossref as crossref_mod

    oa_client = oa.OpenAlexClient(
        mailto=args.mailto,
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    cr_client = crossref_mod.CrossrefClient(
        mailto=args.mailto,
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )

    rows = []
    for query in (args.query or []):
        if "openalex" in args.sources:
            filters = "primary_location.source.id:%s" % oa.SOURCE_IDS["ssrn"]
            if args.filter:
                filters += "," + args.filter
            rows.extend(oa_client.search(search=query, filter=filters,
                                         sort=args.sort, limit=args.limit))
        if "crossref" in args.sources:
            items, total = cr_client.prefix_works(
                "10.2139", query=query, rows=args.limit,
                filters=args.filter or None, sort=args.sort)
            print("Crossref(10.2139) 命中约 %s 条" % total, file=sys.stderr)
            for item in items:
                rec = crossref_mod.normalize(item)
                if rec:
                    rec["_meta"]["source"] = "crossref-ssrn"
                    if not rec.get("venue"):
                        rec["venue"] = "SSRN working paper"
                    rec["publicationTypes"] = ["working paper"]
                    rows.append(rec)

    unique, dup = s2api.dedup(rows)
    print("合并 %d 条，去重 %d 条" % (len(rows), dup), file=sys.stderr)
    _emit_rows(unique, args.out)
    return 0


def cmd_openalex(args):
    """OpenAlex works 检索。"""
    import openalex as oa
    client = oa.OpenAlexClient(
        mailto=args.mailto,
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    rows = []
    if args.citations or args.references:
        target = args.doi or args.work_id
        if not target:
            print("需要 --doi 或 --work-id 才能查引文边。", file=sys.stderr)
            return 1
        if args.citations:
            rows = client.citations(target, limit=args.limit)
        else:
            rows = client.references(target, limit=args.limit)
    elif args.related:
        target = args.doi or args.work_id
        if not target:
            print("需要 --doi 或 --work-id 才能查相关文献。", file=sys.stderr)
            return 1
        rows = client.related(target, limit=args.limit)
    else:
        filter_expr = args.filter or ""
        if args.source:
            source_id = oa.SOURCE_IDS.get(args.source.lower())
            if not source_id:
                print("未知 source：%s（可选：%s）"
                      % (args.source, ", ".join(sorted(oa.SOURCE_IDS))), file=sys.stderr)
                return 1
            clause = "primary_location.source.id:%s" % source_id
            filter_expr = (clause + "," + filter_expr) if filter_expr else clause
        rows = client.search(
            search=args.query,
            filter=filter_expr or None,
            sort=args.sort,
            limit=args.limit,
            cursor=args.cursor,
        )
    _emit_rows(rows, args.out)
    return 0


def cmd_opencitations(args):
    """OpenCitations 引用图谱（免 key）。"""
    import opencitations
    client = opencitations.OpenCitationsClient(
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    rows = getattr(client, args.direction)(args.doi, limit=args.limit)
    _emit_rows(rows, args.out)
    return 0


def cmd_arxiv(args):
    """arXiv 预印本检索。"""
    import preprints
    client = preprints.PreprintClient(
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    categories = [c.strip() for c in (args.categories or "").split(",") if c.strip()]
    rows = []
    for query in (args.query or ["all:"]):
        rows.extend(client.arxiv_search(
            query,
            max_results=args.limit,
            sort_by=args.sort_by,
            sort_order=args.sort_order,
            categories=categories or None,
            date_range=parse_date_range(args.date_range),
        ))
    if args.strict_category and categories:
        wanted = set(c.lower() for c in categories)
        kept = [r for r in rows
                if wanted & set(c.lower() for c in (r.get("categories") or []))]
        print("分类校验：%d → %d 条" % (len(rows), len(kept)), file=sys.stderr)
        rows = kept
    _emit_rows(rows, args.out)

    if args.plan or args.confirm_download:
        import oa_fulltext
        client_oa = oa_fulltext.OAClient(
            email=args.email,
            timeout=args.timeout,
            proxy=args.proxy,
            trust_env=(not args.no_proxy),
            verbose=(not args.quiet),
        )
        plan = client_oa.build_download_plan(rows, directory=args.dir)
        print("\n=== 下载计划（%d 项）===" % len(plan["items"]), file=sys.stderr)
        for item in plan["items"]:
            print("  [%s] %s | %s" % (item["kind"], item["title"][:60], item["url"]))
        if args.confirm_download:
            result = client_oa.download(plan, confirm=True)
            print("下载完成 %d 个，失败 %d 个。" % (len(result.get("downloaded", [])),
                                                  len(result.get("failed", []))), file=sys.stderr)
        else:
            print("未执行下载：先向用户汇报本计划并取得批准，再加 --confirm-download。",
                  file=sys.stderr)
    return 0


def cmd_biorxiv(args):
    """bioRxiv / medRxiv 按日期浏览；--published 取预印本→正式版对应。"""
    import preprints
    client = preprints.PreprintClient(
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    date_range = parse_date_range(args.date_range)
    if date_range and date_range[0] and len(date_range[0]) == 4:
        date_range = ("%s-01-01" % date_range[0],
                      "%s-12-31" % (date_range[1] or date_range[0]))
    if args.published:
        rows = client.biorxiv_published(server=args.server, date_range=date_range,
                                        limit=args.limit)
    else:
        rows = client.biorxiv_details(server=args.server, date_range=date_range,
                                      limit=args.limit)
    _emit_rows(rows, args.out)
    return 0


def cmd_unpaywall(args):
    """Unpaywall OA 状态；--in 可批量给已有记录补 openAccess 字段。"""
    import oa_fulltext
    client = oa_fulltext.OAClient(
        email=args.email,
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    rows = []
    if args.input:
        rows = s2api.read_jsonl(args.input)
        rows = client.annotate_oa(rows)
        if args.out:
            s2api.write_jsonl(args.out, rows, append=False)
            print("保存 %d 条（含 OA 字段）→ %s" % (len(rows), args.out), file=sys.stderr)
    else:
        for doi in (args.doi or []):
            try:
                rows.append(client.unpaywall(doi))
            except oa_fulltext.OAError as exc:
                print("Unpaywall %s 失败：%s" % (doi, exc), file=sys.stderr)
        for rec in rows:
            print("%s | %s | %s" % (rec.get("doi"), rec.get("oa_status"),
                                    rec.get("pdf_url") or rec.get("oa_url") or "-"))
        print("共 %d 条。" % len(rows), file=sys.stderr)

    if args.plan or args.confirm_download:
        plan = client.build_download_plan(rows, directory=args.dir)
        print("\n=== 下载计划（%d 项）===" % len(plan["items"]), file=sys.stderr)
        for item in plan["items"]:
            print("  [%s] %s | %s | %s" % (item["kind"], item["title"][:60],
                                            item["host"], item["url"]))
        print("目标目录：%s" % plan["directory"], file=sys.stderr)
        if args.confirm_download:
            result = client.download(plan, confirm=True)
            print("下载完成 %d 个，失败 %d 个。" % (len(result.get("downloaded", [])),
                                                  len(result.get("failed", []))), file=sys.stderr)
            for item in result.get("failed", []):
                print("  失败：%s（%s）" % (item["url"], item["error"]), file=sys.stderr)
        else:
            print("未执行下载：如需下载，先向用户汇报本计划并取得批准，"
                  "再加 --confirm-download 重跑。", file=sys.stderr)
    return 0


def cmd_core(args):
    """CORE 全文检索；下载同样需要 --confirm-download。"""
    import oa_fulltext
    client = oa_fulltext.OAClient(
        core_api_key=args.core_api_key,
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    if args.doi:
        rows = [client.core_work(args.doi)]
    else:
        rows = client.core_search(args.query, limit=args.limit)
    _emit_rows(rows, args.out)

    if args.plan or args.confirm_download:
        plan = client.build_download_plan(rows, directory=args.dir)
        print("\n=== 下载计划（%d 项）===" % len(plan["items"]), file=sys.stderr)
        for item in plan["items"]:
            print("  [%s] %s | %s | %s" % (item["kind"], item["title"][:60],
                                            item["host"], item["url"]))
        if args.confirm_download:
            result = client.download(plan, confirm=True)
            print("下载完成 %d 个，失败 %d 个。" % (len(result.get("downloaded", [])),
                                                  len(result.get("failed", []))), file=sys.stderr)
        else:
            print("未执行下载：先向用户汇报本计划并取得批准，再加 --confirm-download。",
                  file=sys.stderr)
    return 0


def cmd_econ(args):
    """经济学工作论文：Crossref(ISSN) + RePEc/IDEAS + SSRN（后两者为脆弱网页抓取）。"""
    import econ_sources
    client = econ_sources.EconSourcesClient(
        timeout=args.timeout,
        proxy=args.proxy,
        trust_env=(not args.no_proxy),
        verbose=(not args.quiet),
    )
    sources = tuple(s.strip() for s in (args.sources or "crossref,ideas,ssrn").split(",") if s.strip())
    if "ssrn" in sources or "ideas" in sources:
        print("提示：SSRN / IDEAS 站点直抓当前不可用（Cloudflare 校验 / JS 渲染）。"
              "SSRN 内容请用 `litsearch.py ssrn`（OpenAlex + Crossref 索引），"
              "经济学工作论文请用 `litsearch.py nber`。", file=sys.stderr)
    rows = []
    for query in (args.query or []):
        rows.extend(client.search(query, limit=args.limit, sources=sources))
    _emit_rows(rows, args.out)
    return 0


def cmd_match(args):
    """按标题精确匹配（S2 /paper/search/match）。"""
    client = make_client(args)
    rows = client.match_paper(args.title, limit=args.limit)
    for rec in rows:
        print("- %s (%s) %s | %s" % (rec.get("title") or "?", rec.get("year") or "?",
                                     rec.get("venue") or "",
                                     rec.get("externalIds", {}).get("DOI") or rec.get("paperId") or ""))
    if args.out:
        s2api.write_jsonl(args.out, rows, append=False)
        print("保存 %d 条 → %s" % (len(rows), args.out), file=sys.stderr)
    print("共 %d 条候选。" % len(rows), file=sys.stderr)
    return 0


# --------------------------------------------------------------------------
# argparse
# --------------------------------------------------------------------------

def add_common(parser):
    parser.add_argument("--api-key", help="显式传递 S2 API key（优先级最高）")
    parser.add_argument("--rps", type=float, default=1.0, help="请求速率上限，默认 1.0（官方个人 key 口径）")
    parser.add_argument("--timeout", type=int, default=60, help="单请求超时秒数，默认 60")
    parser.add_argument("--max-retries", dest="max_retries", type=int, default=8,
                        help="网络/5xx 的最大重试次数，默认 8（退避 2/4/8/16/32/60s）")
    parser.add_argument("--retry-429", dest="retry_429", action="store_true",
                        help="允许对 429 重试。默认关闭：遇到 429 立即停止本次检索，"
                             "不再发后续请求，避免继续消耗额度")
    parser.add_argument("--proxy", help="显式代理，如 http://127.0.0.1:7890")
    parser.add_argument("--no-proxy", action="store_true",
                        help="忽略环境/系统代理（Windows 注册表代理常导致 ProxyError）")
    parser.add_argument("--anonymous", action="store_true",
                        help="无 key 时也继续（走匿名共享池，速率低且不稳定）")
    parser.add_argument("--quiet", action="store_true", help="不打印进度")


def add_filters(parser):
    parser.add_argument("--year", help="年份或区间，如 2015- / 2015:2020")
    parser.add_argument("--publication-date", help="精确日期区间，如 2020-01-01:2024-12-31")
    parser.add_argument("--venue", help="期刊/会议名，逗号分隔")
    parser.add_argument("--fields-of-study", dest="fields_of_study", help="学科，如 Computer Science")
    parser.add_argument("--min-citations", dest="min_citations", type=int)
    parser.add_argument("--pub-types", dest="pub_types", help="如 JournalArticle,Review")
    parser.add_argument("--open-access", dest="open_access", action="store_true")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="litsearch",
        description="批量文献检索 CLI（Semantic Scholar REST）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("check", help="检查 key 与配置")
    add_common(p)
    p.add_argument("--live", action="store_true", help="发一个最小请求验证连通性")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("search", help="bulk 检索（多 query、断点续传）")
    add_common(p)
    add_filters(p)
    p.add_argument("--query", action="append", help="检索式，可重复")
    p.add_argument("--queries-file", help="JSON 数组：字符串或 {name,query,year,...}")
    p.add_argument("--out", required=True, help="输出目录（papers.jsonl/state.json/manifest.json）")
    p.add_argument("--max-results", dest="max_results", type=int, default=1000,
                   help="每个 query 累计上限，默认 1000")
    p.add_argument("--sort", default="citationCount:desc",
                   help="citationCount:desc / publicationDate:desc / paperId:asc")
    p.add_argument("--fields", default="standard", help="预设名或逗号分隔字段")
    p.add_argument("--plan", action="store_true", help="只打印计划，不发请求")
    p.add_argument("--restart", action="store_true", help="忽略已有 state，重跑全部 query")
    p.add_argument("--fail-fast", dest="fail_fast", action="store_true")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("hydrate", help="批量补齐元数据（batch）")
    add_common(p)
    p.add_argument("--in", dest="input", required=True, help="输入 JSONL")
    p.add_argument("--out", required=True, help="输出 JSONL")
    p.add_argument("--fields", default="detail", help="预设名或逗号分隔字段")
    p.set_defaults(func=cmd_hydrate)

    p = sub.add_parser("expand", help="引文滚雪球")
    add_common(p)
    p.add_argument("--in", dest="input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--direction", default="citations",
                   choices=["citations", "references", "both"])
    p.add_argument("--depth", type=int, default=1)
    p.add_argument("--max-per-seed", dest="max_per_seed", type=int, default=200)
    p.add_argument("--max-frontier", dest="max_frontier", type=int, default=50)
    p.add_argument("--max-total", dest="max_total", type=int, default=5000)
    p.add_argument("--fields", default="standard")
    p.set_defaults(func=cmd_expand)

    p = sub.add_parser("dedup", help="去重 + 规则筛选")
    add_common(p)
    p.add_argument("--in", dest="input", required=True)
    p.add_argument("--out", help="输出 CSV（默认 <input>_dedup.csv）")
    p.add_argument("--out-jsonl", dest="out_jsonl", help="同时写一份 JSONL")
    p.add_argument("--year-min", dest="year_min", type=int)
    p.add_argument("--year-max", dest="year_max", type=int)
    p.add_argument("--min-citations", dest="min_citations", type=int)
    p.add_argument("--venue-regex", dest="venue_regex", help="venue 正则，不区分大小写")
    p.add_argument("--require-abstract", dest="require_abstract", action="store_true")
    p.add_argument("--require-doi", dest="require_doi", action="store_true")
    p.add_argument("--require-term", dest="require_term", action="append",
                   help="标题+摘要必须含该词，可重复")
    p.add_argument("--exclude-term", dest="exclude_term", action="append",
                   help="标题+摘要不得含该词，可重复")
    p.add_argument("--sort", choices=["citations", "year", "none"], default="citations")
    p.set_defaults(func=cmd_dedup)

    p = sub.add_parser("export", help="导出 Markdown/CSV/BibTeX/JSONL")
    add_common(p)
    p.add_argument("--in", dest="input", required=True, help="输入 JSONL")
    p.add_argument("--out", required=True)
    p.add_argument("--format", required=True,
                   choices=["md", "csv", "bib", "ris", "apa", "gbt", "jsonl"])
    p.add_argument("--limit", type=int, default=50, help="md 表格行数")
    p.add_argument("--details", type=int, default=10, help="md 详情条数")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("datasets", help="Datasets 列表与下载")
    add_common(p)
    p.add_argument("--release", default="latest")
    p.add_argument("--dataset", help="如 papers / abstracts / authors / citations")
    p.add_argument("--download-dir", dest="download_dir", help="下载到目录")
    p.set_defaults(func=cmd_datasets)

    p = sub.add_parser("snippets", help="片段检索")
    add_common(p)
    p.add_argument("--query", required=True)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--fields")
    p.add_argument("--out", help="保存 JSONL")
    p.set_defaults(func=cmd_snippets)

    p = sub.add_parser("crossref", help="Crossref 检索（无需 API key）")
    add_common(p)
    p.add_argument("--query", help="模糊检索词（走 bibliographic 匹配）")
    p.add_argument("--title", help="标题检索")
    p.add_argument("--author", help="作者检索")
    p.add_argument("--doi", help="按 DOI 取单条记录")
    p.add_argument("--journal", help="期刊 ISSN，限定在该刊内检索")
    p.add_argument("--prefix", help="DOI 前缀，如 10.2139（SSRN）/ 10.3386（NBER）")
    p.add_argument("--references", action="store_true",
                   help="配合 --doi：同时输出该文献的参考文献列表")
    p.add_argument("--rows", type=int, default=20)
    p.add_argument("--filter", help="如 from-pub-date:2020-01-01,type:journal-article")
    p.add_argument("--sort", help="如 relevance / published / is-referenced-by-count")
    p.add_argument("--order", choices=["asc", "desc"])
    p.add_argument("--select", help="限定返回字段")
    p.add_argument("--mailto", help="邮箱，进入 Crossref 礼貌池")
    p.add_argument("--out", help="结果保存为 JSONL")
    p.set_defaults(func=cmd_crossref)

    p = sub.add_parser("match", help="按标题精确匹配（S2 match 接口）")
    add_common(p)
    p.add_argument("--title", required=True)
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--out")
    p.set_defaults(func=cmd_match)

    p = sub.add_parser("pubmed", help="PubMed 检索（NCBI E-utilities）")
    add_net(p)
    p.add_argument("--query", action="append", help="PubMed 检索式，可重复")
    p.add_argument("--limit", type=int, default=20, help="每个 query 取回条数")
    p.add_argument("--sort", default="relevance", help="relevance / pub_date / Author")
    p.add_argument("--date-range", dest="date_range", help="如 2020-01-01:2024-12-31")
    p.add_argument("--pub-type", dest="pub_type", action="append",
                   help="Publication Type 限定，如 Review")
    p.add_argument("--email", help="NCBI 邮箱（礼貌池），也可用 NCBI_EMAIL")
    p.add_argument("--out", help="结果保存为 JSONL")
    p.set_defaults(func=cmd_pubmed)

    p = sub.add_parser("pmc", help="PMC 全文（JATS XML / 分节 / BioC）")
    add_net(p)
    p.add_argument("--pmcid", help="如 PMC7029759")
    p.add_argument("--pmid", help="PMID（自动解析出 PMCID）")
    p.add_argument("--sections", action="store_true", help="输出分节正文")
    p.add_argument("--bioc", action="store_true", help="输出 BioC 结构化全文")
    p.add_argument("--email")
    p.add_argument("--out", help="保存全文到文件")
    p.set_defaults(func=cmd_pmc)

    p = sub.add_parser("idconv", help="ID 互转 PMID/PMCID/DOI/MID")
    add_net(p)
    p.add_argument("--ids", action="append", help="ID（逗号分隔），可重复")
    p.add_argument("--in", dest="input", help="从 JSONL 提取 DOI/PMID/PMCID 批量转换")
    p.add_argument("--idtype", help="pmid / pmcid / doi")
    p.add_argument("--email")
    p.add_argument("--out", help="保存原始 JSON")
    p.set_defaults(func=cmd_idconv)

    p = sub.add_parser("openalex", help="OpenAlex works 检索")
    add_net(p)
    p.add_argument("--query", help="search 参数")
    p.add_argument("--filter", help="OpenAlex 过滤表达式")
    p.add_argument("--source", help="限定来源，如 ssrn / nber / aer / misq（见 references/journal-identifiers.md）")
    p.add_argument("--sort", help="如 publication_year:desc")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--cursor", action="store_true", help="用 cursor 深翻页")
    p.add_argument("--doi", help="配合 --citations/--references：目标 DOI")
    p.add_argument("--work-id", dest="work_id", help="配合 --citations/--references：W 开头的 OpenAlex ID")
    p.add_argument("--citations", action="store_true", help="查谁引用了它")
    p.add_argument("--references", action="store_true", help="查它引用了谁")
    p.add_argument("--related", action="store_true", help="查相关文献（OpenAlex related_works，非引用边）")
    p.add_argument("--mailto", help="邮箱，进入礼貌池")
    p.add_argument("--out", help="结果保存为 JSONL")
    p.set_defaults(func=cmd_openalex)

    p = sub.add_parser("opencitations", help="OpenCitations 引用图谱（免 key）")
    add_net(p)
    p.add_argument("--doi", required=True, help="DOI，如 10.1038/nature12373")
    p.add_argument("--direction", default="citations",
                   choices=["citations", "references"],
                   help="citations=谁引用了它；references=它引用了谁")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--out", help="结果保存为 JSONL")
    p.set_defaults(func=cmd_opencitations)

    p = sub.add_parser("nber", help="NBER 工作论文检索（免费，无需 key）")
    add_net(p)
    p.add_argument("--query", action="append", help="关键词，可重复")
    p.add_argument("--program", help="项目名，如 Labor Studies")
    p.add_argument("--new-this-week", dest="new_this_week", action="store_true",
                   help="只取本周新发布")
    p.add_argument("--paper", help="取单篇的完整题录（如 w31201）")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--year-min", dest="year_min", type=int)
    p.add_argument("--year-max", dest="year_max", type=int)
    p.add_argument("--out", help="结果保存为 JSONL")
    p.set_defaults(func=cmd_nber)

    p = sub.add_parser("ssrn", help="SSRN 工作论文（经 OpenAlex + Crossref 索引）")
    add_net(p)
    p.add_argument("--query", action="append", help="关键词，可重复")
    p.add_argument("--sources", default="openalex,crossref", help="openalex,crossref")
    p.add_argument("--filter", help="附加的 OpenAlex / Crossref 过滤条件")
    p.add_argument("--sort", help="排序，如 cited_by_count:desc")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--mailto", help="邮箱，进入礼貌池")
    p.add_argument("--out", help="结果保存为 JSONL")
    p.set_defaults(func=cmd_ssrn)

    p = sub.add_parser("arxiv", help="arXiv 预印本检索")
    add_net(p)
    p.add_argument("--query", action="append", help="arXiv 语法检索式，可重复")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--categories", help="分类，逗号分隔，如 econ.GN,cs.LG")
    p.add_argument("--date-range", dest="date_range", help="如 2020-01-01:2024-12-31")
    p.add_argument("--sort-by", dest="sort_by", default="relevance",
                   help="relevance / lastUpdatedDate / submittedDate")
    p.add_argument("--sort-order", dest="sort_order", default="descending",
                   choices=["ascending", "descending"])
    p.add_argument("--strict-category", dest="strict_category", action="store_true",
                   help="本地复核分类（arXiv 的 cat: 过滤并不总是严格生效）")
    p.add_argument("--plan", action="store_true", help="打印 PDF 下载计划（不下载）")
    p.add_argument("--confirm-download", dest="confirm_download", action="store_true",
                   help="执行下载。必须先向用户汇报下载计划并取得批准")
    p.add_argument("--dir", default="downloads", help="下载目录")
    p.add_argument("--email")
    p.add_argument("--out", help="结果保存为 JSONL")
    p.set_defaults(func=cmd_arxiv)

    p = sub.add_parser("biorxiv", help="bioRxiv / medRxiv 日期浏览")
    add_net(p)
    p.add_argument("--server", default="biorxiv", choices=["biorxiv", "medrxiv"])
    p.add_argument("--date-range", dest="date_range", help="如 2024-01-01:2024-12-31")
    p.add_argument("--published", action="store_true",
                   help="取预印本→正式发表版的对应关系")
    p.add_argument("--limit", type=int, default=100)
    p.add_argument("--out", help="结果保存为 JSONL")
    p.set_defaults(func=cmd_biorxiv)

    p = sub.add_parser("unpaywall", help="Unpaywall OA 状态与 PDF 链接")
    add_net(p)
    p.add_argument("--doi", action="append", help="DOI，可重复")
    p.add_argument("--in", dest="input", help="批量给 JSONL 记录补 OA 字段")
    p.add_argument("--out", help="输出 JSONL")
    p.add_argument("--plan", action="store_true", help="打印下载计划（不下载）")
    p.add_argument("--confirm-download", dest="confirm_download", action="store_true",
                   help="执行下载。必须先向用户汇报下载计划并取得批准")
    p.add_argument("--dir", default="downloads", help="下载目录")
    p.add_argument("--email", help="邮箱，也可用 UNPAYWALL_EMAIL")
    p.set_defaults(func=cmd_unpaywall)

    p = sub.add_parser("core", help="CORE 全文检索")
    add_net(p)
    p.add_argument("--query", help="检索式")
    p.add_argument("--doi", help="按 DOI/CORE id 取单条")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--out", help="结果保存为 JSONL")
    p.add_argument("--plan", action="store_true", help="打印下载计划（不下载）")
    p.add_argument("--confirm-download", dest="confirm_download", action="store_true",
                   help="执行下载。必须先向用户汇报下载计划并取得批准")
    p.add_argument("--dir", default="downloads", help="下载目录")
    p.add_argument("--core-api-key", dest="core_api_key", help="CORE key，也可用 CORE_API_KEY")
    p.set_defaults(func=cmd_core)

    p = sub.add_parser("econ", help="经济学工作论文（Crossref + IDEAS + SSRN）")
    add_net(p)
    p.add_argument("--query", action="append", help="检索词，可重复")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--sources", help="crossref,ideas,ssrn（默认全部）")
    p.add_argument("--out", help="结果保存为 JSONL")
    p.set_defaults(func=cmd_econ)

    return parser


def _source_error_classes(attr):
    """收集各数据源模块的异常类（模块按需导入，故延迟加载）。"""
    classes = []
    for mod_name, name in (
        ("ncbi", attr),
        ("openalex", attr),
        ("preprints", attr),
        ("oa_fulltext", attr),
        ("econ_sources", "EconSourcesError"),
    ):
        try:
            mod = __import__(mod_name)
            cls = getattr(mod, name, None)
            if cls is not None:
                classes.append(cls)
        except Exception:
            continue
    return tuple(classes)


def _RateLimitErrors():
    return (_source_error_classes("NCBIRateLimitError")
            + _source_error_classes("OpenAlexRateLimitError")
            + _source_error_classes("PreprintRateLimitError")
            + _source_error_classes("OARateLimitError"))


def main(argv=None):
    setup_io()
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 1

    try:
        return args.func(args) or 0
    except s2api.S2RateLimitError as exc:
        print("速率限制，已停止（未继续发送后续请求）：\n%s" % exc, file=sys.stderr)
        return 3
    except crossref_mod.CrossrefRateLimitError as exc:
        print("Crossref 限流，已停止：%s" % exc, file=sys.stderr)
        return 3
    except _RateLimitErrors() as exc:
        print("限流，已停止（未继续发送后续请求）：\n%s" % exc, file=sys.stderr)
        return 3
    except s2api.S2AuthError as exc:
        print("认证错误：%s" % exc, file=sys.stderr)
        return 2
    except (s2api.S2Error, crossref_mod.CrossrefError) as exc:
        print("API 错误：%s" % exc, file=sys.stderr)
        return 3
    except _source_error_classes("NCBIError") + _source_error_classes("OpenAlexError") \
            + _source_error_classes("PreprintError") + _source_error_classes("OAError") as exc:
        print("数据源错误：%s" % exc, file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("\n已中断（state 已保存，可重跑同命令续传）。", file=sys.stderr)
        return 130
    except (ValueError, OSError) as exc:
        print("参数/文件错误：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
