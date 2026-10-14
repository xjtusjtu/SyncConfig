# Marp Theme: Marp_basic

Brief entry for the Marp_basic Marp theme. Assumes generic Marp syntax from [SKILL.md](../SKILL.md).

## When to Read

Load this file when:

- User sets `theme: Marp_basic` or `theme: Marp_blue`
- User asks for Marp_basic layouts: `cover_*`, `cols-*`, `scrollbox`, `navbar`, `lastpage`, etc.
- Parent `marp` skill delegates via Theme Extensions

Then **lazy-load** the vault Showcase below for class docs and copy-paste slide examples.

## Environment

Register theme CSS in `markdown.marp.themes`. Use the **GitHub raw URL** (any vault can use it directly):

```json
{
  "markdown.marp.themes": [
    "https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/marp/assets/css/Marp_basic.css",
    "https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/marp/assets/css/Marp_blue.css"
  ],
  "markdown.marp.enableHtml": true
}
```

| Theme | CSS |
|:------|:----|
| Marp_basic | [../assets/css/Marp_basic.css](../assets/css/Marp_basic.css) |
| Marp_blue | [../assets/css/Marp_blue.css](../assets/css/Marp_blue.css) (imports Marp_basic + blue tokens) |
| Marp_slate | [../assets/css/Marp_slate.css](../assets/css/Marp_slate.css) — child theme (`@import "Marp_basic"`), see [marp_slate.md](marp_slate.md) |

Local alternative: copy `assets/css/` into the vault and use a vault-relative path instead of the raw URL.

> Fallback: if raw GitHub fails (MIME type rejected), switch to the jsDelivr mirror `https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/marp/assets/css/Marp_basic.css`.

`enableHtml` is required for `cols-*`, panel divs, `scrollbox-*`, `gallery`, and Mermaid HTML blocks.

## Standard Frontmatter

```yaml
---
marp: true
theme: Marp_basic
paginate: true
size: 16:9
header: '![width:130px](logo.png) Organization Name'
footer: '汇报标题'
math: katex
---
```

Blue variant: set `theme: Marp_blue` — an **indigo** palette (accent `#3949ab`), kept
deliberately distinct from `Marp_slate`'s teal accent (`#147d92`); the two were
previously within 5° of each other and read as the same colour.

`cover_f` follows each theme's palette: basic uses muted red, blue uses
indigo (`#141a3a` → `#2a3583`), and slate uses navy → teal (`#113454` → `#155a70`).
Traditional cover color blocks (`cover_a`–`cover_e`) use
`--color-coverbg: var(--color-cover-to)` in all three themes.

## Layout Selection

```
cover_a~f → toc_a/b → cols-2/3/rows-* → cols2_* + list-cols-2 (+ fglass) → scrollbox-y/x → gallery → navbar → lastpage
```

