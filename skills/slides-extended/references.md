# Slides Extended Reference Index

Vault documentation for Obsidian **Slides Extended** (reveal.js). Read files **on demand** — do not copy content into skill files or invent syntax.

Base directory: `Sources/Equipments/PPT/Advanced Slides/`

## How to Use

1. Identify the topic from the tables below.
2. `Read` the matching vault file before writing or editing that feature.
3. For fork-specific config (Theme Directory, Windows theme bug), also read `P_obsidian-slides-extended.md`.
4. For AS_basic / SJTU / nav / scrollbox / gallery / CSS slide classes, read [themes/as_basic.md](themes/as_basic.md) first.
5. Cross-folder supplements are listed separately — they are referenced from `P_Advanced Slides.md` but live outside the main directory.

## Overview & Plugin Context

| Topic | Vault file |
|:------|:-----------|
| Plugin overview (deprecated MSzturc note, install, print, tips) | `Sources/Equipments/PPT/Advanced Slides/P_Advanced Slides.md` |
| Slides Extended fork differences, Theme Directory, Windows custom theme bug | `Sources/Equipments/PPT/Advanced Slides/P_obsidian-slides-extended.md` |
| Tips, export, math escaping, CSS combos (supplements official docs) | `Sources/Equipments/PPT/Advanced Slides/Advanced Slides 技巧汇总（官方文档补充）.md` |
| Training notes | `Sources/Equipments/PPT/Advanced Slides/20230930140743-AS训练.md` |
| CSS `@import` patterns (generic) | `Sources/Equipments/PPT/Advanced Slides/css import.md` |

## Basic / Extended Syntax

| Topic | Vault file |
|:------|:-----------|
| Callouts (`data-type`, blank/noborder; multi-line image pitfall → use `gallery`) | `Sources/Equipments/PPT/Advanced Slides/AS_Callouts.md` |
| Horizontal / vertical slide separators | `Sources/Equipments/PPT/Advanced Slides/AS-Horizontal Vertical Slides.md` |
| Element annotations (`<!-- element ... -->`) | `Sources/Equipments/PPT/Advanced Slides/AS-Element Annotations.md` |
| Slide annotations (`<!-- .slide: ... -->`) | `Sources/Equipments/PPT/Advanced Slides/AS-Slide Annotations.md` |
| Block comments (`::: block`) | `Sources/Equipments/PPT/Advanced Slides/AS-Block Comments.md` |
| Slide backgrounds | `Sources/Equipments/PPT/Advanced Slides/AS-Slide Backgrounds.md` |
| Speaker notes | `Sources/Equipments/PPT/Advanced Slides/AS-Speaker Notes.md` |
| Slide animation (cross-slide, `data-auto-animate`) | `Sources/Equipments/PPT/Advanced Slides/AS-Slide Animation.md` |
| Icons | `Sources/Equipments/PPT/Advanced Slides/AS-Icons.md` |
| Emojis | `Sources/Equipments/PPT/Advanced Slides/AS-Emojis.md` |
| Charts | `Sources/Equipments/PPT/Advanced Slides/AS-Charts support.md` |
| Excalidraw embed | `Sources/Equipments/PPT/Advanced Slides/AS-Excalidraw support.md` |

## Features / Layouts / Config

