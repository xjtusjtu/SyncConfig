# -*- coding: utf-8 -*-
"""docx-comments skill 回归测试：python tests/test_docx_comments.py"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'scripts'))

import docx_comments as dc  # noqa: E402

FIXTURE = os.path.join(HERE, 'fixture.docx')


def main():
    data = dc.extract(FIXTURE)
    threads = data['comments']

    assert len(threads) == 3, '顶层批注应为 3 条，实际 %d' % len(threads)

    flat = list(dc._numbered(threads))
    assert len(flat) == 4, '含回复应为 4 条，实际 %d' % len(flat)
    assert sum(1 for _, n in flat if n['resolved']) == 1, '应有 1 条已解决'

    first = threads[0]
    assert first['author'] == '张三'
    assert first['anchor'] == '这句话需要修改，因为逻辑不通。'
    assert '后续文字继续' in first['context']
    assert first['paragraph'] == 2
    assert len(first['replies']) == 1
    assert first['replies'][0]['author'] == '王五'

    second = threads[1]
    assert second['resolved'] is True
    assert second['anchor'] == '短句'

    third = threads[2]
    assert third['anchor'] == '', '无 range 的批注锚点应为空'
    assert third['context'] == '第三段，批注贴在整段上。'

    md = dc.to_markdown(data)
    assert '共 3 条批注线程（含回复 4 条）' in md
    assert '### 1.1 · 王五' in md

    text = dc.to_text(data)
    assert '[批注1｜张三：这里论证跳跃' in text

    # 无批注的文档不应抛异常
    empty = os.path.join(HERE, '_empty.docx')
    import zipfile
    with zipfile.ZipFile(empty, 'w') as z:
        z.writestr('word/document.xml',
                   '<w:document xmlns:w="http://schemas.openxmlformats.org/'
                   'wordprocessingml/2006/main"><w:body/></w:document>')
    try:
        assert dc.extract(empty)['comments'] == []
    finally:
        os.remove(empty)

    print('ok')


if __name__ == '__main__':
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding='utf-8')
        except Exception:
            pass
    main()
