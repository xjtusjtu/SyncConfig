# Slides Extended Theme: AS_basic

Brief entry for the vault AS_basic / AS_red / AS_blue / AS_SJTU theme stack. Assumes generic Slides Extended syntax from [SKILL.md](../SKILL.md).

## When to Read

Load this file when:

- User loads [`assets/css/AS_basic.css`](../assets/css/AS_basic.css) (with or without `AS_red` / `AS_blue` / `AS_SJTU`)
- User asks for SJTU nav decks, `ASTp-nav-*` templates, or group-meeting presentation styling
- User needs slide classes: `academia`, `fancy-ol-*`, `fglass`, `list-grid`, `list-flex-*`, `list-card-grid`, `grid-align-restore`, `scrollbox-*`, `gallery`, `on-light-bg`, etc.
- Parent `slides-extended` skill delegates via Theme Extensions

Then **lazy-load** the vault references below for full docs and copy-paste examples.

## CSS Load Order

Register in the frontmatter `remoteCSS:` array. Use the **GitHub raw URLs** below — they work from any vault. (Remote URLs go in `remoteCSS:`; the `css:` array is for vault-local files only.)

**Red theme** — use `AS_red.css`; **blue** — swap in `AS_blue.css` (**not both**).

```yaml
remoteCSS:
  - https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/slides-extended/assets/css/AS_basic.css
  - https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/slides-extended/assets/css/AS_red.css    # OR .../AS_blue.css
  - https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/slides-extended/assets/css/AS_SJTU.css   # optional — auto SJTU backgrounds
```

Local alternative: copy `assets/css/` into the vault and use the `css:` array with vault-relative paths instead.

> Fallback: if raw GitHub fails (MIME type rejected), switch to the jsDelivr mirror `https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/slides-extended/assets/css/AS_basic.css` (returns `Content-Type: text/css`).

| File | Role |
|:-----|:-----|
| [`../assets/css/AS_basic.css`](../assets/css/AS_basic.css) | Layout, typography, header/footer, tables, lists, scrollbox, images |
| [`../assets/css/AS_red.css`](../assets/css/AS_red.css) | Red `:root` color tokens |
| [`../assets/css/AS_blue.css`](../assets/css/AS_blue.css) | Blue `:root` color tokens + `filter` tint on `AS_SJTU.css` backgrounds |
| [`../assets/css/AS_SJTU.css`](../assets/css/AS_SJTU.css) | Auto backgrounds — first slide `SJTU-cover-bg.svg`, others `SJTU-bg1.svg` |

When `AS_SJTU.css` is loaded, **omit** frontmatter `bg:` and slide `bg="..."`. Omit `AS_SJTU.css` if you need per-slide custom backgrounds.

Recommended frontmatter for SJTU nav decks:

```yaml
---
width: 1920
height: 1080
theme: white
center: false
remoteCSS:
  - https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/slides-extended/assets/css/AS_basic.css
  - https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/slides-extended/assets/css/AS_red.css
  - https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/slides-extended/assets/css/AS_SJTU.css
---
```

## AS_basic.css Section Map

Source: `../assets/css/AS_basic.css`. Read the CSS file for selectors; use this table to pick slide classes.

