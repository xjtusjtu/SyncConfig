---
name: docx-comments
description: "读取并分析 Word (.docx) 中的批注（comments）：作者、时间、被批注的原文、所在段落、已解决状态、回复线程。当用户要求查看/汇总/回应 Word 批注、审阅稿件评审意见、把批注整理成修改清单时使用。不适用于 .doc 旧格式（需先转 .docx）、PDF 注释或修订痕迹（tracked changes）。"
compatibility: opencode
---

# Word 批注提取与审阅

`.docx` 是 ZIP 包，批注存放在 `word/comments.xml`，锚点（批注针对哪句话）在 `word/document.xml` 里。本 skill 用纯标准库脚本把两者拼起来，输出 agent 可直接阅读的 Markdown / JSON，无需 Word、无需 COM。

## 何时使用

- 用户给出 `.docx`，要求看「批注 / 意见 / 评审意见 / 导师批注 / 审稿意见」
- 需要把多人多轮的批注整理成可执行的修改清单
- 需要在改写正文前先确认批注指向的原文

**不适用**

- `.doc`（97-2003 二进制）：先另存为 `.docx`，或用 `soffice --headless --convert-to docx 旧文件.doc`
- PDF 注释（`/Annots`）、Markdown 注释、Excel 批注：结构完全不同
- 修订痕迹（tracked changes，`w:ins` / `w:del`）：本项目脚本只取批注；需要修订时单独解析
- **不要用 pandoc 中转**：`pandoc x.docx -t markdown` 会静默丢弃全部批注（已实测）

## 快速开始

脚本路径（相对仓库根）：`Extras/SyncConfig/skills/docx-comments/scripts/docx_comments.py`

```bash
# 1. 先看全貌：谁批注了什么、多少条、多少已解决
python "Extras/SyncConfig/skills/docx-comments/scripts/docx_comments.py" 稿件.docx

# 2. 需要上下文时：把批注内联进正文，按段落通读
python .../docx_comments.py 稿件.docx --text

# 3. 需要程序处理时：JSON（含回复树、段落号、durableId）
python .../docx_comments.py 稿件.docx --json

# 4. 批量
python .../docx_comments.py 评审稿.docx 终稿.docx
```

脚本自己把 stdout/stderr 切到 UTF-8，Windows 的 GBK 控制台不会乱码。Python 3.7+。

## 输出的含义

Markdown 报告每条批注含：

- `1` / `1.1` / `1.1.1`：线程编号，点号表示回复层级
- 作者 · 日期 · `已解决`（只有 Word 的 `commentsExtended` 里有 `w15:done` 才判得出）
- `原文（第 N 段）`：批注锚点覆盖的文字；空表示锚在图片、表格或已删除内容上
- `所在段落`：整段文字，用于判断批注是否指对了地方
- `批注`：批注正文

JSON 里字段同名：`author` / `date` / `anchor` / `context` / `paragraph`（1 起，全文分段序号）/ `text` / `resolved` / `durableId` / `replies[]`。

## 分析工作流

1. **先跑默认模式**：拿到条数、作者分布、已解决比例，判断这是「少数关键意见」还是「逐句校对」。
2. **再跑 `--text`**：核对每条批注的上下文。批注常省略主语和指代，脱离段落容易误读。
3. **逐条判定**，不要默认批注正确：
   - 成立 / 部分成立 / 不成立 / 信息不足需作者确认
   - 理由要具体（涉及哪句、缺什么证据、与哪条批注冲突）
4. **归类**：结构论证 / 事实与证据 / 表述与文字 / 格式与规范 / 引用与数据。
5. **合并重复**：同一作者在不同位置的同类意见合并成一条规则，避免输出几十条同义项。
6. **处理冲突**：两位审阅者意见相反、或与作者自述矛盾时，单列「需裁决」并给出各自依据，不要自行选边。
7. **输出表格**：`编号 | 原文 | 批注 | 判定 | 建议动作 | 需要作者决定`。原文超过一行时截断并保留段落号。
8. **不擅自改稿**：本 skill 只读 docx。真要改正文，先给修改方案或 diff 建议，等用户确认；改完正文不会自动改批注（批注需在 Word 里处理）。

## 已知坑

- **锚点为空**：批注贴在图片、表格、或修订中已删除的文字上时，`commentRangeStart/End` 之间没有字符。此时靠 `paragraph` + `context` 定位，不要编造原文。
- **页眉页脚 / 脚注里的批注**：脚本已扫这些部件；段落号仍按「正文 + 这些部件」的遍历顺序累加。
- **回复不是独立批注**：回复同样写在 `comments.xml`，靠 `commentsExtended` 的 `paraIdParent` 串树；缺这个部件时回复会退化成平行批注。
- **`已解决` 不一定有**：WPS 或其他工具产出的 docx 可能没有 `commentsExtended.xml`，此时 `resolved` 全为 false，不代表未解决。
- **修订模式**：正文里 `w:del` 的删除文字也算进锚点文本，可能与 Word 界面上看到的不一致。
- **异常文档**：`commentRangeStart` 未闭合时脚本用栈容错，不会崩，但该条锚点可能落在错误段落。
- **文件被 Word 打开**：读取不受影响（`~$xxx.docx` 是锁文件，跳过它）。

## 相关文件

- `scripts/docx_comments.py`：提取脚本（标准库实现，无依赖）
- `tests/fixture.docx`：带 3 条批注、1 条回复、1 条已解决的构造样本
- `tests/test_docx_comments.py`：回归测试，`python tests/test_docx_comments.py` 应输出 `ok`
- `references/ooxml-comments.md`：注释相关 XML 部件与命名空间速查
