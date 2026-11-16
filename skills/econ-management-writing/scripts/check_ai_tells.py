#!/usr/bin/env python3
"""Screen a manuscript for template-like writing patterns, without rewriting it.

The checker reports *signals* (locations and categories) that commonly appear in
machine-generated prose. It does not judge scholarly quality, does not certify
authorship, and does not estimate any detector score. Every hit needs a human
judgement: a trained author may legitimately use the same words.

Findings carry a ``signal`` field: ``strong`` categories justify acting on a
single sighting, ``weak`` ones need corroboration in the same passage (see
references/anti-ai-style.md 2.3).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


BIBLIOGRAPHY_HEADING = re.compile(
	r"^\s*(#{0,4}\s*)?(参考文献|引用文献|References|Bibliography|Works Cited)\s*$",
	re.IGNORECASE,
)

CODE_FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
MATH = re.compile(
	r"\$\$.*?\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$|\\\(.*?\\\)|\\\[.*?\\\]"
	r"|\\begin\{(?:equation|align|gather|multline|displaymath|math)\*?\}.*?"
	r"\\end\{(?:equation|align|gather|multline|displaymath|math)\*?\}",
	re.DOTALL,
)
CITATION_COMMAND = re.compile(
	r"\\(?:cite[A-Za-z]*|autocite|parencite|textcite|Cite[A-Za-z]*)\*?"
	r"(?:\s*\[[^\]]*\]){0,2}\s*\{[^{}]*\}"
)
NUMBER = re.compile(
	r"(?<![\w])[-+−]?(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)"
	r"(?:[eE][-+]?)?(?:\\?%|％)?"
)

# P0: credibility risks (vague attribution without a source, absolutes, chat residue)
P0_RULES = {
	"模糊归因": re.compile(
		r"(专家认为|观察者指出|行业报告显示|一些批评者认为|众多研究者(认为|指出)"
		r"|学界普遍认为|业界普遍认为|大量研究表明|Studies show that"
		r"|Experts (believe|agree|argue)|Observers note)"),
	"绝对化断言": re.compile(
		r"(显而易见|毫无疑问|不言而喻|必然导致|完全解决|充分证明|无可争议"
		r"|It's (obvious|undeniable) that|Undoubtedly)"),
	"对话残留": re.compile(
		r"(希望这对您有帮助|当然！|您说得完全正确|请告诉我|这是一个简单的例子"
		r"|I hope this helps|Great question!)"),
	"知识截止声明": re.compile(
		r"(截至(我的|本次|上次)?(知识|训练)?更新|根据我最后的训练更新"
		r"|As of my last update)"),
}

# P1: obvious template signals (filler openers, vague adjectives, meta discourse)
P1_RULES = {
	"填充连接词": re.compile(
		r"(值得注意的是|综上所述|总而言之|总的来说|不难发现|众所周知|毋庸讳言"
		r"|不可否认的是|需要指出的是|归根结底|不难看出"
		r"|It('s| is) (important|worth) (to note|noting)|Notably,|In conclusion,)"),
	"空洞领域套话": re.compile(
		r"(赋能|闭环|抓手|底层逻辑|深度融合|降本增效|协同增效|数字化转型|新质生产力"
		r"|delve into|tapestry|game-changer|paradigm shift|unlock the potential)"),
	"元话语": re.compile(
		r"(本文旨在|本文进行了深入(分析|研究|探讨)|进行了深入(分析|研究)"
		r"|从(表|图)\s*\d*中可以看出|结果表明该方法|取得了显著成效"
		r"|This paper (aims|delves) to|It can be seen from)"),
	"机械三段式": re.compile(
		r"(首先[，,].{0,60}其次[，,].{0,60}最后"
		r"|一方面.{0,60}另一方面.{0,60}(同时|而且)"
		r"|First[,.].{0,60}Second[,.].{0,60}Third[,.])"),
	"模糊量化": re.compile(
		r"(大量研究|大量文献|众多研究|大批研究|绝大多数|大幅提升|显著提升"
		r"|取得了显著|a (large|great) number of studies|significantly outperform)"),
	"否定对比": re.compile(
		r"(不是[^，。；！？\n]{1,24}[，,]\s*而是"
		r"|并非[^，。；！？\n]{1,24}[，,]\s*而是"
		r"|这并不意味着[^。！？\n]{1,30}[。.]\s*[这它]意味着"
		r"|这并不意味着[^。！？\n]{1,30}[，,]\s*而是"
		r"|不仅仅是[^，。；！？\n]{1,24}[，,]\s*(而是|更是)"
		r"|not (just|only)\b[^.?!]{0,60}\b(but|it'?s)\b"
		r"|it'?s not\b[^.?!]{0,60}, it'?s\b)", re.IGNORECASE),
	"格言化表达": re.compile(
		r"(真正的问题(是|在于)|真正重要的|归根结底|说到底|本质上(是|在于)"
		r"|核心在于|更深的(问题|层次)"
		r"|at its core|the real question is|the heart of the matter)", re.IGNORECASE),
	"铺垫式开场": re.compile(
		r"(让我们(深入|来看|一起)|先来看|话说回来|说实话|坦白说|不夸张地说"
		r"|Let's (dive|explore|look)|Here's what you need to know|Without further ado)",
		re.IGNORECASE),
	"反驳无人异议": re.compile(
		r"(我不是说|这并不是主要|有人可能会说|有人也许会|不可否认的是"
		r"|诚然[^，。；\n]{1,20}但是"
		r"|I'?m not saying|This isn'?t (mainly|really))", re.IGNORECASE),
	"赋予重大意义": re.compile(
		r"(标志着[^，。；\n]{1,20}(重要|关键|转折|里程碑|新阶段)"
		r"|彰显(了)?|奠定(了)?[^，。；\n]{1,10}基础"
		r"|凸显(了)?[^，。；\n]{1,12}重要性|具有重要(的)?(理论|实践)意义"
		r"|深刻(变革|转型)|stands as a testament|pivotal moment)", re.IGNORECASE),
	"含糊关联": re.compile(
		r"(与[^，。；\n]{1,16}(密切相关|存在[^，。；\n]{0,4}(关联|联系))"
		r"|在[^，。；\n]{1,12}方面具有[^，。；\n]{0,6}作用"
		r"|associated with|in connection with)", re.IGNORECASE),
	"浅层动名词短语": re.compile(
		r"(通过[^，。；\n]{1,16}(实现|完成|提升|优化|改善)"
		r"|体现了[^，。；\n]{1,16}(的)?(价值|意义)|有助于[^，。；\n]{1,14}|从而使得"
		r"|highlighting|underscoring|showcasing)", re.IGNORECASE),
	"回避简单动词": re.compile(
		r"(作为一个[^，。；\n]{1,16}(的)?(重要)?组成部分"
		r"|充当[^，。；\n]{1,10}(角色|作用)|发挥着[^，。；\n]{1,10}作用"
		r"|serves as|functions as)", re.IGNORECASE),
}

# P2: style polish (verbosity, formatting noise, uniformity)
P2_RULES = {
	"英文高危词": re.compile(
		r"\b(delve|tapestry|realm|beacon|utilize|leverage|pivotal|underscores"
		r"|meticulous|seamless|holistic|actionable|impactful|unpack|bustling"
		r"|ever-evolving|testament to|at its core|deep dive)\w*\b",
		re.IGNORECASE),
	"无主语句式": re.compile(
		r"(进行了(深入)?(分析|研究|探讨|处理|验证|评估)"
		r"|存在[^，。；\n]{0,6}(显著|明显)(的)?(差异|影响|提升|关联)"
		r"|使得[^，。；\n]{1,14}(能够|无法|难以))"),
	"连续转折填充": re.compile(
		r"(此外|同时|另外|然而)[，,][^。；;]{0,40}(此外|同时|另外|然而)[，,]"),
}

# Patterns that justify acting on a single sighting (see anti-ai-style.md 2.3).
STRONG_LABELS = {
	"模糊归因", "绝对化断言", "对话残留", "知识截止声明",
	"否定对比", "单独成段收束", "格言化表达", "铺垫式开场", "反驳无人异议", "赋予重大意义",
}
CLOSER_RE = re.compile(
	r"(这才是|真正(的)?(关键|重要|收获|意义|价值)|这一点(很)?重要|这一区分"
	r"|值得(记住|深思|回味)|说明了一切|这就是答案|这就是关键"
	r"|That'?s the real win|That distinction matters|Let that sink in)")
HEDGE_RE = re.compile(r"(可能|或许|也许|在一定程度上|某种程度上|似乎|大概|未必|不一定)")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

SENTENCE_SPLIT = re.compile(r"(?<=[。！？!?；;])|(?<=[.])\s+(?=[A-Z])")
CJK_OPENERS = re.compile(r"^(本文|本研究|我们|该方法|该研究|一方面|首先|其次|最后|此外|然而|因此|同时)")


def _strip_protected(text: str) -> str:
	"""Remove code, math and citation commands so they are not scanned."""
	text = INLINE_CODE.sub(" ", text)
	text = MATH.sub(" ", text)
	text = CITATION_COMMAND.sub(" ", text)
	return text


def _sentence_start(text: str):
	out = []
	for piece in SENTENCE_SPLIT.split(text):
		piece = (piece or "").strip()
		if not piece:
			continue
		m = CJK_OPENERS.match(piece)
		if m:
			out.append(m.group(1))
			continue
		first = piece.split()[0].lower() if piece.split() else ""
		out.append(first)
	return out


def _signal(label: str) -> str:
	return "strong" if label in STRONG_LABELS else "weak"


def scan(text: str) -> dict:
	"""Return findings grouped by priority; positions are line-based."""
	findings = []
	lines = text.splitlines()
	in_code = False
	in_bibliography = False

	for index, raw in enumerate(lines, start=1):
		if CODE_FENCE.match(raw):
			in_code = not in_code
			continue
		if in_code:
			continue
		if BIBLIOGRAPHY_HEADING.match(raw):
			in_bibliography = True
			continue
		if in_bibliography:
			continue
		line = _strip_protected(raw)
		if not line.strip():
			continue

		for level, rules in (("P0", P0_RULES), ("P1", P1_RULES), ("P2", P2_RULES)):
			for label, pattern in rules.items():
				for match in pattern.finditer(line):
					findings.append({
						"priority": level,
						"signal": _signal(label),
						"category": label,
						"line": index,
						"text": match.group(0)[:60],
					})

		# vague adjectives that sit in a sentence without any number
		for match in re.finditer(
				r"(显著|全面|有效|重要|新颖|鲁棒|深入|重大)", line):
			sentence_start = line.rfind("。", 0, match.start()) + 1
			sentence_end = line.find("。", match.end())
			sentence = line[sentence_start:sentence_end if sentence_end > 0 else len(line)]
			if not NUMBER.search(sentence):
				findings.append({
					"priority": "P1",
					"signal": "weak",
					"category": "空泛形容词（句内无数字）",
					"line": index,
					"text": match.group(0),
				})

		# stacked citations inside one sentence
		cites = CITATION_COMMAND.findall(raw) + re.findall(r"\[\d+\]", raw)
		if len(cites) >= 3:
			findings.append({
				"priority": "P1",
				"signal": "weak",
				"category": "堆叠并列引用（同一句 ≥3 处）",
				"line": index,
				"text": " ".join(cites)[:60],
			})

	# paragraph uniformity
	paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
	if len(paragraphs) >= 5:
		lengths = [len(p) for p in paragraphs]
		mean = sum(lengths) / len(lengths)
		if mean and (max(lengths) - min(lengths)) / mean < 0.5:
			findings.append({
				"priority": "P2",
				"signal": "weak",
				"category": "段落长度过于一致",
				"line": 0,
				"text": "最长 %d / 最短 %d 字符" % (max(lengths), min(lengths)),
			})

	# repeated sentence openings
	for para_no, paragraph in enumerate(paragraphs, start=1):
		starters = _sentence_start(paragraph)
		run = 1
		for a, b in zip(starters, starters[1:]):
			if a == b and a:
				run += 1
				if run >= 3:
					findings.append({
						"priority": "P2",
						"signal": "weak",
						"category": "连续同构句首",
						"line": 0,
						"text": "第 %d 段连续 %d 次以「%s」开头" % (para_no, run, a),
					})
					break
			else:
				run = 1

	# em dash density
	dashes = text.count("—")
	if dashes and len(text) and dashes / (len(text) / 1000.0) > 1:
		findings.append({
			"priority": "P2",
			"signal": "weak",
			"category": "破折号密度偏高",
			"line": 0,
			"text": "每千字 %.1f 个" % (dashes / (len(text) / 1000.0)),
		})

	# bold overuse
	bold = text.count("**") // 2
	if bold > 4:
		findings.append({
			"priority": "P2",
			"signal": "weak",
			"category": "粗体成串",
			"line": 0,
			"text": "%d 处" % bold,
		})

	# one-line closers: a paragraph that is a single short sentence and only asks
	# the reader to pause on a claim it just made
	blocks = []
	current: list[tuple[int, str]] = []
	for index, raw in enumerate(lines, start=1):
		if raw.strip():
			current.append((index, raw))
		elif current:
			blocks.append(current)
			current = []
	if current:
		blocks.append(current)
	for block in blocks:
		body = "\n".join(line for _, line in block).strip()
		if "|" in body or body.startswith("#"):
			continue
		sentences = [s for s in SENTENCE_SPLIT.split(body) if s and s.strip()]
		if len(sentences) != 1:
			continue
		closer = CLOSER_RE.search(body)
		if closer and len(body) <= 40:
			findings.append({
				"priority": "P1",
				"signal": "strong",
				"category": "单独成段收束",
				"line": block[0][0],
				"text": closer.group(0),
			})

	# stacked qualifiers, decorative headings and dashes used as connectors
	for index, raw in enumerate(lines, start=1):
		stripped = _strip_protected(raw)
		hedges = len(HEDGE_RE.findall(stripped))
		if hedges >= 2:
			findings.append({
				"priority": "P2",
				"signal": "weak",
				"category": "限定词堆叠",
				"line": index,
				"text": "%d 个限定词" % hedges,
			})
		if stripped.count("——") >= 2:
			findings.append({
				"priority": "P2",
				"signal": "weak",
				"category": "破折号作连接符",
				"line": index,
				"text": "%d 处" % stripped.count("——"),
			})
		heading = HEADING_RE.match(raw)
		if heading and EMOJI_RE.search(heading.group(2)):
			findings.append({
				"priority": "P2",
				"signal": "weak",
				"category": "装饰性标题",
				"line": index,
				"text": heading.group(2)[:40],
			})

	# a heading restated by the first line of the section
	for position, raw in enumerate(lines):
		heading = HEADING_RE.match(raw)
		if not heading:
			continue
		title = heading.group(2).strip()
		core = re.match(r"[一-鿿]{2,8}|[A-Za-z]{4,}", title)
		if not core:
			continue
		token = core.group(0)
		for follower in lines[position + 1:]:
			if not follower.strip():
				continue
			if HEADING_RE.match(follower):
				break
			cleaned = follower.strip().lstrip("—>-*# ").lstrip()
			if cleaned.startswith(token):
				findings.append({
					"priority": "P2",
					"signal": "weak",
					"category": "标题后重复首句",
					"line": position + 1,
					"text": token,
				})
			break

	counts = {}
	for item in findings:
		counts[item["priority"]] = counts.get(item["priority"], 0) + 1

	return {
		"status": "findings" if findings else "no_findings",
		"counts": counts,
		"findings": findings,
		"scope": (
			"Lexical screen for template-like patterns only; not a quality score, "
			"not an authorship claim, and not a detector score."
		),
		"manual_review_required": [
			"A single hit is not evidence: only signal=strong categories justify "
			"acting alone; weak signals need corroboration in the same passage.",
			"Each hit may be legitimate in context; decide per sentence.",
			"Replacing vague wording must not invent numbers, citations or claims.",
			"Vocabulary, citation attribution and conclusion strength stay protected.",
			"Do not edit quotations, titles, proper nouns or code that contain a "
			"watched phrase, and leave legitimate academic constructions alone.",
		],
	}


def main() -> int:
	"""Read one UTF-8 manuscript and emit a read-only report as JSON."""
	if hasattr(sys.stdout, "reconfigure"):
		sys.stdout.reconfigure(encoding="utf-8")
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("manuscript", type=Path)
	parser.add_argument("--priority", choices=["P0", "P1", "P2", "all"], default="all")
	args = parser.parse_args()
	try:
		text = args.manuscript.read_text(encoding="utf-8")
	except (OSError, UnicodeError) as error:
		print(json.dumps({"status": "input_error", "error": str(error)}, ensure_ascii=False))
		return 2
	result = scan(text)
	if args.priority != "all":
		result["findings"] = [f for f in result["findings"] if f["priority"] == args.priority]
		result["status"] = "findings" if result["findings"] else "no_findings"
	print(json.dumps(result, ensure_ascii=False, indent=2))
	serious = any(f["priority"] in ("P0", "P1") for f in result["findings"])
	return 1 if serious else 0


if __name__ == "__main__":
	raise SystemExit(main())
