---
UID: 20260708010500
tags:
  - Obsidian
  - plugin
aliases:
  - AS scrollbox
description: Slides Extended 模板槽（left/right）内溢出滚动的两种写法与反模式
status: developing
modified: 2026-09-20T09:56:00
---

up:: [[P_Advanced Slides]]
Related:
	- "[[AS-Block Comments]]"
	- "[[AS-Templates]]"
	- "[[AS-Element Annotations]]"
	- "[[AS_Mermaid]]"
	- "[[AS_Basic Showcase]]"

[toc]

参考链接：
- Marp 侧同类用法：[[Marp_Basic Showcase#滚动容器]]（`<!-- AGENT: layout=scrollbox-y -->` 等）
- CSS 实现：`AS_basic.css` §9.5 Scroll containers、§8.1 Table fit
- 演示：[[AS_Basic Showcase#table-fit — 字号随容器缩放]]

# AS-Scrollbox

Slides Extended（Advanced Slides 语法）中，宽表、长表、宽图等超出 grid 分栏边界时，须在 **scroll target**（table、pre、`.mermaid` 等）上触发 `overflow`，不能依赖 `.academia table` 自身的 `overflow-x`（无效）。`AS_basic.css` 提供 `.scrollbox` / `.scrollbox-x` / `.scrollbox-y`：容器为 flex 纵列、`overflow: hidden`；**标题、段落、列表固定**，table / 图 / 代码 / Mermaid 等占剩余空间并在溢出时出现滚动条。

## CSS 类选型

| 类 | 滚动发生在 | 典型场景 |
|:---|:---|:---|
| `scrollbox` | 内部 target 双向 | 代码块、混合重内容 |
| `scrollbox-x` | 内部 target 横向 | 列数多、策略名长的 `.academia` 表 |
| `scrollbox-y` | 内部 target 纵向 | 行数多的结果表 |
| `table-fit` | **不滚动**（缩表格字号） | 常与 `scrollbox-*` 叠用；见下方 [table-fit](#table-fit) |
| `as-no-scale` | **不滚动**（仅取消 mermaid SVG 撑满缩放） | 与 `scrollbox-*` 联用：按初始字号显示，溢出由 scrollbox 出条。见 [[AS_Mermaid#as-no-scale]] |
| `gallery` | 容器横滚（子项横排） | 图 / SVG / mermaid 等长廊；**独立于** `scrollbox-*`；**宽高由作者控制**（`\|w\|` / element style） |


`scrollbox-x` / `scrollbox` 内 table 为完整 `display: table` + `width: max-content`，由**容器**横滚（勿把 `thead`/`tbody` 拆成独立 table，否则列宽会对不齐）。`scrollbox-y` 内 table 为 `width: 100%`，由容器纵滚；`.academia` 下常用 `table-layout: fixed`。

宽 mermaid 要**初始字号 + 滚动条**时，加 `as-no-scale`（写法 A / B 均可），并在 mermaid 中设 `useMaxWidth: false`。该类只取消 SVG 撑满缩放，不含 overflow。见 [[AS_Mermaid#as-no-scale]]。

**Chrome（不滚）**：`h1–h6`、`p`（非纯图段落）、`ul`、`ol`、`blockquote`、`hr`。

**Scroll target（占剩余空间）**：`table`、`pre`、`.mermaid`、`iframe`、`video`、`.image-container`、`figure`、纯图 `p:has(> img:only-child)`。

## gallery

独立类（`AS_basic.css` §9.6）：大块内容**横排 + 容器横滚**，不与 `scrollbox-x` 联用。子项含 `img` / `figure` / `.mermaid` / `svg` / `iframe` / `video`。标题写在容器外。多行 `![]()` / `![[]]` 合法（无 callout 截断问题）。宽高由作者指定（`![](…|1550)`、`<!-- element style="width: …" -->` 等）；**只给一边时另一边 `auto` + `object-fit: contain`，等比例缩放**（覆盖插件默认的 `object-fit: fill`）。详见 [[AS_Callouts#坑：多行图片会截断 callout]]。

```markdown
::: block

![](./a.svg)
![](./b.svg)
![](./c.svg)

::: <!-- element class="gallery" -->
```

或写法 B：`<div class="gallery">…</div>`。

## table-fit

`AS_basic.css` §8.1：给容器加 `.table-fit`，内部 `table` 的字号随容器剩余空间（`cqh` / `cqw`）缩放。容器须有高度链（常与 `scrollbox-*` 叠用，如 `class="scrollbox-y table-fit"`）。

### 与 scrollbox 的分工

| | scrollbox | table-fit |
|:--|:--|:--|
| 问题 | 内容超出容器 | 默认字号偏大，一屏信息密度低 |
| 手段 | `overflow` 出滚动条 | 按容器尺寸缩 `font-size` |
| 结果 | 能滚完看全表 | 同屏多看几行/列；仍溢出则继续滚 |

有滚动条仍要调 `table-fit`：滚动只保证「能看完」，不保证「一屏可读」。默认字号下长表可能要滚很多屏；调小字号提高密度，滚动距离变短，讲演时一屏信息更够用。二者互补，不是二选一。

### `--as-table-fit-rows` / `--as-table-fit-cols`

填的是**假定行数 / 列数**（预算分母），**不是**字号。

```text
font-size = clamp(min, min(100cqh / rows, 100cqw / cols), max)
```

含义：假定表大约有 `rows` 行、`cols` 列，把容器高/宽均分，取更紧的一侧作字号，再夹在 `--as-table-fit-min` / `--as-table-fit-max` 之间。

| 自定义属性 | 默认 | 含义 | 调大效果 |
|:-----------|:-----|:-----|:---------|
| `--as-table-fit-rows` | `12` | 行数预算 | 字更小 |
| `--as-table-fit-cols` | `8` | 列数预算 | 字更小 |
| `--as-table-fit-min` | `0.55em` | 字号下限 | — |
| `--as-table-fit-max` | `1em` | 字号上限 | — |

宜略大于真实行列。写法示例与演示见 [[AS_Basic Showcase#table-fit — 字号随容器缩放]]。

## 写法 A：闭合 `:::` 加 element annotation

将 `scrollbox-*` 加在 **模板槽结束行** 的闭合 `:::` 上。CSS 把槽内标题/说明留在上方，仅让 table 等 scroll target 占剩余空间并滚动。与 [[AS-Block Comments#闭合 annotation]] 技巧一致。

> **导出 DOM 注意**：nav-grid 模板展开后，槽内是 `div.block` 直接包 markdown 内容（无 `.as-body` 中间层）。闭合 annotation 应把 class 落到 `.block` 上；若导出 HTML 里注释仍残留为 `<!-- .element: class="scrollbox-*" -->` 而未进入 class，请改用写法 B。

Mermaid 按初始字号显示须另加 `useMaxWidth: false`（[[AS_Mermaid#as-no-scale]]）；`scrollbox-x as-no-scale` 的写法 A / 写法 B 均有效。

```markdown
<!-- slide template="[[ASTp-nav-grid-cols2-64]]" class="academia" -->

::: header
…
:::

::: footer
…
:::

::: left

### Condition 2: 用户问优惠国补

完整估计结果（按 ATE 降序）

| 策略 | treated/control | ATE | 95% CI / 状态 |
| … | … | … | … |

:::  <!-- element class="scrollbox-x" -->

::: right

![](./assets/c2_bar.png)

:::
```

- 适用：分栏内「标题 + 宽表/长表」——标题固定，表横/纵滚
- 无需在槽内再包 `<div class="scrollbox-*">`

## 写法 B：HTML `div` 包裹（nav-grid 槽内推荐）

在 `::: left` **内部**用显式 HTML，只包需要滚动的部分：

```markdown
::: left

### Condition 2: 用户问优惠国补

<div class="scrollbox-y">

| 策略 | treated/control | ATE | 95% CI / 状态 |
| … | … | … | … |

</div>

:::
```

- 适用：写法 A 无效时、或需把 table + 说明列表一起滚动的场景
- 长表优先 `scrollbox-y`；宽表用 `scrollbox-x`
- **高度**：默认由 `AS_basic.css` 从 grid 栏高向下传递（`block` → `scrollbox` flex 链），全屏/窗口模式均适用；**勿依赖 `vh` 设 `max-height`**（Reveal 缩放 slide 后 `vh` 与栏内可用高度不一致）。仅当某页 CSS 高度链仍失效时，才可在该页写法 B 加 inline `max-height` 作页面级兜底

## 限制

- 栏内 **长 ul/ol** 默认不滚动，超出可能被裁切；需滚动时用写法 B 包住列表。
- 同一栏 **多个** table 会平分剩余高度，各自带滚动条。

## 反模式

### 不要在 `::: left` 内嵌 `::: block`

`::: 名称` 同时用于 **模板变量**（`left` / `right` / `header` …）与 **Block Comment 分组**（`::: block`）。解析器按 **slide 级平级** 切分，不会把 `::: left` 内的 `::: block` 当作嵌套 styling wrapper：

```markdown
::: left
### 标题
::: block        ← 此处终止 left，开启名为 block 的新槽
| 表格 |
:::
:::
```

- 模板若无 `<% block %>`，表格等内容落入 `<% content %>`（常显示在错误区域）
- 详见 [[AS-Block Comments#模板槽与 block 的冲突]]、[[AS-Templates#模板槽平级解析与 scrollbox]]

### 不要给 `.academia table` 单独加 overflow

overflow 在 **scrollbox 容器**上：`table` 保持完整 `display: table`（`scrollbox-x` 用 `width: max-content` 撑开）。勿把 `table` 设成 `display: block` 再让 `thead`/`tbody` 各自 `display: table`——会变成两张独立表，表头与表体同列宽不一致。

### 双栏 nav 页勿用 legacy 无 header 槽模板

带 `::: header` / `::: footer` 的页应使用 `ASTp-nav-grid-cols2-64` 等（chain `ASTp-nav-shell`），勿用仅含 `content` / `left` / `right` 的 `AsTp-lText6-rImg4`，否则 header/footer 会进 `content`。

## 示例 deck

[[20260706195116_wei_pre]] — Condition 2 结果页（写法 A，`scrollbox-x`）。