| Topic | Vault file |
|:------|:-----------|
| Embed slides | `Sources/Equipments/PPT/Advanced Slides/AS_Embed Slides.md` |
| Templates / `defaultTemplate` | `Sources/Equipments/PPT/Advanced Slides/AS-Templates.md` |
| Split layout (`<split>`) | `Sources/Equipments/PPT/Advanced Slides/AS_Split Component.md` |
| Frontmatter options (full table) | `Sources/Equipments/PPT/Advanced Slides/AS_Frontmatter Options.md` |
| Built-in plugins (Menu, Chalkboard, Laser Pointer, etc.) | `Sources/Equipments/PPT/Advanced Slides/AS_Plugins.md` |
| Antai layout showcase (ASTp templates) | [showcase/AS_Basic Showcase.md](showcase/AS_Basic%20Showcase.md) |
| SJTU nav + AS_basic/AS_red/AS_blue/AS_SJTU theme | [themes/as_basic.md](themes/as_basic.md) |
| Nav shell / cover / trans 等 ASTp 模板用法 | [showcase/AS_Basic Showcase.md](showcase/AS_Basic%20Showcase.md) |
| Scroll containers / **gallery** (img·mermaid strip) in template slots | `Sources/Equipments/PPT/Advanced Slides/AS-Scrollbox.md` |
| List grid columns (`list-grid`, `list-grid--*` modifiers) | `Sources/Program/代码库/css_AS_Grid Listi网格列表.md` — demo in `AS_Basic Showcase.md` §列表分列 |
| Flex step lists (`list-flex-row` / `list-flex-col` / `list-flex-step`) | `Sources/Program/代码库/css_AS列表横向、纵向逐步显示.md` — demo in `AS_Basic Showcase.md` §横排有序步骤图 |
| Card grid lists (`list-card-grid`, modifiers) | [themes/as_basic.md](themes/as_basic.md) § List card grid — demo in `AS_Basic Showcase.md` §卡片矩阵 |
| Block 2-col grid (`g-columns` element class) | `Sources/Program/代码库/css_AS_任何内容服从两列网格布局.md` |

## AS_basic.css Section Map

Full section/line table, class catalogs, and SJTU nav workflow → [themes/as_basic.md](themes/as_basic.md) § AS_basic.css Section Map.

Source CSS: [`assets/css/AS_basic.css`](assets/css/AS_basic.css). Color tokens: [`assets/css/AS_red.css`](assets/css/AS_red.css) or [`assets/css/AS_blue.css`](assets/css/AS_blue.css) (mutually exclusive). Backgrounds: [`assets/css/AS_SJTU.css`](assets/css/AS_SJTU.css). Load via GitHub raw URLs in `remoteCSS:` (see [themes/as_basic.md](themes/as_basic.md) § CSS Load Order).

## ASTp Layout Templates

Templates live in [assets/templates/](assets/templates/) (prefix `ASTp-` / `AsTp-`). Migrated from Marp Antai layout classes — **structure only**, pair with `AS_basic.css` or default reveal theme.

Full demo: [showcase/AS_Basic Showcase.md](showcase/AS_Basic%20Showcase.md)

### Column / row layouts — two paths

**Path B (rows / flexible height):** slide class + Block Comment panels — [themes/as_basic.md](themes/as_basic.md) § Panel layouts. Top/`heading` = `auto`; bottom or left+right band = `1fr`. With nav: `template="[[ASTp-nav-shell]]" class="rows-1-2"`.

```markdown
<!-- slide class="rows-1-2" -->

## Title

::: block
Top full width
::: <!-- element class="tdiv" -->

::: block
Left
::: <!-- element class="ldiv" -->

::: block
Right
::: <!-- element class="rdiv" -->
```

Do **not** use `::: left` without a template (orphan slot). Panels: `ldiv` / `rdiv` / `mdiv` / `tdiv` / `bdiv` (and `*img`).

**Path A — ASTp-grid templates** (fixed `%` drag boxes):

> **勿在 ASTp 模板内用 `<split>`** — 见 `AS-Templates.md`。

| Template | Variables |
|:---------|:----------|
| `assets/templates/ASTp-grid-cols2.md` | `left`, `right` |
| `assets/templates/ASTp-grid-cols-3.md` | `left`, `middle`, `right` |
| `assets/templates/ASTp-grid-cols2-73.md` | `left`, `right` |
| `assets/templates/ASTp-grid-cols2-64.md` | `left`, `right` |
| `assets/templates/ASTp-grid-cols2-37.md` | `left`, `right` |
| `assets/templates/ASTp-grid-cols2-46.md` | `left`, `right` |
| `assets/templates/ASTp-grid-lr.md` | `left`, `right` (1:1); `trans_a` / `trans_b` |
| `assets/templates/AsTp-tb.md` | legacy; use CSS `rows-2` |
| `assets/templates/AsTp-top-splitHalves.md` | legacy; use CSS `rows-1-2` |

