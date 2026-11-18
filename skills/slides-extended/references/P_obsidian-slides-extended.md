---
UID: 20250208113650
tags: 
aliases: 
description: advanced slides 插件的延续，因为原插件不再维护了
status: planning
modified: 2026-11-14T10:00:00
---

up:: "[[P_Advanced Slides]]"
Related: "[[AS_Grid Component]]"

参考链接：
- 官方 [ebullient/obsidian-slides-extended: Create markdown-based reveal.js presentations in Obsidian](https://github.com/ebullient/obsidian-slides-extended)
    - 论坛 [Slides Extended - Share & showcase - Obsidian Forum](https://forum.obsidian.md/t/slides-extended/85825)
    - [CSS for Presentation Slides - Share & showcase - Obsidian Forum](https://forum.obsidian.md/t/css-for-presentation-slides/12050)提供了很多用于汇报的常见 css
- 第三方
	- [Slides Extended (for Obsidian)](https://all-in-obsidian.li3huo.com/obsidian/slides-extended-for-obsidian/)

# obsidian-slides-extended



> OBAS Assistant 是 [[Johnny]] 开发的插件，未在OB官方的第三方库里面发布
> 
> 
> 还不会使用OBAS Assistant插件的同学，请先看这个视频 https://meeting.tencent.com/cw/lv9GMBnj31
> 
> 
> 录制: OBAS 1.4.1 功能演示
> 录制文件：https://meeting.tencent.com/crm/KmVoLJ6697
> 


## 配置对比

- 新增了 Theme Directory，指定本地主题和样式文件的目录
	- Specify the vault directory for custom themes. Highlight themes should include"highlight" or "hljs" in their name.
	- 什么叫 highlight theme 查看 [Themes — Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/themes/)  ** Highlight Themes define how codeblock elements should look.**
	- the custom theme setting (and these custom themes) should also be in your vault. Not randomly elsewhere 必须放在库当中，而不是其他位置
- 幻灯片部分，增加了是否居中的 Toggle 【Center content】
	- 对应 frontmatter `center: true/false`；设为 `false` 时正文左对齐，但会触发 grid 的 `align-items` 覆盖（见下节）
- 插件部分，按字母排序

## center: false 与 grid align-items

frontmatter 或插件设置 **Center content = 关**（`center: false`）时，Slides Extended 在渲染每个 `<grid>` 的末尾执行：

```javascript
this.isCenter !== void 0 && !this.isCenter && e.addStyle("align-items", "start")
```

（源码：`.obsidian/plugins/slides-extended/main.js`，`getAlignment()` 之后。）

### 现象

- **所有** grid 生成的 flex 容器都会被写入内联 `align-items: start`
- 该值**覆盖**模板上 `align="center"` 映射出的 `align-items`（如封面、目录页标题贴左）
- 与 reveal 整页 `text-align` 无关；影响的是 **grid flex 容器的交叉轴对齐**

### 项目内解法

[`AS_basic.css`](../assets/css/AS_basic.css) 提供 slide class **`grid-align-restore`**：

```css
.reveal .slides section.grid-align-restore div {
    align-items: unset !important;
}
```

- 用 `unset`（**不是** `center`），避免整页回到 `center: true` 效果 — 见 [[P_Advanced Slides#使用技巧]] Issue #133
- 封面、目录等需 grid 居中的 slide 在 `center: false` 下加 class，并配合 **`[[AsTp-Cover]]`** 等模板的 `align="center"`：

```md
<!-- slide id="0" class="grid-align-restore" template="[[AsTp-Cover]]" -->

::: title
# 主标题
:::

::: content
副标题、表格等底部内容
:::

<!-- slide class="grid-align-restore" template="[[ASTp-toc-a]]" -->
```

- `AsTp-Cover` 仅有 `title` / `content` 两槽；勿用 `::: subtitle` / `::: info`（不会进入模板）

### 模板槽内 scrollbox

分栏模板（`::: left` / `::: right`）内宽表、长表溢出时，**不要**在 left 内嵌 `::: block`（会截断 left、内容进 `content`）。两种可行写法见 [AS-Scrollbox.md](AS-Scrollbox.md)：闭合 `:::` 加 `scrollbox-*` class，或槽内 HTML `<div class="scrollbox-*">`。CSS 实现见 `AS_basic.css` §9.5。

`align` 各取值与 `align-items` / `justify-content` 的映射见 [[AS_Grid Component#align]]。

# Docs


https://github.com/ebullient/obsidian-slides-extended/discussions/16 现阶段没有渲染的文档，但是在仓库目录下面的 docs/ 文件夹下面有 md 文档

多看 Discussions 和 Issues

查看 [[P_Advanced Slides#Advanced Slides Documentation]] 下面的子文档，里面 obsidian-slides-extended 额外新增的内容也更新了


## Features

- theme 主题的css 存放在 D:\Markdown directory\.obsidian\plugins\slides-extended\dist\theme
    - 尚未尝试在 skill 的 `assets/css/` 中通过头部 `@import` 导入默认 CSS，再进行二次开发 [css import syntax.md](css%20import%20syntax.md)
- 右上角 【Export as HTML】，现在会导出一个和 presentation 同名的文件夹，下面除了本身的 index.html ，还会把用到的 css 从 ob 库的相对目录下的css，附带相对路径地、完整的复制一份放到这个导出的文件夹下


```
|-- css
|   -- slides-extended.css
|-- dist
|   |-- css
|   |   |-- print
|   |   |-- theme
|   |   |-- layout.scss
|   |   -- reveal.scss
|   |-- fontawesome
|   |   -- all.min.js
|   |-- theme
|   |   |-- fonts
|   |   |-- beige.css
|   |   |-- black-contrast.css
|   |   |-- black.css
|   |   |-- blood.css
|   |   |-- consult.css
|   |   |-- dracula.css
|   |   |-- league.css
|   |   |-- mattropolis.css
|   |   |-- moon.css
|   |   |-- night.css
|   |   |-- serif.css
|   |   |-- simple.css
|   |   |-- sky.css
|   |   |-- solarized.css
|   |   |-- white-contrast.css
|   |   |-- white.css
|   |   -- white_contrast_compact_verbatim_headers.css
|   |-- reset.css
|   |-- reveal.css
|   |-- reveal.esm.js
|   |-- reveal.esm.js.map
|   |-- reveal.js
|   -- reveal.js.map
|-- Extras
|   -- css
|       |-- AS_basic.css
|       -- AS_red.css
|-- plugin
|   |-- audio-slideshow
|   |   |-- plugin.js
|   |   -- recorder.js
|   |-- chalkboard
|   |   |-- img
|   |   |-- plugin.js
|   |   |-- README.md
|   |   -- style.css
|   |-- zoom
|   |   |-- plugin.js
|   |   |-- zoom.esm.js
|   |   -- zoom.js
|   |-- load-mathjax.js
|   -- obsidian-markdown.js
|-- Spaces
|   -- Projects
|       -- Zhihu-Paid & Free
-- index.html
```


## 使用日志


- @2026-08-12 [[Reveal JS#^pandoc]]

### Custom themes 在 Windows 上的路径 Bug

参考链接：
- [#301 Custom CSS theme always 404s on Windows](https://github.com/ebullient/obsidian-slides-extended/issues/301)
- [#97 custom themes are not working](https://github.com/ebullient/obsidian-slides-extended/issues/97)

#301 提供了详细的 root cause 分析：

1. **根因**：`revealRenderer.ts` 中 `toExternalPath()` 使用 `String.replace()` 剥离 vault 路径时，`vaultDirectory` 由模板字符串拼接生成（末尾**正斜杠** `/`），而 `directPath` 由 `path.join` 生成（Windows 上全是**反斜杠** `\`），导致 replace 永不匹配
2. **结果**：完整绝对路径（如 `C:\Users\me\Vault\_Templates\css\theme.css`）被写入 HTML 的 `<link href>` 中 → 浏览器请求 `/C:/Users/.../theme.css` → **404**
3. **内置主题不受影响**：因为 `pluginDirectory` 同样来自 `path.join`（全反斜杠），replace 能匹配成功
4. **级联错误**：theme 404 → `--r-background-color` 未定义 → `isLight()` 报 `TypeError: object null is not iterable` → `ReferenceError: options is not defined`
5. **修复方案**（PR #302 ）：统一两边的路径分隔符（如改用 `path.relative` 而非 string replace），或 `normalise vaultDirectory` 以匹配 `path.join` 的输出

#97 (v2.1.8) 用户反馈设置了 Theme Directory、CSS 文件能在下拉菜单中找到，但加载后只有白底黑字无样式，应为同一 bug 的不同表现 

### `remoteCSS` 的 CSS MIME 类型

`remoteCSS:` 支持远程 CSS URL，但服务端响应的 MIME 类型会影响 WebView 是否按样式表加载。实际测试中：

- `raw.githubusercontent.com` 提供本仓库 CSS 时返回 `Content-Type: text/plain; charset=utf-8`，放入 `remoteCSS:` 后在 Obsidian 中**没有渲染出样式**。
- jsDelivr 返回 `Content-Type: text/css; charset=utf-8`，相同 CSS 可以正常渲染。

因此本库 Slides Extended CSS 的远程引用统一使用 jsDelivr：

```yaml
remoteCSS:
  - https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/slides-extended/assets/css/AS_basic.css
  - https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/slides-extended/assets/css/AS_blue.css
```

若 jsDelivr 不可访问，可将 CSS 复制到 Vault 内并用 `css:` 配置本地相对路径。这里的 MIME 问题不同于上文 Windows `Theme Directory` 的本地路径 404。



