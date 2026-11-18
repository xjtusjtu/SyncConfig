# Slides Extended Reference Index

This skill is self-contained. Supporting notes referenced by the skill live in the local [`references/`](references/) directory. Read only the document needed for the current task; do not load every reference by default.

## How to Use

1. Identify the topic from the index below.
2. Read the matching file under `references/` before using unfamiliar syntax.
3. For fork-specific config (Theme Directory, Windows theme bug, remote CSS), read [P_obsidian-slides-extended.md](references/P_obsidian-slides-extended.md).
4. For AS_basic / SJTU / nav / scrollbox / gallery / CSS slide classes, read [themes/as_basic.md](themes/as_basic.md) first.
5. Use the local reference files in this skill package; do not assume the user's Vault has a particular folder structure.

## Overview and Plugin Context

| Topic | Reference |
|:------|:----------|
| Plugin overview, install, print, tips | [P_Advanced Slides.md](references/P_Advanced%20Slides.md) |
| Slides Extended fork differences, Theme Directory, Windows custom-theme issue, remote CSS | [P_obsidian-slides-extended.md](references/P_obsidian-slides-extended.md) |
| Tips, export, math escaping, CSS combinations | [Advanced Slides 技巧汇总（官方文档补充）.md](references/Advanced%20Slides%20技巧汇总（官方文档补充）.md) |
| Training notes | [20230930140743-AS训练.md](references/20230930140743-AS训练.md) |
| CSS `@import` patterns | [css import syntax.md](references/css%20import%20syntax.md) |

## Basic and Extended Syntax

| Topic | Reference |
|:------|:----------|
| Callouts (`data-type`, blank/noborder; multi-line image pitfall) | [AS_Callouts.md](references/AS_Callouts.md) |
| Horizontal and vertical slide separators | [AS-Horizontal Vertical Slides.md](references/AS-Horizontal%20Vertical%20Slides.md) |
| Element annotations (`<!-- element ... -->`) | [AS-Element Annotations.md](references/AS-Element%20Annotations.md) |
| Slide annotations (`<!-- .slide: ... -->`) | [AS-Slide Annotations.md](references/AS-Slide%20Annotations.md) |
| Block comments (`::: block`) | [AS-Block Comments.md](references/AS-Block%20Comments.md) |
| Slide backgrounds | [AS-Slide Backgrounds.md](references/AS-Slide%20Backgrounds.md) |
| Speaker notes | [AS-Speaker Notes.md](references/AS-Speaker%20Notes.md) |
| Slide animation (`data-auto-animate`) | [AS-Slide Animation.md](references/AS-Slide%20Animation.md) |
| Icons | [AS-Icons.md](references/AS-Icons.md) |
| Emojis | [AS-Emojis.md](references/AS-Emojis.md) |
| Charts | [AS-Charts support.md](references/AS-Charts%20support.md) |
| Excalidraw embeds | [AS-Excalidraw support.md](references/AS-Excalidraw%20support.md) |

## Features, Layouts, and Configuration

