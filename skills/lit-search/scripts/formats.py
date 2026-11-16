# -*- coding: utf-8 -*-
"""薄导出层：把统一记录导出为 .bib / .ris / .apa / GB/T 7714 文本。

定位说明（非一等公民）
----------------------
本模块只做「记录 → 字符串」的一次性导出，不含正文引用编号、重编号、
幽灵引用清理、引文校验、Word/LaTeX 排版；这些属于下游 agent / 其它 skill。

- BibTeX：优先使用上游 S2 返回的 citationStyles.bibtex；缺失时用极简回退生成器。
- RIS：通用交换格式（TY/AU/TI/JO/PY/DO/UR/AB ...）。
- APA：单条参考文献字符串。
- GB/T 7714-2015：顺序编码制参考文献表；中文文献用「等」与全角标点，
  英文文献用 "et al." 与半角标点；缺失字段只告警不编造。

Python 3.7+，仅标准库。
"""

from __future__ import print_function

import re

# Crossref / S2 类型 → BibTeX entry type
BIBTEX_TYPE = {
    "journal-article": "article",
    "proceedings-article": "inproceedings",
    "book": "book",
    "book-chapter": "incollection",
    "dissertation": "phdthesis",
    "posted-content": "misc",
    "report": "techreport",
    "report-component": "techreport",
    "standard": "techreport",
    "dataset": "misc",
    "preprint": "misc",
    "conference": "inproceedings",
    "conference-paper": "inproceedings",
    "journal": "article",
    "review": "article",
    "article": "article",
    "thesis": "phdthesis",
    "book-chapter": "incollection",
}

RIS_TYPE = {
    "article": "JOUR",
    "inproceedings": "CONF",
    "book": "BOOK",
    "incollection": "CHAP",
    "phdthesis": "THES",
    "techreport": "RPRT",
    "misc": "GEN",
    "preprint": "GEN",
}


def _cjk(text):
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def _doi(rec):
    return (rec.get("externalIds") or {}).get("DOI") or ""


def _authors(rec):
    out = []
    for a in rec.get("authors") or []:
        name = (a.get("name") or "").strip()
        if name:
            out.append(name)
    return out


def _type_key(rec):
    """推断记录类型键（article / inproceedings / book / phdthesis / misc）。"""
    ptypes = [str(t).lower() for t in (rec.get("publicationTypes") or [])]
    if any("thesis" in t or "dissertation" in t for t in ptypes):
        return "phdthesis"
    if any("conference" in t or "proceedings" in t for t in ptypes):
        return "inproceedings"
    if any("book" in t for t in ptypes):
        return "book"
    if any("preprint" in t or "posted" in t for t in ptypes):
        return "misc"
    if any("report" in t for t in ptypes):
        return "techreport"
    if any("journal" in t or "article" in t for t in ptypes):
        return "article"
    venue = (rec.get("venue") or "").lower()
    if "preprint" in venue or "arxiv" in venue:
        return "misc"
    if rec.get("volume") or rec.get("issue") or rec.get("pages"):
        return "article"
    return "article"


def _bib_author(name):
    """'John Smith' → 'Smith, John'；'张三' → '张三'。"""
    if _cjk(name) or " " not in name.strip():
        return name.strip()
    parts = name.strip().split()
    last = parts[-1]
    first = " ".join(parts[:-1])
    return "%s, %s" % (last, first)


def _bib_key(rec, used):
    authors = _authors(rec)
    base = "anon"
    if authors:
        base = re.sub(r"[^A-Za-z]", "", authors[0].split()[-1]).lower() or "anon"
    title_word = ""
    for w in re.findall(r"[A-Za-z]+", rec.get("title") or ""):
        if w.lower() not in ("the", "a", "an", "of", "on", "and", "in"):
            title_word = w.lower()
            break
    year = rec.get("year") or "nd"
    key = "%s%s%s" % (base, year, title_word)
    candidate, suffix = key, ord("a")
    while candidate in used:
        candidate = "%s%s" % (key, chr(suffix))
        suffix += 1
    used.add(candidate)
    return candidate


def _bib_escape(text):
    text = str(text or "")
    text = text.replace("\\", "\\textbackslash{}")
    for ch, rep in (("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"),
                     ("_", "\\_"), ("{", "\\{"), ("}", "\\}")):
        text = text.replace(ch, rep)
    return text


