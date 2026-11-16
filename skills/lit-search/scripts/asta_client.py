#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Asta MCP 的脚本侧客户端（备用通道）。

为什么需要它：
- Asta 走 MCP。正常情况下由 agent 直接调 MCP 工具。
- 但 Asta 端点 `https://asta-tools.allen.ai/mcp/v1` 在部分网络下会被边缘 WAF
  拦成 403 HTML 页面（不是 JSON 错误），此时 MCP 工具全部不可用。
- 前置条件：在代理软件（mihomo / clash）自定义规则里加入
  `DOMAIN,asta-tools.allen.ai,PROXY`，并打开 TUN 模式。
- 本脚本用同样的 MCP 协议（initialize → notifications/initialized → tools/call）
  从 Python 直接调用，可显式指定代理。

用法：
  python asta_client.py tools
  python asta_client.py search --keyword "advertising sales" --limit 20 --out r.jsonl
  python asta_client.py paper --ids <paperId|DOI:...> [--ids ...] --out p.jsonl
  python asta_client.py citations --id <paperId> --limit 50 --date-range "2020-" --out c.jsonl
  python asta_client.py snippets --query "..." --limit 10 --paper-ids a,b --out s.jsonl
  python asta_client.py authors --name "..." --fields "name,paperCount,citationCount,hIndex,externalIds"
  python asta_client.py author-papers --author-id 123 --limit 50

通用选项：
  --proxy socks5://127.0.0.1:10809   显式代理
  --auto-proxy                       先直连，遇 403 再依次尝试本机常见代理端口
  --no-proxy                         强制直连
  --api-key <key>                    显式 key（默认读环境变量 ASTA_API_KEY 或 .env）

