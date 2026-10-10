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

`cover_f` / `lead` follows each theme's palette: basic uses muted red, blue uses
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
- `cover_f`（别名 `lead`）= 左对齐深色渐变封面 / 章节过渡页（配色令牌 `--color-cover-*`）
- 封面字号入口：主标题 `--font-size-cover-title`、正文 `--font-size-cover-body`、副标题 `--foot-size-subtitle`（`cover_a`–`cover_e` 共用，子主题可覆盖）
- Opt-in 变体：`th_fill` 表头填充主题强调色；`quote_mark` 引用框改回「引号装饰」样式（默认引用框为浅底 + 左侧强调色粗边框）
- `zebra_bar`：顶部 9px 主题强调色条（`--color-much`）；三套主题默认均不显示，可与其他布局 class 组合

## Key Pitfalls

| Issue | Fix |
|:------|:----|
| Cover/toc/lastpage shows page number | `<!-- _paginate: "" -->` on that slide |
| scrollbox-y not scrolling in column | Put scrollbox **before** blockquote |
| Centered image | Alt text ending in `C`: `![C](image.svg)` |
| Want the old quote look | Add `<!-- _class: quote_mark -->` to that slide |
| Filled table header | Add `<!-- _class: th_fill -->` to that slide |
| HTML layouts broken | Confirm `markdown.marp.enableHtml: true` |
| Hold-to-peek on decorative images | 按住正文 `img` / `.mermaid > svg` 可放大预览；装饰图加 `class="as-no-peek"`（header/footer 图默认不触发） |

Per-slide directives (`_header`, `_footer`, etc.) → see [SKILL.md](../SKILL.md).

## Authoritative Reference (lazy-load)

| Need | File |
|:-----|:-----|
| 类名、令牌、scrollbox、布局与可复制 slide（唯一权威） | [showcase/Marp_Basic Showcase.md](../showcase/Marp_Basic%20Showcase.md) |

Search Showcase for `<!-- AGENT: layout=` comments to find working Marp slide snippets.
