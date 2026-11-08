#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取 .docx 中的 Word 批注（comments），供 agent 阅读和分析。

用法:
    python docx_comments.py 稿件.docx            # Markdown 报告
    python docx_comments.py 稿件.docx --json     # JSON（含回复树）
    python docx_comments.py 稿件.docx --text     # 批注内联进正文的全文
    python docx_comments.py a.docx b.docx        # 可传多个文件

仅用标准库，Python 3.7+。
"""
import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET


# ------------------------------------------------------------------ 基础工具

def _local(elem):
    return elem.tag.rsplit('}', 1)[-1] if isinstance(elem.tag, str) else ''


def a(elem, local_name):
    """按 local name 取属性，规避 w14 / w15 / w16cid 命名空间版本差异。"""
    for key, val in elem.attrib.items():
        if key.rsplit('}', 1)[-1] == local_name:
            return val
    return None


def _text_of(elem, keep_deleted=True):
    """把一个 w:p / w:comment 内的文字按顺序拼出来。"""
    out = []
    for node in elem.iter():
        name = _local(node)
        if name == 't' or (keep_deleted and name == 'delText'):
            out.append(node.text or '')
        elif name == 'tab':
            out.append('\t')
        elif name in ('br', 'cr'):
            out.append('\n')
    return ''.join(out)


def _story_parts(z):
    """正文 + 页眉页脚 + 脚注尾注：批注可能锚定在其中任何一处。"""
    names = set(z.namelist())
    extra = sorted(n for n in names
                   if n.startswith('word/')
                   and (n.split('/')[-1].startswith(('header', 'footer'))
                        or n.split('/')[-1] in ('footnotes.xml', 'endnotes.xml'))
                   and n.endswith('.xml'))
    return [n for n in ['word/document.xml'] + extra if n in names]


# ------------------------------------------------------------------ 锚点扫描

def _scan_story(z, part):
    """返回 (anchors, paragraphs)。

    anchors: {comment_id: {'anchor': 被批注的文字, 'para': 段落序号(1 起)}}
    paragraphs: [(序号, 段落文字), ...]，按文档顺序跨部件累加
    """
    root = ET.fromstring(z.read(part))
    anchors, paragraphs = {}, []
    open_ids, buffers = [], []

    for p in root.iter():
        if _local(p) != 'p':
            continue
        number = len(paragraphs) + 1
        buf = []
        for node in p.iter():
            name = _local(node)
            if name == 'commentRangeStart':
                open_ids.append(a(node, 'id'))
                buffers.append([])
            elif name == 'commentRangeEnd':
                cid = a(node, 'id')
                if cid in open_ids:
                    pos = open_ids.index(cid)
                    text = ''.join(buffers.pop(pos)).strip()
                    del open_ids[pos]
                    if cid not in anchors or (text and not anchors[cid]['anchor']):
                        anchors[cid] = {'anchor': text, 'para': number}
            elif name == 'commentReference':
                cid = a(node, 'id')
                if cid:
                    anchors.setdefault(cid, {'anchor': '', 'para': number})
            elif name in ('t', 'delText'):
                txt = node.text or ''
                buf.append(txt)
                for b in buffers:
                    b.append(txt)
            elif name == 'tab':
                buf.append('\t')
                for b in buffers:
                    b.append('\t')
            elif name in ('br', 'cr'):
                buf.append('\n')
                for b in buffers:
                    b.append('\n')
        paragraphs.append((number, ''.join(buf).strip()))

    return anchors, paragraphs


# ------------------------------------------------------------------ 批注主体

def _para_ids(comment):
    ids = []
    for p in comment.iter():
        if _local(p) == 'p':
            pid = a(p, 'paraId')
            if pid:
                ids.append(pid)
    return ids


def _read_opt(z, name):
    return ET.fromstring(z.read(name)) if name in z.namelist() else None


def _read_sidecars(z):
    """commentsExtended（已解决 / 回复关系）与 commentsIds（durableId）。"""
    done, parent_of, durable = {}, {}, {}

    ext = _read_opt(z, 'word/commentsExtended.xml')
    if ext is not None:
        for ex in ext.iter():
            if _local(ex) != 'commentEx':
                continue
            pid = a(ex, 'paraId')
            if not pid:
                continue
            done[pid] = (a(ex, 'done') or '').lower() in ('1', 'true', 'on')
            parent = a(ex, 'paraIdParent')
            if parent:
                parent_of[pid] = parent

    ids_root = _read_opt(z, 'word/commentsIds.xml')
    if ids_root is not None:
        for ci in ids_root.iter():
            if _local(ci) != 'commentId':
                continue
            pid, did = a(ci, 'paraId'), a(ci, 'durableId')
            if pid and did:
                durable[pid] = did

    return done, parent_of, durable


def extract(path):
    """返回 {'file', 'comments'(顶层批注含 replies), 'paragraphs'}"""
    with zipfile.ZipFile(path) as z:
        if 'word/comments.xml' not in z.namelist():
            return {'file': path, 'comments': [], 'paragraphs': []}

        anchors, paragraphs = {}, []
        for part in _story_parts(z):
            got, paras = _scan_story(z, part)
            for cid, info in got.items():
                if info['anchor'] or cid not in anchors:
                    anchors[cid] = info
            paragraphs.extend(paras)

        done, parent_of, durable = _read_sidecars(z)
        context = dict(paragraphs)

        body = ET.fromstring(z.read('word/comments.xml'))
        raw = []
        for c in body.iter():
            if _local(c) != 'comment':
                continue
            cid = a(c, 'id')
            pids = _para_ids(c)
            last = pids[-1] if pids else None
            info = anchors.get(cid, {})
            number = info.get('para')
            raw.append({
                'id': cid,
                'author': a(c, 'author') or '',
                'initials': a(c, 'initials') or '',
                'date': a(c, 'date') or '',
                'anchor': info.get('anchor', ''),
                'context': context.get(number, ''),
                'paragraph': number,
                'text': _text_of(c).strip(),
                'resolved': done.get(last, False) if last else False,
                'durableId': durable.get(last, '') if last else '',
                '_paraId': last,
                '_parent': parent_of.get(last) if last else None,
                'replies': [],
            })

        by_para = {}
        for r in raw:
            if r['_paraId']:
                by_para[r['_paraId']] = r

        top = []
        for r in raw:
            parent = by_para.get(r['_parent']) if r['_parent'] else None
            if parent is not None and parent is not r:
                parent['replies'].append(r)
            else:
                top.append(r)
        for r in raw:
            r.pop('_paraId', None)
            r.pop('_parent', None)

        return {'file': path, 'comments': top, 'paragraphs': paragraphs}


def _numbered(nodes, prefix=''):
    """按 1 / 1.1 / 1.1.1 的顺序给整棵树编号，返回 (label, node)。"""
    for i, node in enumerate(nodes, 1):
        label = '%s.%d' % (prefix, i) if prefix else str(i)
        yield label, node
        for item in _numbered(node.get('replies') or [], label):
            yield item


# ------------------------------------------------------------------ 输出

def to_markdown(data):
    items = data['comments']
    name = os.path.basename(data['file'])
    if not items:
        return '# 批注：%s\n\n（该文档没有批注）\n' % name

    flat = list(_numbered(items))
    resolved = sum(1 for _, n in flat if n['resolved'])
    lines = [
        '# 批注：%s' % name,
        '',
        '共 %d 条批注线程（含回复 %d 条），其中 %d 条已标记为已解决。'
        % (len(items), len(flat), resolved),
        '',
    ]

    for label, node in flat:
        depth = label.count('.')
        head = '#' * min(2 + depth, 6)
        bits = [label, node['author'] or '未知作者', (node['date'] or '')[:10]]
        if node['resolved']:
            bits.append('已解决')
        lines.append('%s %s' % (head, ' · '.join(b for b in bits if b)))
        lines.append('')
        if depth == 0:
            if node['anchor']:
                lines.append('- 原文（第 %s 段）：%s' % (node['paragraph'], node['anchor']))
            else:
                lines.append('- 原文：（无文本锚点，可能贴在图片、表格或已删内容上）')
            if node['context'] and node['context'] != node['anchor']:
                lines.append('- 所在段落：%s' % node['context'])
        lines.append('- 批注：%s' % node['text'].replace('\n', ' '))
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def to_text(data):
    """把批注内联到正文对应段落末尾，便于通读上下文。"""
    marks = {}
    for label, node in _numbered(data['comments']):
        if node.get('paragraph'):
            marks.setdefault(node['paragraph'], []).append(
                '[批注%s｜%s：%s]' % (label, node['author'] or '?',
                                   node['text'].replace('\n', ' ')))
    out = []
    for number, text in data['paragraphs']:
        tag = ''.join(marks.get(number, []))
        out.append(text + ('  %s' % tag if tag else ''))
    return '\n\n'.join(out) + '\n'


def main(argv):
    files = [x for x in argv if not x.startswith('-')]
    if not files:
        sys.stderr.write(__doc__)
        return 2
    mode = 'json' if '--json' in argv else ('text' if '--text' in argv else 'md')
    rc = 0
    for f in files:
        try:
            data = extract(f)
        except (zipfile.BadZipFile, KeyError, ET.ParseError) as e:
            sys.stderr.write('无法解析 %s：%s（.doc 需先另存为 .docx）\n' % (f, e))
            rc = 1
            continue
        if mode == 'json':
            sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        elif mode == 'text':
            sys.stdout.write(to_text(data))
        else:
            sys.stdout.write(to_markdown(data))
    return rc


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8')
        except Exception:
            pass
    sys.exit(main(sys.argv[1:]))
