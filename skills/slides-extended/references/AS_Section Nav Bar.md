---
UID: 20261115203500
tags:
  - slides
  - reveal
aliases:
  - 原生章节导航栏
  - Section Nav Bar
up: "[[P_Advanced Slides]]"
Related:
  - "[[AS-Inline Styling]]"
  - "[[AS-Slide Annotations]]"
description: 用 HTML `<nav>` + slide id 锚点做章节导航栏；不依赖 AS_basic.css 与 ASTp-nav 模板，reveal.js 会拦截 `a[href^="#"]` 并按 id 跳转
status: developing
modified: 2026-11-15T20:35:00
source:
---

up::

参考链接：
- [reveal.js — Internal links](https://revealjs.com/links/)（官方写法 `href="#/<id>"`）
- [reveal.js 4.6.0 源码 `getIndicesFromHash`](https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reveal.esm.js)
- [Slides Extended GitHub](https://github.com/ebullient/obsidian-slides-extended)

# AS-Section Nav Bar

在正文里放一条**章节导航栏**（原生 HTML `<nav>`），当前章节加粗、其余章节可点击跳转。与 SJTU 的 `::: header` 导航不同，它**不依赖 `AS_basic.css` 与 `ASTp-nav-*` 模板**，任何 reveal.js 风格的 deck 都能用。

## 语法：两件套

### 1. 给目标 slide 加 id

id 必须落在 `<section>`（即 slide）元素上，Slides Extended 用 slide 注解注入：

```markdown
<!-- slide id="discovery" -->

## Module I: iterative situation-tactic discovery
```

### 2. 在正文里放 nav 栏

```html
<nav style="font-size: 0.65em; color: #1769aa; margin-bottom: 28px;"><a href="#discovery">Discovery</a> / <strong>Evaluation</strong> / <a href="#results">Results</a></nav>
```

- 未跳转的章节写 `<a href="#章节 id">名称</a>`；
- **当前章节**写 `<strong>名称</strong>`（不包 `<a>`，不可点）；
- 分隔符随意，惯例用 ` / `。

## 工作原理（reveal.js 源码级）

reveal.js 4.6.0 里：

```js
// 点击拦截：只接管 href 以 # 开头的 <a>
const link = event.target.closest('a[href^="#"]');
if (link) {
    const indices = location.getIndicesFromHash(link.getAttribute('href'));
    if (indices) { slide(indices.h, indices.v, indices.f); event.preventDefault(); }
}

// hash → 目标 slide
getIndicesFromHash(hash) {
    let name = hash.replace(/^#\/?/, "");     // "#id" 与 "#/id" 都能剥掉前缀
    ...
    let el = document.getElementById(decodeURIComponent(name))
                   ?.closest('.slides>section, .slides>section>section');
    if (el) return { ...getIndices(el), f: fragment };
    return null;
}
```

由此可知：

| 事项 | 结论 |
|:-----|:-----|
| `href="#discovery"` | **可用**——前缀 `#` 被剥掉后按 `getElementById` 找 slide |
| `href="#/discovery"` | 官方文档写法，同样可用 |
| id 不存在 / 写错 | `getIndicesFromHash` 返回 `null` → 点击无反应（且 `preventDefault` 不执行，浏览器会尝试跳到页内锚点） |
| 链接是否被 Obsidian 抢先 | raw HTML 里的 `<a>` 不会被 Obsidian 改写 | 写成 Markdown 链接 `[x](#discovery)` 也不行：nav 块内 Markdown 根本不解析 |

## 块内不能用 Markdown 语法

`<nav>` 是**块级 HTML 标签**。当 `<nav …>` 单独起一行时，整个标签块（含内部内容）按 raw HTML 处理，**块内的 Markdown 语法不会被解析**，原样显示。

```html
<!-- ✗ 错：渲染出来是字面量 [d](#discovery)，不会成为链接 -->
<nav style="font-size: 0.65em; color: #1769aa; margin-bottom: 28px;"> [d](#discovery) </nav>
```

正确写法一律用 raw HTML 标签：

```html
<!-- ✓ 对：raw HTML 链接 + <strong> 标当前章节 -->
<nav style="font-size: 0.65em; color: #1769aa; margin-bottom: 28px;"><a href="#discovery">Discovery</a> / <strong>Evaluation</strong> / <a href="#results">Results</a></nav>
```

| 想表达 | ✗ Markdown（无效） | ✓ raw HTML（有效） |
|:-------|:-------------------|:-------------------|
| 跳转链接 | `[d](#discovery)` | `<a href="#discovery">d</a>` |
| 当前章节加粗 | `**Evaluation**` | `<strong>Evaluation</strong>` |
| 分隔符 | ` / `（纯文本可以） | `<span style="color:#999">/</span>`（需改色时用 HTML） |
| 样式 | 无（Markdown 无法写 inline style） | `<nav style="…">` |

> [!note] 连带影响
> 同理，nav 栏里的**图片、脚注、强调、列表**等也都不会被 Markdown 解析；需要就改用对应的 HTML 标签（`<img>`、`<em>`、`<ul><li>`）。

## 样式旋钮

| 属性 | 作用 | 示例值 |
|:-----|:-----|:-------|
| `font-size` | 导航栏字号 | `0.65em`（相对 slide 根字号） |
| `color` | 未跳转章节的颜色 | `#1769aa`（SJTU 蓝） |
| `margin-bottom` | 与下方标题的间距 | `28px` |

分隔符与文字颜色也可以拆开写：`<span style="color:#999">/</span>`。

## 变体

### 章节首页放一条

一般放在**每章第一张 slide** 的标题上方：

```markdown
<!-- slide id="evaluation" -->

<nav style="font-size: 0.65em; color: #1769aa; margin-bottom: 28px;"><a href="#discovery">Discovery</a> / <strong>Evaluation</strong> / <a href="#results">Results</a></nav>

## Module II: evaluate complete response actions
```

### 全局统一样式

nav 栏在每张 slide 里重复写，样式不好改时，用 `<style>` 标签统一控制（`<style>` 对整个 deck **全局生效**，见 [[AS-Inline Styling]]）：

```html
<style>
  nav.secnav { font-size: 0.65em; color: #1769aa; margin-bottom: 28px; }
</style>
```

然后每处写 `<nav class="secnav">…</nav>`。

## 与 SJTU header nav 的区别

| 维度 | 原生 `<nav>` 栏（本篇） | SJTU header nav |
|:-----|:---------------------|:-----------------|
| 位置 | 正文内（自己控制插入点） | 页眉（`::: header` + `ul`） |
| 依赖 | 无（纯 HTML） | `AS_basic.css` + `AS_red/AS_blue.css` + `ASTp-nav-*` 模板 |
| 当前章节标记 | `<strong>` | `==[章节名](#c-N)==`（高亮写法） |
| 适合 | 非 SJTU 主题的学术/汇报 deck | SJTU 主题长 deck |

SJTU 侧的写法见 [themes/as_basic.md](../themes/as_basic.md) § SJTU Nav Deck Structure。

## 坑

| 现象 | 原因 | 处理 |
|:-----|:-----|:-----|
| 点击没反应 | `href` 的 id 与 slide 的 `id` 不一致 / id 不存在 | 两边逐字核对；id 区分大小写 |
| 点击跳到页内某处而非 slide | id 没落在 `<section>` 上 | 用 `<!-- slide id="…" -->` 注入，而不是写在正文标题里 |
| id 重复 | 同一 id 出现在多张 slide | id 全局唯一，建议用章节名（`discovery` / `evaluation` / `results`） |
| 乱码 / 链接变形 | 用 Markdown 链接 `[x](#id)` | 改用 raw HTML `<a href="#id">x</a>`（nav 块内 Markdown 根本不解析） |
| 中文 id | 需 URL 编码，跨环境不稳 | id 一律用 ASCII |
| 预览里点不动 | 编辑视图与演示模式的渲染不同 | 以「演示 / 播放」模式或导出的 HTML 验证 |

## 实战示例

`Spaces/Projects/temp/临时文件.md`（SJTU 蓝主题 deck）用三段式章节导航：`Discovery` → `Evaluation` → `Results`，每章首页一条 nav 栏，当前章节加粗：

```html
<!-- slide id="discovery" -->

<nav style="font-size: 0.65em; color: #1769aa; margin-bottom: 28px;"><strong>Discovery</strong> / <a href="#evaluation">Evaluation</a> / <a href="#results">Results</a></nav>
```

## 相关

- [[AS-Inline Styling]] — `<style>` 全局生效、inline style 写法
- [[AS-Slide Annotations]] — `<!-- slide ... -->` 注解
- [themes/as_basic.md](../themes/as_basic.md) — SJTU nav deck 结构、`==[章节名](#c-N)==` 高亮写法