Python 3.7+，依赖 requests（socks5 需要 PySocks）。
"""

from __future__ import print_function

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import s2api  # noqa: E402

ENDPOINT = "https://asta-tools.allen.ai/mcp/v1"
PROTOCOL_VERSION = "2024-11-05"

# 本机常见的代理端口（mihomo/clash）。按实测顺序尝试。
AUTO_PROXY_CANDIDATES = [
    "socks5://127.0.0.1:10809",
    "socks5h://127.0.0.1:10809",
    "http://127.0.0.1:10809",
    "socks5://127.0.0.1:10808",
    "http://127.0.0.1:10808",
]


class AstaError(Exception):
    pass


class AstaRoutingError(AstaError):
    """403 HTML：通常是路由/WAF，而不是 API 语义错误。"""


class AstaClient(object):
    def __init__(self, api_key=None, proxy=None, auto_proxy=False, timeout=90,
                 verbose=True, endpoint=ENDPOINT):
        try:
            import requests
        except ImportError:
            raise SystemExit("缺少依赖：pip install requests")

        self._requests = requests
        self.api_key = api_key or s2api.resolve_key_from_env(("ASTA_API_KEY",))
        if not self.api_key:
            raise AstaError("未找到 ASTA_API_KEY：请在 .env 写 ASTA_API_KEY=... 或设置环境变量")
        self.timeout = timeout
        self.verbose = verbose
        self.endpoint = endpoint
        self._proxy_candidates = []
        if auto_proxy:
            self._proxy_candidates = list(AUTO_PROXY_CANDIDATES)
        elif proxy:
            self._proxy_candidates = [proxy]
        self._session = None
        self._tools = None

    # -- 传输层 -----------------------------------------------------------

    def _new_session(self, proxy=None):
        s = self._requests.Session()
        # 默认不信任环境/注册表代理：本机直连 Asta 会被 403，代理才通
        s.trust_env = False
        if proxy:
            s.proxies = {"http": proxy, "https": proxy}
        s.headers.update({
            "x-api-key": self.api_key,
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        })
        return s

    def _rpc(self, session, method, params=None, notify=False):
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        if not notify:
            payload["id"] = 1
        resp = session.post(self.endpoint, json=payload, timeout=self.timeout)
        if notify and resp.status_code in (200, 202):
            return None
        if resp.status_code not in (200, 202):
            body = (resp.text or "")[:200]
            if resp.status_code == 403 and body.lstrip().startswith("<"):
                raise AstaRoutingError(
                    "Asta 返回 403 HTML（边缘拦截，非 API 错误）。\n"
                    "前置条件：代理软件自定义规则加入 DOMAIN,asta-tools.allen.ai,PROXY，"
                    "并打开 TUN 模式。\n"
                    "本机实测：直连不可通，socks5://127.0.0.1:10809 可通。\n"
                    "请改用 --proxy socks5://127.0.0.1:10809 或 --auto-proxy。"
                )
            raise AstaError("HTTP %s：%s" % (resp.status_code, body))
        if notify:
            return None
        return self._parse_messages(resp.text)

    @staticmethod
    def _parse_messages(text):
        """解析 JSON 或 SSE（event:/data:）响应。"""
        chunks = []
        try:
            payload = json.loads(text)
            chunks.append(payload)
        except ValueError:
            for line in (text or "").splitlines():
                if line.startswith("data:"):
                    raw = line[5:].strip()
                    if not raw:
                        continue
                    try:
                        chunks.append(json.loads(raw))
                    except ValueError:
                        chunks.append({"raw": raw})
        return chunks

    def connect(self):
        """初始化连接；auto_proxy 模式下遇 403 依次换代理重试。"""
        attempts = self._proxy_candidates or [None]
        last_error = None
        for proxy in attempts:
            session = self._new_session(proxy)
            try:
                self._rpc(session, "initialize", {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "lit-search/asta_client", "version": "1.0"},
                })
                self._rpc(session, "notifications/initialized", notify=True)
                self._session = session
                if proxy:
                    print("[proxy] %s" % proxy, file=sys.stderr)
                return self
            except AstaRoutingError as exc:
                last_error = exc
                if self.verbose:
                    print("[route] 直连/当前代理失败：%s" % proxy, file=sys.stderr)
                continue
            except AstaError as exc:
                last_error = exc
                break
        raise last_error or AstaError("连接失败")

    # -- 工具层 -----------------------------------------------------------

    def list_tools(self):
        if self._tools is not None:
            return self._tools
        if self._session is None:
            self.connect()
        msgs = self._rpc(self._session, "tools/list")
        tools = []
        for msg in msgs:
            result = msg.get("result") or {}
            tools.extend(result.get("tools") or [])
        self._tools = tools
        return tools

    def call(self, tool, arguments):
        """调用工具，返回解析后的对象列表。

        Asta 的返回是 content blocks：一段文本通常对应一个 JSON 对象。
        """
        if self._session is None:
            self.connect()
        msgs = self._rpc(self._session, "tools/call", {
            "name": tool,
            "arguments": arguments or {},
        })
        out = []
        for msg in msgs:
            if "error" in msg:
                raise AstaError("MCP 错误：%s" % json.dumps(msg["error"], ensure_ascii=False))
            result = msg.get("result") or {}
            if result.get("isError"):
                texts = [c.get("text") for c in (result.get("content") or [])]
                raise AstaError("工具返回错误：%s" % " ".join([t for t in texts if t])[:300])
            for block in (result.get("content") or []):
                if block.get("type") != "text":
                    continue
                text = (block.get("text") or "").strip()
                if not text:
                    continue
                try:
                    parsed = json.loads(text)
                except ValueError:
                    out.append({"text": text})
                    continue
                if isinstance(parsed, list):
                    out.extend(parsed)
                else:
                    out.append(parsed)
        return out

    # -- 高层封装 ---------------------------------------------------------

    def search_relevance(self, keyword, limit=20, fields=None,
                         date_range=None, venues=None):
        args = {"keyword": keyword, "limit": limit}
        if fields:
            args["fields"] = fields
        if date_range:
            args["publication_date_range"] = date_range
        if venues:
            args["venues"] = venues
        return self.call("search_papers_by_relevance", args)

    def search_title(self, title, limit=None, fields=None, date_range=None, venues=None):
        args = {"title": title}
        if limit:
            args["limit"] = limit
        if fields:
            args["fields"] = fields
        if date_range:
            args["publication_date_range"] = date_range
        if venues:
            args["venues"] = venues
        return self.call("search_paper_by_title", args)

    def get_paper(self, paper_id, fields=None):
        args = {"paper_id": paper_id}
        if fields:
            args["fields"] = fields
        return self.call("get_paper", args)

    def get_paper_batch(self, ids, fields=None):
        """ids 必须是列表（与 snippet_search 的 paper_ids 逗号分隔不同）。"""
        args = {"ids": list(ids)}
        if fields:
            args["fields"] = fields
        return self.call("get_paper_batch", args)

    def get_citations(self, paper_id, limit=50, fields=None, date_range=None):
        args = {"paper_id": paper_id, "limit": limit}
        if fields:
            args["fields"] = fields
        if date_range:
            args["publication_date_range"] = date_range
        return self.call("get_citations", args)

    def snippet_search(self, query, limit=10, venues=None, paper_ids=None, inserted_before=None):
        args = {"query": query, "limit": limit}
        if venues:
            args["venues"] = venues
        if paper_ids:
            args["paper_ids"] = paper_ids if isinstance(paper_ids, str) else ",".join(paper_ids)
        if inserted_before:
            args["inserted_before"] = inserted_before
        return self.call("snippet_search", args)

    def search_authors(self, name, limit=10, fields=None):
        args = {"name": name, "limit": limit}
        if fields:
            args["fields"] = fields
        return self.call("search_authors_by_name", args)

    def get_author_papers(self, author_id, limit=50, paper_fields=None):
        args = {"author_id": author_id, "limit": limit}
        if paper_fields:
            args["paper_fields"] = paper_fields
        return self.call("get_author_papers", args)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _save(rows, out):
    if not out:
        return
    s2api.write_jsonl(out, rows, append=False)
    print("保存 %d 条 → %s" % (len(rows), out), file=sys.stderr)


def build_parser():
    p = argparse.ArgumentParser(prog="asta_client", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    def common(sp):
        sp.add_argument("--api-key")
        sp.add_argument("--proxy")
        sp.add_argument("--auto-proxy", action="store_true")
        sp.add_argument("--no-proxy", action="store_true")
        sp.add_argument("--timeout", type=int, default=90)
        sp.add_argument("--out", help="结果保存为 JSONL")
        sp.add_argument("--fields", help="fields 字段串")

    sp = sub.add_parser("tools", help="列出可用工具")
    common(sp)

    sp = sub.add_parser("search", help="主题检索")
    common(sp)
    sp.add_argument("--keyword", required=True)
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--date-range", dest="date_range", help="如 2021: 或 2020-01:2024-06")
    sp.add_argument("--venues")

    sp = sub.add_parser("title", help="标题匹配")
    common(sp)
    sp.add_argument("--title", required=True)
    sp.add_argument("--limit", type=int)
    sp.add_argument("--date-range", dest="date_range")
    sp.add_argument("--venues")

    sp = sub.add_parser("paper", help="按 ID 取论文（可多个）")
    common(sp)
    sp.add_argument("--ids", nargs="+", required=True, help="paperId 或 DOI:... 等")

    sp = sub.add_parser("citations", help="被引论文")
    common(sp)
    sp.add_argument("--id", required=True)
    sp.add_argument("--limit", type=int, default=50)
    sp.add_argument("--date-range", dest="date_range")

    sp = sub.add_parser("snippets", help="片段检索")
    common(sp)
    sp.add_argument("--query", required=True)
    sp.add_argument("--limit", type=int, default=10)
    sp.add_argument("--paper-ids", dest="paper_ids", help="逗号分隔")
    sp.add_argument("--venues")
    sp.add_argument("--inserted-before", dest="inserted_before")

    sp = sub.add_parser("authors", help="作者检索")
    common(sp)
    sp.add_argument("--name", required=True)
    sp.add_argument("--limit", type=int, default=10)

    sp = sub.add_parser("author-papers", help="作者论文")
    common(sp)
    sp.add_argument("--author-id", dest="author_id", required=True)
    sp.add_argument("--limit", type=int, default=50)
    sp.add_argument("--paper-fields", dest="paper_fields")

    return p


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass

    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 1

    proxy = None
    auto = False
    if args.no_proxy:
        proxy, auto = None, False
    elif args.auto_proxy:
        auto = True
    elif args.proxy:
        proxy = args.proxy

    try:
        client = AstaClient(api_key=args.api_key, proxy=proxy, auto_proxy=auto,
                             timeout=args.timeout)
        client.connect()
    except AstaRoutingError as exc:
        print("路由失败：%s" % exc, file=sys.stderr)
        return 3
    except AstaError as exc:
        print("连接失败：%s" % exc, file=sys.stderr)
        return 2

    try:
        if args.cmd == "tools":
            for tool in client.list_tools():
                print("%s :: %s" % (tool.get("name"), (tool.get("description") or "")[:120]))
            return 0

        if args.cmd == "search":
            rows = client.search_relevance(args.keyword, limit=args.limit,
                                           fields=args.fields, date_range=args.date_range,
                                           venues=args.venues)
        elif args.cmd == "title":
            rows = client.search_title(args.title, limit=args.limit, fields=args.fields,
                                       date_range=args.date_range, venues=args.venues)
        elif args.cmd == "paper":
            rows = client.get_paper_batch(args.ids, fields=args.fields)
        elif args.cmd == "citations":
            rows = client.get_citations(args.id, limit=args.limit, fields=args.fields,
                                        date_range=args.date_range)
        elif args.cmd == "snippets":
            rows = client.snippet_search(args.query, limit=args.limit, venues=args.venues,
                                          paper_ids=args.paper_ids,
                                          inserted_before=args.inserted_before)
        elif args.cmd == "authors":
            rows = client.search_authors(args.name, limit=args.limit, fields=args.fields)
        elif args.cmd == "author-papers":
            rows = client.get_author_papers(args.author_id, limit=args.limit,
                                            paper_fields=args.paper_fields)
        else:
            parser.print_help()
            return 1
    except AstaError as exc:
        print("调用失败：%s" % exc, file=sys.stderr)
        return 3

    _save(rows, args.out)
    if not args.out:
        print(json.dumps(rows, ensure_ascii=False, indent=2)[:4000])
    print("共 %d 条。" % len(rows), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
