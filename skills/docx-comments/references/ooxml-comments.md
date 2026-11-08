# OOXML 批注部件速查

`.docx` = ZIP + XML。批注不是一个整体对象，而是分散在几个部件里，靠 id / paraId 关联。

## 部件一览

| 部件 | 作用 | 关键元素 |
|---|---|---|
| `word/document.xml` | 正文（及表格、内容控件内的段落） | `w:commentRangeStart` / `w:commentRangeEnd` / `w:commentReference` |
| `word/header*.xml`、`word/footer*.xml` | 页眉页脚，批注可锚在其中 | 同上 |
| `word/footnotes.xml`、`word/endnotes.xml` | 脚注尾注 | 同上 |
| `word/comments.xml` | 批注正文与元数据 | `w:comment` |
| `word/commentsExtended.xml` | 回复关系、是否已解决 | `w15:commentEx` |
| `word/commentsIds.xml` | 跨版本稳定标识 | `w16cid:commentId` |
| `word/people.xml` | 作者信息（头像、providerId） | `w15:person` |
| `[Content_Types].xml` | 声明上述部件类型 | `Override` |

## 命名空间

```
w     http://schemas.openxmlformats.org/wordprocessingml/2006/main
w14   http://schemas.microsoft.com/office/word/2010/wordml
w15   http://schemas.microsoft.com/office/word/2012/wordml
w16cid http://schemas.microsoft.com/office/word/2016/wordml/cid
```

同名字符串在不同版本存在差异（`paraId` 早期在 `w14`，`commentEx` 在 `w15`，`commentId` 在 `w16cid`）。脚本按 **local name** 取属性，不绑定前缀。

## 锚点结构

```xml
<w:p>
  <w:commentRangeStart w:id="0"/>
  <w:r><w:t>被批注的这段文字</w:t></w:r>
  <w:commentRangeEnd w:id="0"/>
  <w:r><w:commentReference w:id="0"/></w:r>
</w:p>
```

- `w:id` 与 `comments.xml` 里 `w:comment/@w:id` 对应，取值只需在同一文档内唯一。
- 锚点可以跨段落：`commentRangeStart` 在上一段，`commentRangeEnd` 在下一段 → 需要维护开放栈，逐段落累加文字。
- 只有 `w:commentReference` 没有 range 时，说明锚点没有文本（图片、表格、删除内容），只能记录所在段落。

## 批注本体

```xml
<w:comment w:id="0" w:author="张三" w:initials="ZS" w:date="2026-01-05T10:12:00Z">
  <w:p w14:paraId="0AAA0001"><w:r><w:t>这里论证跳跃。</w:t></w:r></w:p>
</w:comment>
```

批注内部可以有多个段落、列表、甚至图片。`w:date` 为 ISO 8601 UTC。

## 回复与已解决

```xml
<w15:commentsEx>
  <w15:commentEx w15:paraId="0AAA0004" w15:paraIdParent="0AAA0001" w15:done="0"/>
</w15:commentsEx>
```

- `w15:paraId` 指向该批注**最后一个** `w:p` 的 `w14:paraId`（不是批注 id）。
- `w15:paraIdParent` 存在 → 这条是对父批注的回复。
- `w15:done="1"` → 在 Word 里标记为「已解决 / 完成」。

## durableId

```xml
<w16cid:commentsIds>
  <w16cid:commentId w16cid:paraId="0AAA0001" w16cid:durableId="1122334455"/>
</w16cid:commentsIds>
```

`durableId` 在批注被复制、跨版本保存后仍保持稳定，适合做外部系统的批注映射键；`w:id` 会重排。

## 与修订痕迹的区别

| 特征 | 批注 | 修订 |
|---|---|---|
| 元素 | `w:commentRangeStart` 等 | `w:ins` / `w:del` / `w:moveFrom` / `w:moveTo` |
| 作者/时间 | 在 `comments.xml` | 在修订元素属性上 |
| 正文是否改变 | 否，只在正文旁挂注 | 是，插入/删除直接改变正文 |
| 提取 | 本文脚本 | 需另行解析，注意 `w:delText` |

`w:delText` 是「被删除的旧文字」，脚本把它算入锚点文本；如果文档同时开启修订与批注，锚点文本可能长于界面上看到的正文。

## 相关规范

- ECMA-376 Part 1（WordprocessingML）
- MS-DOCX 扩展：`[MS-DOCX]` 中的 `commentsEx`、`commentsIds`、`people`
