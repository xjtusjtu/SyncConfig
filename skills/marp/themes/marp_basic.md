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

`enableHtml` is required for `cols-*`, panel divs, `scrollbox-*`, and Mermaid HTML blocks.

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
cover_a~f → toc_a/b → cols-2/3/rows-* → cols2_* (+ fglass) → scrollbox-y/x → navbar → lastpage
```

- Section class via `<!-- _class: cols-2-64 -->`; content in `<div class="ldiv">` / `rdiv` / etc.
- Left image + right text → `cols-2` + `limg` + `rdiv`
- Old `info` → use `cover_a`
- Transition slide → `trans`
- **封面副标题用 `##`（h2，勿用 `######`）** — `cover_*` / `lastpage` 已按 h2 定型；这样作为普通 Markdown 打开时层级也合理
- `cover_f` = 左对齐深色渐变封面 / 章节过渡页（配色令牌 `--color-cover-*`）
- 封面字号入口：主标题 `--font-size-cover-title`、正文 `--font-size-cover-body`、副标题 `--font-size-cover-subtitle`（`cover_a`–`cover_f` 共用，子主题可覆盖）
- Opt-in 变体：`th_fill` 表头填充主题强调色；`quote_mark` 引用框改回「引号装饰」样式（默认引用框为浅底 + 左侧强调色粗边框）
- `zebra_bar`：顶部 9px 主题强调色条（`--color-much`）；三套主题默认均不显示，可与其他布局 class 组合

## 封面布局模型（cover_a / cover_b / cover_e）

封面遵循三条不变量：

1. **主标题放大时能挤动副标题** — `h1` / `h2` 走正常文档流（`position: static`），
   不使用各自的绝对定位或固定百分比行。`<!-- fit -->` 把 h1 撑高时，h2 自然下移。
2. **标题↔正文的间距由各封面自行决定** — `--gap-cover-body` 在 `:root` 给默认值
   （`3.5em`），`cover_a` 覆盖为 `4em`、`cover_b` / `cover_e` 覆盖为 `3em`。
3. **色块必须与标题匹配** — 色块不是固定高度的装饰层，而是 **h1 / h2 自身的
   `background-color` + `padding`**。标题多高，色块就多高，任何 `<!-- fit -->` 缩放
   都不会露出白边或错位。

标题↔副标题的间距统一由 `--gap-cover-title`（`0.6em`）控制，全封面一致。
相邻两个色块之间用 `--cover-seam`（`3px`）负 margin 轻微重叠，
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

Per-slide directives (`_header`, `_footer`, etc.) → see [SKILL.md](../SKILL.md).

## Authoritative Reference (lazy-load)

| Need | File |
|:-----|:-----|
| 类名、令牌、scrollbox、布局与可复制 slide（唯一权威） | [showcase/Marp_Basic Showcase.md](../showcase/Marp_Basic%20Showcase.md) |

Search Showcase for `<!-- AGENT: layout=` comments to find working Marp slide snippets.