- Section class via `<!-- _class: cols-2-64 -->`; content in `<div class="ldiv">` / `rdiv` / etc.
- **列表样式与分栏正交**：`cols2_ol_sq` / `cols2_ol_ci` / `cols2_ul_sq` / `cols2_ul_ci` 只定义列表长什么样（有序列表方形 / 圆形序号块，无序列表小色块），**默认单列自上而下**；`list-cols-2` 负责拆成两栏（`column-count`，先填满左列 1–3 / 4–6）。两者组合 = 两栏列表，只写 `cols2_*` = 普通单列
- `navbar` 只做顶部导航条（`header` 内写 `***左标题***　**当前**　*其他*`），**正文部分与普通页完全一致**，可与 `cols-2-64` / `cols2_*` / `list-cols-2` / `th_fill` 等任意组合；不再对正文元素加 `margin-top` 偏移
- `gallery`：**长廊容器**（div 类，非 section 类）—— img / Mermaid / iframe / video 横排成一条，超出宽度横向滚动；图片尺寸由作者用 `![w:600]` 控制，标题与说明写在容器外
- Left image + right text → `cols-2` + `limg` + `rdiv`
- Old `info` → use `cover_a`
- Transition slide → `trans`
- **封面副标题用 `##`（h2，勿用 `######`）** — `cover_*` / `lastpage` 已按 h2 定型；这样作为普通 Markdown 打开时层级也合理
- `lastpage`（致谢页）：中部固定高度色带 —— 高度 `--lastpage-band`（默认 `40%`），按「上方留白 1 份 : 下方留白 2 份」分布，色带落在 20%–60%（中心约 40%，略高于页面中线）；标题（`##`）在色带内垂直居中，联系方式贴页面底部居中
- `cover_f` = 左对齐深色渐变封面 / 章节过渡页（配色令牌 `--color-cover-*`）
- 封面字号入口：主标题 `--font-size-cover-title`、正文 `--font-size-cover-body`、副标题 `--font-size-cover-subtitle`（`cover_a`–`cover_f` 共用，子主题可覆盖）
- Opt-in 变体：`th_fill` 表头填充主题强调色；`quote_mark` 引用框改回「引号装饰」样式（默认引用框为浅底 + 左侧强调色粗边框）
- `zebra_bar`：顶部 9px 主题强调色条（`--color-much`）；三套主题默认均不显示，可与其他布局 class 组合
- `fancyhead_1`：一整套 `h1`–`h6` 装饰（h1 居中下划线（宽 = 文字宽度 60%，`--fancyhead-underline-width` 可调） / h2 `#` 前缀 + 整行淡红下划线（`color-mix()` 由强调色 + 页面底色现调，不新增令牌） / h3 左侧竖条 / h4 方框（上边框 4px、其余 2px） / h5、h6 级别标签）；**只改装饰、不改字体字号**，装饰色统一 `--color-strong`，仅作用于 section.fancyhead_1（封面等不受影响）
- `fancyhead_2`：极简风，**只装饰 h1–h3 且全部靠左**（h1 粗下划线 5px，宽 = 文字宽度 60%，随文字缩放并左对齐 / h2 整行极淡细线 1px（`color-mix()` 现调，比例越小越淡） / h3 左侧实心圆点前缀）；h4 及以下保持全局样式，同样**只改装饰、不改字体字号**
- `fancyhead_1r`：**相对级别**标题装饰，按页面起始级别自动分档——有 h2 时 `h2/h3/h4` = 第 1/2/3 级，无 h2 时 `h3/h4/h5` 顶上（第 1 级 = 靠左 + 文字宽度 60% 粗下划线 / 第 2 级 = 左侧竖条 / 第 3 级 = 方框且上边框 4px、其余 2px）；用 `:has(h2)` 与 `:not(:has(h2))` 两个守卫使分支互斥。要求标题**级别连续**、`header`/`footer` 内不放标题；仅作用于 `section.fancyhead_1r`，需 `section.` 前缀（否则 marpit 会加后代关系导致永不匹配）
- `fadehead`：**标题颜色随层级渐淡**——h1 用最深端 `--fadehead-base`（默认 = `--color-h1`），h2–h6 逐级与 `--color-bg` 做 `color-mix()`（90/80/70/60/50%）。**只改颜色**，不动字号 / 字体 / 装饰，可与 `fancyhead_*` 叠加（一方管颜色、一方管线条边框）；未挂该 class 的封面 / `trans` 页不受影响，配色随子主题自动跟随。想更平缓就整体上调那组百分比
- **h1 颜色**：非封面页取 `--color-h1`（默认 = 主题强调色 `--color-much`，可单独调）；
  封面 `cover_a`–`cover_d` / `cover_f` 及 `trans` 页的 h1 落在色块 / 深色底上，改用浅色 `--color-title`；
  `cover_e` 的 h1 在白色一侧，用 `--color-h1`

## Design Tokens

| 令牌 | 默认值 | 用途 |
|:-----|:-------|:-----|
| `--color-h1` | `var(--color-much)` | 非封面页 `h1` 颜色（封面 / `trans` 另用 `--color-title`）；也是 `fadehead` 的默认最深端 |
| `--color-title` | `#fff` | 深色 / 彩色底块上的浅色文字（封面、表头、`trans` 等） |
| `--color-much` | `#864248` | 主题强调色：`h2`/`h3`、标记、`zebra_bar`、`--color-h1` 默认值 |

## 封面布局模型（cover_a / cover_b / cover_e）

`cover_a` 采用 **区域模型**（固定色块 + 居中标题 + 独立信息区）：