| Topic | Reference |
|:------|:----------|
| Embed slides | [AS_Embed Slides.md](references/AS_Embed%20Slides.md) |
| Templates and `defaultTemplate` | [AS-Templates.md](references/AS-Templates.md) |
| Split layout (`<split>`) | [AS_Split Component.md](references/AS_Split%20Component.md) |
| Frontmatter options | [AS_Frontmatter Options.md](references/AS_Frontmatter%20Options.md) |
| Built-in plugins (Menu, Chalkboard, Laser Pointer, etc.) | [AS_Plugins.md](references/AS_Plugins.md) |
| Scroll containers and `gallery` | [AS-Scrollbox.md](references/AS-Scrollbox.md) |
| Mermaid configuration and text-layout issues | [AS_Mermaid.md](references/AS_Mermaid.md) |
| Grid layout (`<grid drag drop>`) | [AS_Grid Component.md](references/AS_Grid%20Component.md) |
| Fragments | [AS-Fragments.md](references/AS-Fragments.md) |
| Fragmented lists | [AS-Fragmented list.md](references/AS-Fragmented%20list.md) |
| Inline styling and custom CSS | [AS-Inline Styling.md](references/AS-Inline%20Styling.md) |
| Native section nav bar (`<nav>` + slide `id` anchors) | [AS_Section Nav Bar.md](references/AS_Section%20Nav%20Bar.md) |
| List grid columns (`list-grid`, `list-grid--*`) | [css_AS_Grid Listi网格列表.md](references/css_AS_Grid%20Listi网格列表.md) — demo in [AS_Basic Showcase](showcase/AS_Basic%20Showcase.md) |
| Flex step lists (`list-flex-row` / `list-flex-col` / `list-flex-step`) | [css_AS列表横向、纵向逐步显示.md](references/css_AS列表横向、纵向逐步显示.md) — demo in [AS_Basic Showcase](showcase/AS_Basic%20Showcase.md) |
| Block 2-column grid (`g-columns`) | [css_AS_任何内容服从两列网格布局.md](references/css_AS_任何内容服从两列网格布局.md) |
| Card grid lists | [themes/as_basic.md](themes/as_basic.md) § List card grid — demo in [AS_Basic Showcase](showcase/AS_Basic%20Showcase.md) |

## AS_basic CSS

Full section map, class catalogs, and SJTU navigation workflow are in [themes/as_basic.md](themes/as_basic.md) § AS_basic.css Section Map.

CSS sources: [`assets/css/AS_basic.css`](assets/css/AS_basic.css), [`assets/css/AS_red.css`](assets/css/AS_red.css) or [`assets/css/AS_blue.css`](assets/css/AS_blue.css) (mutually exclusive), and [`assets/css/AS_SJTU.css`](assets/css/AS_SJTU.css). Load hosted CSS with the jsDelivr URLs documented in [themes/as_basic.md](themes/as_basic.md) § CSS Load Order; use local `css:` paths if remote loading is unavailable.

## ASTp Layout Templates

Templates live in [`assets/templates/`](assets/templates/) (prefix `ASTp-` / `AsTp-`). They provide structural layouts migrated from Marp Antai layout classes; pair them with `AS_basic.css` or the default reveal theme.

Full demo: [AS_Basic Showcase](showcase/AS_Basic%20Showcase.md).

### Column and Row Layouts

**Flexible-height path:** use a slide class plus Block Comment panels — see [themes/as_basic.md](themes/as_basic.md) § Panel layouts. Top/heading uses `auto`; bottom or left/right bands use `1fr`. With navigation, use `template="[[ASTp-nav-shell]]" class="rows-1-2"`.

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

Do not use `::: left` without a template. Panel classes: `ldiv`, `rdiv`, `mdiv`, `tdiv`, `bdiv` and their `*img` variants.

**ASTp Grid templates** use fixed percentage-based drag boxes:

| Template | Variables |
|:---------|:----------|
| [`ASTp-grid-cols2.md`](assets/templates/ASTp-grid-cols2.md) | `left`, `right` |
| [`ASTp-grid-cols-3.md`](assets/templates/ASTp-grid-cols-3.md) | `left`, `middle`, `right` |
| [`ASTp-grid-cols2-73.md`](assets/templates/ASTp-grid-cols2-73.md) | `left`, `right` |
| [`ASTp-grid-cols2-64.md`](assets/templates/ASTp-grid-cols2-64.md) | `left`, `right` |
| [`ASTp-grid-cols2-37.md`](assets/templates/ASTp-grid-cols2-37.md) | `left`, `right` |
| [`ASTp-grid-cols2-46.md`](assets/templates/ASTp-grid-cols2-46.md) | `left`, `right` |
| [`ASTp-grid-lr.md`](assets/templates/ASTp-grid-lr.md) | `left`, `right`; `trans_a` / `trans_b` |
| [`AsTp-tb.md`](assets/templates/AsTp-tb.md) | Legacy; use CSS `rows-2` |
| [`AsTp-top-splitHalves.md`](assets/templates/AsTp-top-splitHalves.md) | Legacy; use CSS `rows-1-2` |

