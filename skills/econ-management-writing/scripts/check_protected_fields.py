#!/usr/bin/env python3
"""Compare literal inventories, without certifying meaning or scholarly validity."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


NUMBER = re.compile(
	r"(?<![\w])[-+−]?(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)"
	r"(?:[eE][-+]?\d+)?(?:\\?%|％)?"
)
CITATION = re.compile(
	r"\\(?:cite[A-Za-z]*|[Cc]ite[A-Za-z]*|autocite|parencite|textcite)"
	r"\*?(?:\s*\[[^\]]*\]){0,2}\s*\{([^{}]+)\}"
)
CROSS_REFERENCE = re.compile(
	r"\\(?:label|ref|eqref|autoref|[cC]ref|pageref)\*?\s*\{([^{}]+)\}"
)
MATH = re.compile(
	r"\$\$.*?\$\$|(?<!\\)\$(?!\$).*?(?<!\\)\$|\\\(.*?\\\)|\\\[.*?\\\]"
	r"|\\begin\{(?:equation|align|gather|multline|displaymath|math)\*?\}"
	r".*?\\end\{(?:equation|align|gather|multline|displaymath|math)\*?\}",
	re.DOTALL,
)


def inventory(text: str) -> dict[str, Counter[str]]:
	"""Return protected literal counts from a text passage; parsing is approximate."""
	citations: Counter[str] = Counter()
	for match in CITATION.finditer(text):
		citations.update(key.strip() for key in match.group(1).split(",") if key.strip())
	return {
		"numeric_tokens": Counter(NUMBER.findall(text)),
		"latex_citation_keys": citations,
		"latex_cross_reference_commands": Counter(
			match.group(0) for match in CROSS_REFERENCE.finditer(text)
		),
		"literal_math_blocks": Counter(match.group(0) for match in MATH.finditer(text)),
	}


def compare(original: str, revised: str) -> dict:
	"""Report inventory changes and explicit limits; never certify semantic identity."""
	before, after = inventory(original), inventory(revised)
	differences = {}
	for category in before:
		removed = before[category] - after[category]
		added = after[category] - before[category]
		if removed or added:
			differences[category] = {
				"removed": dict(sorted(removed.items())),
				"added": dict(sorted(added.items())),
			}
	return {
		"status": "inventory_changes" if differences else "no_inventory_changes",
		"differences": differences,
		"semantic_equivalence_verified": False,
		"scope": "Literal inventory screen only; not a manuscript approval gate.",
		"manual_review_required": [
			"Claim ownership of numbers, citations, and mathematical expressions.",
			"Negation, causal strength, construct definitions, units, and scope.",
			"Citation support, numeric interpretation, and evidence for new content.",
		],
		"limitations": [
			"Identical inventories can accompany materially different meanings.",
			"Patterns are incomplete and do not parse arbitrary TeX or native documents.",
			"Authorized expansion, deletion, translation, or reformatting may change inventories.",
		],
	}


def main() -> int:
	"""Read two UTF-8 inputs and emit a read-only comparison as JSON."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("original", type=Path)
	parser.add_argument("revised", type=Path)
	args = parser.parse_args()
	try:
		result = compare(
			args.original.read_text(encoding="utf-8"),
			args.revised.read_text(encoding="utf-8"),
		)
	except (OSError, UnicodeError) as error:
		print(json.dumps({"status": "input_error", "error": str(error)}, ensure_ascii=False))
		return 2
	print(json.dumps(result, ensure_ascii=False, indent=2))
	return 1 if result["differences"] else 0


if __name__ == "__main__":
	raise SystemExit(main())