1. **色块固定高度** — 顶部色块由 section 背景渐变绘制，高度固定为 `--cover-a-band`
   （默认 `62%`）。加/删副标题、`<!-- fit -->` 放大主标题都不会改变色块大小。
2. **标题区** — `h1`（+ `h2`）作为一个整体在色块内 **垂直居中**（grid 上下两段等分留白，
   随主标题高度自动重新等分）。
3. **信息区** — 下方 `table` 独立占据剩余高度并在其中居中，不受标题增减影响。

`cover_b` / `cover_e` 采用 **匹配模型**（色块随标题伸缩）：

1. **主标题放大时能挤动副标题** — `h1` / `h2` 走正常文档流（`position: static`），
   不使用各自的绝对定位或固定百分比行。`<!-- fit -->` 把 h1 撑高时，h2 自然下移。
2. **标题↔正文的间距由各封面自行决定** — `--gap-cover-body` 在 `:root` 给默认值
   （`3.5em`），`cover_b` / `cover_e` 覆盖为 `3em`。
3. **色块必须与标题匹配** — 色块不是固定高度的装饰层，而是 **h1 / h2 自身的
   `background-color` + `padding`**。标题多高，色块就多高，任何 `<!-- fit -->` 缩放
   都不会露出白边或错位。

标题↔副标题的间距统一由 `--gap-cover-title`（`0.6em`）控制，全封面一致。
`cover_b` 相邻两个色块之间用 `--cover-seam`（`3px`）负 margin 轻微重叠，
消除缩放渲染下两盒边界处的亚像素白缝。

`cover_c` / `cover_d` 仍为 grid 布局（行高固定），其色块由 section 背景渐变承担，
不参与上述模型。`cover_f` 为 flex 流式布局。

## Key Pitfalls

| Issue | Fix |
|:------|:----|
| Cover/toc/lastpage shows page number | `<!-- _paginate: "" -->` on that slide |
| scrollbox-y not scrolling in column | Put scrollbox **before** blockquote |
| Centered image | Alt text ending in `C`: `![C](image.svg)` |
| Want the old quote look | Add `<!-- _class: quote_mark -->` to that slide |
| Filled table header | Add `<!-- _class: th_fill -->` to that slide |
| HTML layouts broken | Confirm `markdown.marp.enableHtml: true` |
| `<!-- fit -->` heading not auto-scaling | Keep `fittingHeader` in the theme's `@auto-scaling` metadata (`@auto-scaling fittingHeader, math, code`); omitting it silently disables `<!-- fit -->` |
| 封面色块比标题窄/宽，或标题溢出右边缘 | 封面 `h1`/`h2` 用 `width: 100%` + 水平 `padding` 时**必须**加 `box-sizing: border-box`，否则按 content-box 计算会超出 1280px |
| 封面 h1/h2 两个色块之间有细白线 | 两个相邻背景盒在缩放渲染下有亚像素缝；给下面那个加 `margin-top: calc(-1 * var(--cover-seam))` |
| `<!-- fit -->` 放大主标题后压住副标题 | 封面 h1/h2 不要各自绝对定位或写死 `top` 百分比；保持正常文档流，让 h2 被自然挤下去 |
| Hold-to-peek on decorative images | 按住正文 `img` / `.mermaid > svg` 可放大预览；装饰图加 `class="as-no-peek"`（header/footer 图默认不触发） |
| 两栏列表变成单列 | 给该页加上 `list-cols-2`：`<!-- _class: cols2_ol_sq list-cols-2 fglass -->`（`cols2_*` 本身只管列表样式） |
| `navbar` 页上下留白异常 / 正文与普通页位置不同 | 不要给 navbar 正文加 `margin-top` 偏移；`navbar` 的 `header` 是 `position: absolute`，不占正文流，正文应与普通页一样在 section 内居中 |

Per-slide directives (`_header`, `_footer`, etc.) → see [SKILL.md](../SKILL.md).

## Authoritative Reference (lazy-load)

| Need | File |
|:-----|:-----|
| 类名、令牌、scrollbox、布局与可复制 slide（唯一权威） | [showcase/Marp_Basic Showcase.md](../showcase/Marp_Basic%20Showcase.md) |

Search Showcase for `<!-- AGENT: layout=` comments to find working Marp slide snippets.