def fallback_bibtex(records):
    """极简 BibTeX 生成器（上游未提供 citationStyles 时使用）。"""
    out = []
    used = set()
    for rec in records or []:
        styles = rec.get("citationStyles") or {}
        if styles.get("bibtex"):
            out.append(styles["bibtex"].strip())
            continue
        key = _bib_key(rec, used)
        etype = BIBTEX_TYPE.get(_type_key(rec), "misc")
        fields = []
        authors = _authors(rec)
        if authors:
            fields.append(("author", " and ".join(_bib_author(a) for a in authors)))
        if rec.get("title"):
            fields.append(("title", _bib_escape(rec["title"])))
        if etype == "article":
            if rec.get("venue"):
                fields.append(("journal", _bib_escape(rec["venue"])))
        elif etype == "inproceedings":
            if rec.get("venue"):
                fields.append(("booktitle", _bib_escape(rec["venue"])))
        elif etype == "phdthesis":
            if rec.get("venue"):
                fields.append(("school", _bib_escape(rec["venue"])))
        if rec.get("year"):
            fields.append(("year", str(rec["year"])))
        if rec.get("volume"):
            fields.append(("volume", str(rec["volume"])))
        if rec.get("issue"):
            fields.append(("number", str(rec["issue"])))
        if rec.get("pages"):
            pages = str(rec["pages"]).replace("-", "--")
            fields.append(("pages", pages))
        if _doi(rec):
            fields.append(("doi", _doi(rec)))
        if rec.get("url"):
            fields.append(("url", rec["url"]))
        body = ",\n".join("  %s = {%s}" % (k, v) for k, v in fields)
        out.append("@%s{%s,\n%s\n}" % (etype, key, body))
    return "\n\n".join(out)


def to_bibtex(records):
    return fallback_bibtex(records)


def to_ris(records):
    """RIS 交换格式。"""
    chunks = []
    for rec in records or []:
        etype = _type_key(rec)
        lines = ["TY  - %s" % RIS_TYPE.get(etype, "GEN")]
        for name in _authors(rec):
            lines.append("AU  - %s" % name)
        if rec.get("title"):
            lines.append("TI  - %s" % rec["title"])
        venue = rec.get("venue") or ""
        if venue:
            if etype == "article":
                lines.append("JO  - %s" % venue)
            else:
                lines.append("T2  - %s" % venue)
        if rec.get("year"):
            lines.append("PY  - %s" % rec["year"])
        if rec.get("publicationDate"):
            lines.append("DA  - %s" % rec["publicationDate"])
        if rec.get("volume"):
            lines.append("VL  - %s" % rec["volume"])
        if rec.get("issue"):
            lines.append("IS  - %s" % rec["issue"])
        pages = str(rec.get("pages") or "")
        if pages:
            if "-" in pages:
                start, end = pages.split("-", 1)
                lines.append("SP  - %s" % start)
                lines.append("EP  - %s" % end)
            else:
                lines.append("SP  - %s" % pages)
        if _doi(rec):
            lines.append("DO  - %s" % _doi(rec))
        if rec.get("url"):
            lines.append("UR  - %s" % rec["url"])
        if rec.get("abstract"):
            lines.append("AB  - %s" % rec["abstract"].replace("\n", " "))
        lines.append("ER  - ")
        chunks.append("\n".join(lines))
    return "\n\n".join(chunks) + ("\n" if chunks else "")


def _apa_authors(authors):
    if not authors:
        return "Anonymous"
    rendered = []
    for name in authors:
        if _cjk(name):
            rendered.append(name)
            continue
        parts = name.split()
        last = parts[-1]
        initials = " ".join("%s." % p[0].upper() for p in parts[:-1] if p)
        rendered.append("%s, %s" % (last, initials) if initials else last)
    if len(rendered) == 1:
        return rendered[0]
    if len(rendered) <= 20:
        return ", ".join(rendered[:-1]) + ", & " + rendered[-1]
    return ", ".join(rendered[:19]) + ", ... " + rendered[-1]