`ASTp-grid-rows-*` and `ASTp-nav-grid-rows-1-2` **removed** — use CSS `rows-2` / `rows-1-2` / `rows-2-1` (+ `ASTp-nav-shell` when nav needed).

List columns: `list-grid` — [themes/as_basic.md](themes/as_basic.md). Card matrix: `list-card-grid`. `<split wrap>` in body only: [[AS_Split Component]].

### Cover / special pages (Grid)

| Template | Variables |
|:---------|:----------|
| `assets/templates/AsTp-Cover.md` | `title`, `subtitle?`, `content` — cover; `class="grid-align-restore cover"` when `center: false` |
| `assets/templates/ASTp-toc-a.md` | `toc_a` — `title?`, `items` |
| `assets/templates/ASTp-toc-b.md` | `toc_b` — `header?`, `items` |
| `assets/templates/ASTp-fixedtitle.md` | `fixedtitleB` — `title`, `body` |
| `assets/templates/ASTp-footnote.md` | `footnote` — `body`, `note` |
| `assets/templates/ASTp-lastpage.md` | `lastpage` — `title?`, `contacts` |

### Nav shell templates (SJTU decks)

| Template | Body layout | Blocks |
|:---------|:------------|:-------|
| `assets/templates/ASTp-nav-shell.md` | Full-width | `header`, `footer`, body → `content` |
| `assets/templates/ASTp-nav-grid-lr.md` | 50 / 50 | `header`, `footer`, `left`, `right` |
| `assets/templates/ASTp-nav-grid-cols2-64.md` | 55 / 40 | `header`, `footer`, `left`, `right` |
| `assets/templates/ASTp-nav-grid-tb.md` | Top / bottom | `header`, `footer`, `top`, `content` |
| *(rows-1-2 with nav)* | use `ASTp-nav-shell` + `class="rows-1-2"` | panels via `::: block` + `tdiv`/`ldiv`/`rdiv` |

SJTU nav workflow, CSS load order, header p+ul, scrollbox, slide classes → [themes/as_basic.md](themes/as_basic.md).

Demo deck: [showcase/AS_Basic Showcase.md](showcase/AS_Basic%20Showcase.md).

### Usage (non-nav ASTp layouts)

```markdown
<!-- slide template="[[ASTp-grid-cols2-64]]" -->

::: left
## Section title

Left column content
:::

::: right
Right column content
:::
```

Scrollable content inside template slots (`::: left` / `::: right`): see `Sources/Equipments/PPT/Advanced Slides/AS-Scrollbox.md`.

- **A.** Close the slot with `:::  <!-- element class="scrollbox-x" -->` (titles fixed; table/img/pre/mermaid scroll in remaining space)
- **B.** Wrap partial content in `<div class="scrollbox-y">` inside the slot (lists, isolated blocks)
- **gallery** (independent): `::: <!-- element class="gallery" -->` or `<div class="gallery">` — horizontal strip of img / mermaid / svg; do not use callout for multi-line images

Do **not** nest `::: block` inside `::: left` — parser treats it as a sibling template slot named `block`, and content falls into `<% content %>`.

## Cross-Folder Supplements

Referenced from `P_Advanced Slides.md` but stored elsewhere:

| Topic | Vault file |
|:------|:-----------|
| Grid layout (`<grid drag drop>`) | `Sources/Equipments/PPT/Johnny学OB/AS_Grid Component.md` |
| Fragments (reveal item-by-item) | `Sources/Equipments/PPT/Advanced Slides/AS-Fragments.md` |
| Fragmented lists | `Sources/Equipments/PPT/Advanced Slides/AS-Fragmented list.md` |
| Inline styling / custom CSS | `Sources/Equipments/PPT/Advanced Slides/AS-Inline Styling.md` |

## External Official Docs

Use when vault notes are insufficient:

- [Slides Extended GitHub](https://github.com/ebullient/obsidian-slides-extended) — source docs in repo `docs/` folder
- [Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/) — syntax largely compatible; brand renamed to "Slides Extended"
- [reveal.js config](https://revealjs.com/config/) — additional frontmatter parameters