`ASTp-grid-rows-*` and `ASTp-nav-grid-rows-1-2` were removed; use CSS `rows-2` / `rows-1-2` / `rows-2-1` (and `ASTp-nav-shell` when navigation is needed).

List columns: `list-grid` — see [themes/as_basic.md](themes/as_basic.md). Card matrix: `list-card-grid`. Use `<split wrap>` in the body only; see [AS_Split Component.md](references/AS_Split%20Component.md).

### Cover and Special Pages

| Template | Variables |
|:---------|:----------|
| [`AsTp-Cover.md`](assets/templates/AsTp-Cover.md) | `title`, optional `subtitle`, `content`; add `class="grid-align-restore cover"` when `center: false` |
| [`ASTp-toc-a.md`](assets/templates/ASTp-toc-a.md) | `toc_a`: optional `title`, `items` |
| [`ASTp-toc-b.md`](assets/templates/ASTp-toc-b.md) | `toc_b`: optional `header`, `items` |
| [`ASTp-fixedtitle.md`](assets/templates/ASTp-fixedtitle.md) | `fixedtitleB`: `title`, `body` |
| [`ASTp-footnote.md`](assets/templates/ASTp-footnote.md) | `footnote`: `body`, `note` |
| [`ASTp-lastpage.md`](assets/templates/ASTp-lastpage.md) | `lastpage`: optional `title`, `contacts` |

### Navigation Shell Templates

| Template | Body layout | Blocks |
|:---------|:------------|:-------|
| [`ASTp-nav-shell.md`](assets/templates/ASTp-nav-shell.md) | Full-width | `header`, `footer`, body → `content` |
| [`ASTp-nav-grid-lr.md`](assets/templates/ASTp-nav-grid-lr.md) | 50 / 50 | `header`, `footer`, `left`, `right` |
| [`ASTp-nav-grid-cols2-64.md`](assets/templates/ASTp-nav-grid-cols2-64.md) | 55 / 40 | `header`, `footer`, `left`, `right` |
| [`ASTp-nav-grid-tb.md`](assets/templates/ASTp-nav-grid-tb.md) | Top / bottom | `header`, `footer`, `top`, `content` |
| Rows `1-2` with navigation | Use `ASTp-nav-shell` + `class="rows-1-2"` | Panels via `::: block` + `tdiv`/`ldiv`/`rdiv` |

For SJTU navigation decks, see [themes/as_basic.md](themes/as_basic.md) for CSS load order, navigation templates, header/footer, scrollbox, and slide classes.

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

Scrollable content inside template slots (`::: left` / `::: right`): see [AS-Scrollbox.md](references/AS-Scrollbox.md).

- Close the slot with `::: <!-- element class="scrollbox-x" -->` to keep titles fixed while overflowing table/image/pre/Mermaid content scrolls.
- Wrap partial content in `<div class="scrollbox-y">` inside the slot for lists or isolated blocks.
- `gallery` is independent: use `::: <!-- element class="gallery" -->` or `<div class="gallery">` for a horizontal strip of images, Mermaid, or SVG; do not use a callout for multi-line images.
- Do not nest `::: block` inside `::: left`; the parser treats it as a sibling template slot and content falls into `<% content %>`.

## External Official Documentation

Use official documentation when local references are insufficient:

- [Slides Extended GitHub](https://github.com/ebullient/obsidian-slides-extended) — source docs in the repository's `docs/` folder
- [Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/) — syntax is largely compatible; the brand was renamed to Slides Extended
- [reveal.js config](https://revealjs.com/config/) — additional frontmatter parameters