def to_apa(records):
    """APA 参考文献字符串（每条一行）。"""
    lines = []
    for rec in records or []:
        authors = _apa_authors(_authors(rec))
        year = rec.get("year") or "n.d."
        title = rec.get("title") or ""
        venue = rec.get("venue") or ""
        head = "%s (%s). %s" % (authors, year, title)
        if not head.endswith("."):
            head += "."
        tail = venue
        vol = rec.get("volume")
        issue = rec.get("issue")
        pages = rec.get("pages")
        locator = ""
        if vol:
            locator = str(vol)
            if issue:
                locator += "(%s)" % issue
            if pages:
                locator += ", %s" % pages
        if locator:
            tail = ("%s, %s" % (tail, locator)) if tail else locator
        if _doi(rec):
            link = "https://doi.org/%s" % _doi(rec)
        elif rec.get("url"):
            link = rec["url"]
        else:
            link = ""
        parts = [head]
        if tail:
            parts.append(tail + ".")
        if link:
            parts.append(link)
        lines.append(" ".join(parts).strip())
    return "\n".join(lines) + ("\n" if lines else "")


def _gbt_authors(authors, chinese):
    """GB/T 作者格式：姓 + 名首字母（西文姓氏大写）；>3 人取前 3 + 等/et al."""
    rendered = []
    for name in authors:
        if _cjk(name):
            rendered.append(name)
            continue
        parts = name.split()
        last = parts[-1].upper()
        initials = "".join(p[0].upper() for p in parts[:-1] if p)
        rendered.append("%s %s" % (last, initials) if initials else last)
    if not rendered:
        return "Anonymous"
    if len(rendered) > 3:
        tail = "等" if chinese else "et al"
        return ", ".join(rendered[:3]) + ", " + tail
    return ", ".join(rendered)


def _gbt_marker(rec):
    etype = _type_key(rec)
    venue = (rec.get("venue") or "").lower()
    if etype == "phdthesis":
        return "D"
    if etype == "book":
        return "M"
    if etype == "inproceedings":
        return "C"
    if "preprint" in venue or "arxiv" in venue or etype == "misc":
        return "Z/OL"
    if etype == "techreport":
        return "R"
    return "J"


def to_gbt(records):
    """GB/T 7714-2015 顺序编码制参考文献表。

    返回 (text, warnings)：warnings 列出缺失字段的条目编号，绝不编造。
    """
    lines = []
    warnings = []
    for idx, rec in enumerate(records or [], start=1):
        title = rec.get("title") or ""
        chinese = _cjk(title)
        authors = _gbt_authors(_authors(rec), chinese)
        marker = _gbt_marker(rec)
        year = rec.get("year") or ""
        venue = rec.get("venue") or ""
        doi = _doi(rec)

        if chinese:
            head = "%s. %s[%s]. " % (authors, title, marker)
        else:
            head = "%s. %s[%s]. " % (authors, title, marker)

        if marker == "J":
            tail = ""
            if venue:
                tail += venue
            else:
                warnings.append("[%d] 缺少刊名" % idx)
            if year:
                tail += ", %s" % year
            else:
                warnings.append("[%d] 缺少年份" % idx)
            if rec.get("volume"):
                tail += ", %s" % rec["volume"]
                if rec.get("issue"):
                    tail += "(%s)" % rec["issue"]
                if rec.get("pages"):
                    tail += ": %s" % rec["pages"]
            if doi:
                tail += ". DOI: %s" % doi
            body = head + tail + "."
        elif marker in ("C", "M", "D", "R"):
            body = head
            if venue:
                body += venue
            if year:
                body += ", %s" % year
            if marker == "D" and not venue:
                warnings.append("[%d] 学位论文缺少授予单位" % idx)
            if marker == "M" and not venue:
                warnings.append("[%d] 专著缺少出版者" % idx)
            if doi:
                body += ". DOI: %s" % doi
            body += "."
        else:  # Z/OL 等
            body = head
            if venue:
                body += venue
            if year:
                body += ", %s" % year
            if rec.get("url"):
                body += ". %s" % rec["url"]
            else:
                warnings.append("[%d] 预印本缺少获取路径" % idx)
            if doi:
                body += ". DOI: %s" % doi
            body += "."
        lines.append("%d. %s" % (idx, body))
    return ("\n".join(lines) + ("\n" if lines else ""), warnings)


def export_records(records, fmt):
    """统一分发。返回 (text, warnings)。"""
    fmt = (fmt or "jsonl").lower()
    if fmt in ("bib", "bibtex"):
        return to_bibtex(records), []
    if fmt == "ris":
        return to_ris(records), []
    if fmt == "apa":
        return to_apa(records), []
    if fmt in ("gbt", "gbt7714"):
        return to_gbt(records)
    raise ValueError("不支持的格式：%s" % fmt)