| Section | Lines (approx.) | Capability | Slide class / usage |
|:--------|:----------------|:-----------|:--------------------|
| §0 Tokens | 35–109 | Fonts, `--list-*` / `--list-card-*` variables | `:root` (in CSS, not markdown) |
| §1 Slide shell | 111–117 | Global left text-align | default with `center: false` |
| §2 Typography | 119–166 | Headings / links / caption | `#` cover only; body slides use `##` / `###` |
| §3 Layout | 168–1167 | `ltBlock`, **panel `cols-*`/`rows-*`**, `grid-align-restore`, **`list-grid`** (~491), `list-flex-*`, **`list-card-grid`** (~714), `g-columns` | see [Panel layouts](#panel-layouts), [List grid columns](#list-grid-columns), [List card grid](#list-card-grid) |
| §4 Lists | 1168–1194 | Generic nested ul/ol indent; `.steps` | default list styling |
| §5 Code & math | 1195–1215 | Code block / math layout | — |
| §6 Blockquote / callout | — | Blockquote, mark; callout `data-type` modifiers `blank` / `notitle` / `noborder` | see vault `AS_Callouts.md` |
| §7 Adaptive text | — | Auto via `has-light-background` / `has-dark-background` (body or section) | set by reveal/bg; not manual slide classes |
| §8 Tables | — | `.academia`, `.table-fit` (§8.1) | `class="academia"` |
| §9 Header/Footer | — | `::: header` (p+ul), `::: footer` (3 li); nav-shell body grid **`as-body`** | ASTp-nav templates |
| §9.4 Split scroll | — | Split + scrollbox height chain | pair with `scrollbox-*` in columns |
| §9.5 Scroll | — | `scrollbox`, `scrollbox-x`, `scrollbox-y` | element annotation or `<div class="scrollbox-x">` |
| §9.6 Gallery | — | **`gallery`** — horizontal strip of img / mermaid / svg / etc. (independent of `scrollbox-*`) | `::: <!-- element class="gallery" -->` or `<div class="gallery">` |
| §10 Images | — | `.image-container` framed strip | HTML `<div class="image-container">` |
| §11 Form controls | 2345–2419 | Styled checkboxes | native `<input type="checkbox">` / `- [ ]` |
| §12 Footnotes | 2420–2544 | `sup` counter badges | `[^1]` footnotes; cross-slide numbering is a known issue |
| §13 Fancy lists | 2545–2686 | `fglass`, `fancy-ol-sq`, `fancy-ol-ci` | `class="fglass fancy-ol-sq"` (combinable) |
| §15 Cover | 2687–2811 | `cover` — strip heading pseudo-elements; title/subtitle colors | `class="grid-align-restore cover"` + `AsTp-Cover` |
| §16 Transition | 2812–2920 | `trans_a` / `trans_b` on `ASTp-grid-lr` | `trans_a` vertical line; `trans_b` image clip + white band + accent triangle |
| §14 Local adaptive | 2921–end | `on-light-bg`, `on-dark-bg` nested text | wrap block: `<div class="on-dark-bg">` |

### Panel layouts

Marp-compatible **CSS path** (`AS_basic.css` §3.x): slide class + `::: block` + `<!-- element class="ldiv" -->`. Grid host = bare `section > div` or nav `div.as-body`. Heights: **heading / top = `auto`**; **`cols-*` column band = `auto`** (row height = tallest panel); whole `cols-*` block **vertically centered** (AS align=`left`); **`rows-*` bottom or left+right fill = `1fr`**.

| Slide class | Areas |
|:------------|:------|
| `cols-2` | heading + left/right (`auto`, equal = max content) |
| `cols-3` | heading + left/middle/right (`auto`, equal = max content) |
| `cols-2-73` / `64` / `37` / `46` | heading + proportional columns (`auto` band) |
| `rows-2` | heading + top (`auto`) + bottom (`1fr`) |
| `rows-1-2` | heading + top (`auto`) + left/right (`1fr`) |
| `rows-2-1` | heading + left/right (`auto`) + bottom (`1fr`) |

Panel classes: `ldiv` `rdiv` `mdiv` `tdiv` `bdiv`. **Do not** use `::: left` without a template. `ASTp-grid-rows-*` / `ASTp-nav-grid-rows-1-2` removed — use these classes (+ `ASTp-nav-shell` for nav). Column templates: `ASTp-grid-cols*` / `ASTp-grid-lr`. Demo → `AS_Basic Showcase.md`.

### grid-align-restore

Plugin injects `align-items: start` on all grids when `center: false`, overriding template `align="center"`. Add slide class on cover and TOC:

```markdown
<!-- slide id="0" class="grid-align-restore cover" template="[[AsTp-Cover]]" -->
```

CSS rule (do not duplicate inline):

```css
.reveal .slides section.grid-align-restore div {
    align-items: unset !important;
}
```

Details → `Sources/Equipments/PPT/Advanced Slides/P_obsidian-slides-extended.md`.

### List grid columns

CSS source: `../assets/css/AS_basic.css` lines ~491–524 (modifiers ~518–524). Vault note: `Sources/Program/代码库/css_AS_Grid Listi网格列表.md`. Demo → [showcase/AS_Basic Showcase.md](../showcase/AS_Basic%20Showcase.md) §列表分列.

Use slide class **`list-grid`** (+ `list-grid--*` ratio modifiers) to split a list into columns. **Do not** use `<split wrap>` inside ASTp templates — each `::: 槽` becomes one `div.block`; see `AS-Templates.md`.

> **DOM paths**（`AS_basic.css`）：无模板 `section > div > ul|ol`；模板槽 `> div > .block > ul|ol`；nav-shell 正文 `div.as-body > ul|ol`（模板 `<grid class="as-body">`）。`<% content %>` 为占位符，**不**对应任何 CSS class。

| Modifier class | Grid columns |
|:---------------|:-------------|
| *(none — `list-grid` only)* | 2 × `1fr` |
| `list-grid--1-2` | `1fr 2fr` |
| `list-grid--2-1` | `2fr 1fr` |
| `list-grid--3` | 3 × `1fr` |
| `list-grid--1-2-1` | `1fr 2fr 1fr` |
| `list-grid--1-1-2` | `1fr 1fr 2fr` |
| `list-grid--2-1-1` | `2fr 1fr 1fr` |
| `list-grid--4` | 4 × `1fr` |

Multiple classes on one slide (space-separated):

```markdown
<!-- slide class="fglass list-grid fancy-ol-sq" -->

## Section title

1. Item one
2. Item two
3. Item three
4. Item four
```

Combine with §13 fancy list classes (`fglass`, `fancy-ol-sq`, `fancy-ol-ci`) for Marp Antai-style panels. See `Advanced Slides 技巧汇总（官方文档补充）.md`.

**Element class `g-columns`** — two-column grid for **any block content** (not list-specific). Close a `::: block` with element annotation:

```markdown
::: block

![|400](image-a.png)
![|400](image-b.png)

::: <!-- element class="g-columns" -->
```

Vault note: `Sources/Program/代码库/css_AS_任何内容服从两列网格布局.md`.

### List card grid

CSS source: `../assets/css/AS_basic.css` lines ~714–1166. Demo → [showcase/AS_Basic Showcase.md](../showcase/AS_Basic%20Showcase.md) §卡片矩阵.

Use slide class **`list-card-grid`** (+ column modifiers `--3` / `--4` + style modifiers) for R×C card matrices. Each top-level list item is one card; rows auto-wrap by item count. Default is **2 columns** (no `--2` class).

> **DOM paths** — same as [List grid columns](#list-grid-columns): `section > div > ul|ol`; template slot `> div > .block > ul|ol`; nav-shell `div.as-body > ul|ol`.

| Modifier | Effect |
|:---------|:-------|
| `list-card-grid` | Base — default **2 columns** |
| `list-card-grid--3` / `--4` | Explicit 3 or 4 columns |
| `list-card-grid--icon` | Unordered — top-level symbol/emoji; nested **bold** = title, plain = body |
| `list-card-grid--ordered` | Ordered — left `01`/`02` counter; use `ol` |
| `list-card-grid--tint` | Pastel background per card (4-color cycle) |
| `list-card-grid--inline` | Marker and title same line; nested list flush with marker |
| `list-card-grid--badge` | Top-centered **hollow ring** on card edge; nested title + body centered |
| `list-card-grid--accent-odd` / `--accent-even` | Top bar color; combine both for row alternation (pair with default 2-col or `--3`) |

**Writing conventions**

| Pattern | Markdown structure |
|:--------|:-------------------|
| `--ordered` (default) | Top-level `**Title**` + nested bullet lines |
| `--icon` | Top-level `- ✓` (or emoji) + **blank line** + nested `**Title**` / body |
| `--badge` | Top-level emoji + **blank line** (→ `<p>`) + nested `**Title**` / body; or emoji as 1st nested li |
| `--inline` + `--ordered` | Top-level `**Title**` + single nested line (title beside counter) |

```markdown
<!-- slide class="list-card-grid list-card-grid--icon" -->

### Card grid with icon marker

- ✓

	- **可用性**
	- 用户能否完成核心任务？
	- 界面提示是否清晰？
```

Combine modifiers on one slide (space-separated), e.g. `list-card-grid list-card-grid--3 list-card-grid--ordered list-card-grid--inline list-card-grid--accent-odd list-card-grid--accent-even`.

## SJTU Nav Deck Structure

```
cover (AsTp-Cover, id="0", class="grid-align-restore cover")
→ TOC (ASTp-toc-a, optional)
→ chapter break (`trans_a` / `trans_b` on `ASTp-grid-lr`, optional)
→ body (ASTp-nav-shell or ASTp-nav-grid-*)
→ closing (ASTp-lastpage)
```

Assign anchors: `<!-- slide id="c-1" ... -->`. Highlight current chapter: `==[章节名](#c-N)==`.

### Header: p + ul

```markdown
::: header
[Deck Short Title](#0)

- [Chapter 1](#c-1)
- ==[Chapter 2](#c-2)==
- [Chapter 3](#c-3)
:::

::: footer
- Presenter / Project
- Deck short title
- Date
:::
```

`p` = left title link; `ul` = right chapter nav. **Do not** use a single `ul` with first `li` as title.

### Nav templates

| Template | Body layout |
|:---------|:--------------|
| `ASTp-nav-shell` | Full-width content |
| `ASTp-nav-grid-lr` | 50/50 `::: left` / `::: right` |
| `ASTp-nav-grid-cols2-64` | 55/40 columns |
| `ASTp-nav-grid-tb` | Top / bottom |
| `ASTp-nav-shell` + `class="rows-1-2"` | Nav + CSS 上+左右（替代已删 `ASTp-nav-grid-rows-1-2`） |

Per-slide: `<!-- slide id="c-2" template="[[ASTp-nav-shell]]" class="academia" -->` — no `defaultTemplate`.

### Slide classes (quick ref)

| Class | Effect |
|:------|:-------|
| `cover` | Cover title style; removes all heading `::before`/`::after` |
| `trans_a` | Center vertical divider on `ASTp-grid-lr` |
| `trans_b` | Three parallel strips: image parallelogram clip + white band (`::before`) + bottom red trapezoid (`::after`) |
| `academia` | Academic table borders/shadows |
| `fancy-ol-sq` | Square numbered list markers |
| `fancy-ol-ci` | Circular numbered list markers |
| `fglass` | Frosted-glass list panel (combine with `fancy-ol-*`) |
| `grid-align-restore` | Restore grid alignment under `center: false` |
| `list-grid` | CSS Grid on slide list — default 2 columns; pair with `list-grid--*` modifiers |
| `list-grid--1-2` / `list-grid--2-1` | 2-column list, unequal width (with `list-grid`) |
| `list-grid--3` (+ `--1-2-1`, `--1-1-2`, `--2-1-1`) | 3-column list ratios (with `list-grid`) |
| `list-grid--4` | 4 equal columns (with `list-grid`) |
| `list-flex-row` | Horizontal flex step list with fragment highlight (element or slide) |
| `list-flex-col` | Vertical flex step list with fragment highlight |
| `list-flex-step` | Horizontal ordered step cards (`01`/`02` counter) |
| `list-card-grid` | Card matrix base — default **2 columns**, rows auto-wrap |
| `list-card-grid--3` | **3 columns** (e.g. 6 items → 2×3, 9 items → 3×3) |
| `list-card-grid--4` | **4 columns** |
| `list-card-grid--icon` | Unordered card grid — top-level symbol/emoji (blank line before nested list); nested **bold** = title, plain = body |
| `list-card-grid--ordered` | Ordered card grid with left counter (with `list-card-grid`, use `ol`) |
| `list-card-grid--tint` | Pastel background per card (4-color cycle, any grid size) |
| `list-card-grid--inline` | Title beside marker (same size); nested list flush with marker start |
| `list-card-grid--badge` | Top-centered emoji **hollow ring** on card edge; nested **title** + body centered. Emoji line needs blank line before nested list (→ `<p>`), or put emoji as 1st nested li |
| `list-card-grid--accent-odd` | Top bar primary color; alone → all cards same color |
| `list-card-grid--accent-even` | Top bar alt color; alone → all cards same color |
| `list-card-grid--accent-odd` + `list-card-grid--accent-even` | Top bar alternates by row — pair with default 2-col or `--3` |
| `g-columns` | Element class — 2-column grid for arbitrary block content |
| `cols-2` / `cols-3` / `cols-2-73|64|37|46` | Panel layout — heading + columns (`ldiv`/`rdiv`/`mdiv`) |
| `rows-2` / `rows-1-2` / `rows-2-1` | Panel layout — top/bottom / 上+左右 / 左右+下 |
| `ldiv` `rdiv` `mdiv` `tdiv` `bdiv` | Panel element classes (on `::: block` or `<div>`) |
| `gallery` | Horizontal strip (img / mermaid / svg / …); independent of `scrollbox-*` — [[AS-Scrollbox#gallery]] |
| `has-light-background` / `has-dark-background` | Auto text palette (body or section) — set by reveal / `bg`, not hand-authored slide classes |
| `on-light-bg` / `on-dark-bg` | Manual local adaptive text on nested block |

## Scrollbox (summary)

Wide/long tables in `::: left` / `::: right` slots — read full note before writing.

| Class | Scroll direction | Typical use |
|:------|:-----------------|:------------|
| `scrollbox` | Both | Code blocks, mixed content |
| `scrollbox-x` | Horizontal | Wide `.academia` tables |
| `scrollbox-y` | Vertical | Long result tables |
| `gallery` | Horizontal strip | img / SVG / mermaid corridor; **not** combined with `scrollbox-x` |

- **A.** Close slot: `:::  <!-- element class="scrollbox-x" -->` or `::: <!-- element class="gallery" -->`
- **B.** Wrap content: `<div class="scrollbox-y">` / `<div class="gallery">` inside slot

Do **not** nest `::: block` inside `::: left` — content falls into `<% content %>`. Full gallery note → vault `AS-Scrollbox.md` § gallery. Do **not** use callout `nowrap` for multi-line images (parser truncates) — see `AS_Callouts.md`.

## Layout Selection (non-nav)

```
AsTp-Cover → ASTp-toc-* → trans_a / trans_b (`ASTp-grid-lr`)
→ columns: ASTp-grid-cols* OR slide class cols-* + block
→ rows-*: slide class only (`rows-2` / `rows-1-2` / `rows-2-1`; nav → shell + class)
→ ASTp-lastpage
```

Panel vs template → [Panel layouts](#panel-layouts). Catalog → [references.md](../references.md). List layouts → [List grid columns](#list-grid-columns). Demo → `AS_Basic Showcase.md`.

## Key Pitfalls

| Issue | Fix |
|:------|:----|
| `center: false` breaks cover/TOC grid centering | Add `grid-align-restore` on those slides |
| `AS_red` + `AS_blue` both loaded | Mutually exclusive — pick one |
| Redundant `bg:` with `AS_SJTU.css` | Omit `bg:` / `bg="..."` when `AS_SJTU.css` loaded |
| Header nav `ul` width collapses | Use **p + ul** header structure |
| Scrollbox in `::: left` via `::: block` | Use写法 A or B from `AS-Scrollbox.md` |
| Multi-line images inside callout | Truncates after first image — use `gallery` or one-line embeds (`AS_Callouts.md`) |
| Inline duplicate `.academia` CSS | Styles live in `AS_basic.css` §8 — no `<style>` paste |
| Theme Directory 404 on Windows | Path separator bug — see `P_obsidian-slides-extended.md` (#301) |
| Custom theme/CSS outside vault | Theme Directory files must be **inside** the vault |
| Block comment syntax in doc slide body | Do not write triple-colon slot markers in explanatory slides (backticks do not escape); use **slot 槽** labels and link [[AS-Templates]] |
| `fglass` / `on-light-bg` unknown | See §13 / §14 in this file; full CSS in `AS_basic.css` |

Per-slide annotations, separators, speaker notes → see [SKILL.md](../SKILL.md).

## Authoritative References (lazy-load)

| Need | File |
|:-----|:-----|
| Fork config, Theme Directory, `center: false` grid bug | `Sources/Equipments/PPT/Advanced Slides/P_obsidian-slides-extended.md` |
| Scrollbox 写法 A/B, export DOM notes | `Sources/Equipments/PPT/Advanced Slides/AS-Scrollbox.md` |
| Templates 机制、Grid 嵌套 | `Sources/Equipments/PPT/Advanced Slides/AS-Templates.md` |
| 布局与 nav 用法演示（权威成品 demo） | [showcase/AS_Basic Showcase.md](../showcase/AS_Basic%20Showcase.md) |
| Tips, export workflow, math escaping, `fglass` combo | `Sources/Equipments/PPT/Advanced Slides/Advanced Slides 技巧汇总（官方文档补充）.md` |
| List grid columns (`list-grid`, `list-grid--*`) | `Sources/Program/代码库/css_AS_Grid Listi网格列表.md` |
| Flex step lists (`list-flex-row/col/step`) | `Sources/Program/代码库/css_AS列表横向、纵向逐步显示.md` |
| Card grid lists (`list-card-grid`, modifiers) | [showcase/AS_Basic Showcase.md](../showcase/AS_Basic%20Showcase.md) §卡片矩阵 |
| Block content 2-col grid (`g-columns`) | `Sources/Program/代码库/css_AS_任何内容服从两列网格布局.md` |
| ASTp template catalog | [references.md](../references.md) § ASTp Layout Templates |
| Grid `drag`/`drop`/`align` | `Sources/Equipments/PPT/Johnny学OB/AS_Grid Component.md` |
| Full CSS source | `../assets/css/AS_basic.css` |

Read vault notes for documentation; read `AS_Basic Showcase.md` for working slide snippets.
