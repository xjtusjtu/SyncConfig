---
name: slides-extended
description: "Create and edit Obsidian Slides Extended (reveal.js) presentation markdown - frontmatter, slide separators, annotations, ASTp templates, SJTU theme (AS_basic/AS_red/AS_blue/AS_SJTU), ASTp-nav header/footer, grid-align-restore, scrollbox, gallery. Use when the user asks for Slides Extended, Advanced Slides, AS_basic, or reveal.js slides in Obsidian. Do not use for Marp (`marp: true`) or native PowerPoint (.pptx)."
compatibility: opencode
---

# Slides Extended Presentation Skill

This skill enables agents to create and edit **Obsidian Slides Extended** (reveal.js) presentation markdown in this vault. Do **not** use Marp syntax (`marp: true`, Marp directives).

## When to Use

Apply when the user explicitly requests:

- Slides Extended or Advanced Slides presentations
- reveal.js slides in Obsidian
- Help with slide separators, `<!-- slide -->` annotations, templates, or speaker notes
- SJTU / AS_basic themed decks or `ASTp-nav-*` layouts

**Do not** apply `obsidian-markdown` agent-note conventions (UID, `[toc]`, `up`/`Related`, agent-note frontmatter) to presentation files. Use reveal.js frontmatter instead.

## Output Conventions

Follow vault `AGENTS.md` presentation rules:

| Item | Convention |
|:-----|:-----------|
| Location | `Spaces/Presentation/`, `Calendar/`, or project directories |
| Naming | `*pre.md`, `*presentation.md`, or project-specific names |
| Frontmatter | `width`, `height`, `theme`, slide options — **not** `marp: true` |
| Avoid | UID, `[toc]`, `up`/`Related`, agent-note template fields |

## Plugin Context

- Original **Advanced Slides** (MSzturc) is discontinued; use **Slides Extended** (ebullient fork).
- Slides Extended adds **Theme Directory** (vault path for custom themes/CSS — files must live **inside** the vault) and **Center content** toggle (`center: true/false` frontmatter).
- Two frontmatter keys for extra CSS: `css:` (vault-local files, resolved inside the vault) and `remoteCSS:` (remote URLs loaded as-is — GitHub raw works from any vault).
- Syntax is largely compatible with Advanced Slides; brand name changed to "Slides Extended".
- Fork-specific notes (Windows custom theme 404, `center: false` grid bug): see `Sources/Equipments/PPT/Advanced Slides/P_obsidian-slides-extended.md`.

## Lazy-Load References

**Before writing advanced syntax**, read [references.md](references.md) to locate the vault note, then `Read` that file. Do not invent syntax from memory.

| Need | Start here |
|:-----|:-----------|
| Full syntax index | [references.md](references.md) |
| AS_basic / SJTU / nav / scrollbox / gallery / CSS classes | [themes/as_basic.md](themes/as_basic.md) |
| All vault docs | `Sources/Equipments/PPT/Advanced Slides/` directory |

## Creation Workflow

```
Task Progress:
- [ ] Step 1: Plan deck structure (cover → sections → closing)
- [ ] Step 2: Write global frontmatter
- [ ] Step 3: Split slides with --- and -- (vertical)
- [ ] Step 4: Add slide / element annotations
- [ ] Step 5: Write slide content
- [ ] Step 6: Apply templates or layouts if needed
- [ ] Step 7: Read references.md or themes/as_basic.md for unfamiliar features
```

### Step 1: Plan structure

Typical deck order: cover → optional TOC → body sections → closing/thanks slide.

For Grid, Split, Templates, or Fragments, read the matching file in [references.md](references.md) first. For SJTU nav decks, also read [themes/as_basic.md](themes/as_basic.md).

### Step 2: Global frontmatter

Must be the **first** block in the file, wrapped in `---`:

```yaml
---
width: 1920
height: 1080
theme: white
center: false
css: []
---
```

Common options (full table → `AS_Frontmatter Options.md` in references):

| Option | Purpose | Example |
|:-------|:--------|:--------|
| `width` / `height` | Slide dimensions | `1920` / `1080` |
| `theme` | reveal.js theme | `white`, `black`, custom name |
| `highlightTheme` | Code highlight theme | `zenburn` |
| `center` | Vertical centering | `true` / `false` |
| `css` | Extra CSS files — vault-relative paths (vault-local files) | See [Theme Extensions](#theme-extensions) |
| `remoteCSS` | Extra CSS files — **GitHub raw URLs** (any vault) | See [Theme Extensions](#theme-extensions) |
| `transition` | Slide transition | `slide`, `fade`, `zoom` |
| `defaultTemplate` | Template applied to all slides | wikilink to template file |
| `separator` | Horizontal slide regex | Slides Extended default: `\r?\n---\r?\n` |
| `verticalSeparator` | Vertical slide regex | Slides Extended default: `\r?\n--\r?\n` |

### Step 3: Slide separators

**Slides Extended defaults** (differ from legacy Advanced Slides regex):

- **Horizontal**: `---` on its own line, with a **blank line on each side**
- **Vertical** (nested slides): `--` on its own line, with a **blank line on each side**

```markdown
# Slide 1

---

# Slide 2.1

--

# Slide 2.2
```

Do not confuse frontmatter delimiters (`---` at file start) with slide breaks. Slide content begins after the closing `---` of frontmatter.

### Step 4: Slide and element annotations

**Slide-level** (apply to current slide):

```markdown
<!-- slide class="..." bg="..." -->
<!-- slide template="[[tpl-name]]" -->
<!-- slide data-background-iframe="https://example.com" data-background-interactive -->

<!-- .slide: style="background-color: coral;" -->
```

**Element-level** (apply to preceding element):

```markdown
![[image.png|500]] <!-- element align="center" -->
text with border <!-- element class="with-border" -->
```

Read `AS-Slide Annotations.md` and `AS-Element Annotations.md` in references for full attribute lists.

### Step 5: Slide content

Standard Markdown inside each slide: headings, lists, tables, code blocks, blockquotes, images.

**Heading hierarchy** (SJTU / nav decks — see [themes/as_basic.md](themes/as_basic.md)):

| Level | Use | Example |
|:------|:----|:--------|
| `#` | Cover title only (`::: title` block) | `# 汇报主标题` |
| `##` | Slide title / major section | `## 变量设计` |
| `###` | In-slide subsection | `### 推荐优先级` |

Do not use `#` for every slide — `AS_basic.css` centers h1; body slides should use `##` / `###`.

Obsidian features supported: wikilinks, embeds `![[note]]`, callouts, Excalidraw embeds.

**Speaker notes** — use `note:` delimiter (default):

```markdown
# Slide title

Content here.

note:
Notes visible only in presenter view.
```

**Code line highlighting** — space + `[]` after language tag:

````markdown
```python [1,5-10]
def foo():
    pass
```
````

For fragments, block comments, backgrounds, charts, icons — read the matching reference file.

### Step 6: Templates and layouts

Templates use `<% content %>` placeholders and `<!-- slide template="[[tpl-name]]" -->`.

Grid (`<grid drag="..." drop="...">`) and Split (`<split even>`) layouts — read references before use. Grid `drag`/`drop` values are percentages.

For Antai-style layouts, use **`ASTp-*` templates** in [assets/templates/](assets/templates/) — see [Antai Layout Templates](#antai-layout-templates) and [references.md](references.md).

For **SJTU nav decks**, load `AS_basic.css` + `AS_red.css` or `AS_blue.css` + `AS_SJTU.css` and use **`ASTp-nav-*` templates** — see [Theme Extensions](#theme-extensions). With `AS_SJTU.css`, omit `bg:` / per-slide `bg="..."`.

### Step 7: Unfamiliar features

Consult [references.md](references.md) or [themes/as_basic.md](themes/as_basic.md), then `Read` the vault note. Never guess syntax for templates, animations, plugins, or custom CSS.

## Images and Embeds

```markdown
![[local-image.png|500]]
![[drawing.excalidraw|600]]
```

Use element annotations for per-image alignment when `center: false`:

```markdown
![[image.png|500]] <!-- element align="center" -->
```

Background images: `<!-- slide bg="url-or-color" -->` — see `AS-Slide Backgrounds.md`. Omit when `AS_SJTU.css` is loaded.

## Math

reveal.js uses MathJax/KaTeX via plugin settings. For rendering issues (line breaks, subscripts with `\text`), see `Advanced Slides 技巧汇总（官方文档补充）.md` — may require extra `\` escaping.

## Common Pitfalls

| Issue | Fix |
|:------|:----|
| Slides not splitting | Use `---` / `--` with blank lines on each side (Slides Extended default) |
| Frontmatter parsed as slide | Frontmatter must be first; only one block at file start |
| Windows custom theme 404 | Path separator bug in Slides Extended — see `P_obsidian-slides-extended.md` (#301) |
| Custom theme/CSS outside vault | `css:` only resolves vault-local files — put remote URLs in `remoteCSS:` instead |
| `center: false` but math still centered | See `Advanced Slides 技巧汇总（官方文档补充）.md`; project uses `AS_basic.css` layout rules |
| Block comment styling | Prefer element annotation on closing `:::` — see `AS-Block Comments.md` |
| `\newline` not working | First backslash may be consumed as escape; try `\\newline` |
| Export HTML missing media on other PC | Create `attachments/` folder; copy images/videos; replace vault-relative paths in `index.html` — see 技巧汇总 §Export |
| Plain note frontmatter on deck | Remove UID, `[toc]`, agent-note fields |
| Confusing with Marp | This skill is **not** Marp — no `marp: true`, no `_class` directives |
| AS_basic / SJTU / nav / list-* / scrollbox / gallery theme issues | See [themes/as_basic.md](themes/as_basic.md) **Key Pitfalls** |

## Relationship to Marp

| | Slides Extended | Marp |
|:--|:----------------|:-----|
| Engine | reveal.js (Obsidian plugin) | Marpit |
| Frontmatter | `width`, `theme`, `center`, … | `marp: true`, `theme`, `size`, … |
| Page break | `---` (blank lines) | `---` |
| Vertical slides | `--` (blank lines) | N/A |
| Per-slide config | `<!-- slide ... -->` | `<!-- _class: ... -->` |
| Skill | This file | `../marp/SKILL.md` |

Do not mix syntax between the two ecosystems.

## Theme Extensions

Custom CSS stacks add layout classes and SJTU styling on top of standard Slides Extended syntax. When a theme is requested, **Read** its companion file (not via the skill tool):

| Theme stack | Companion file | CSS files |
|:------------|:---------------|:----------|
| AS_basic / SJTU (red) | [themes/as_basic.md](themes/as_basic.md) | `AS_basic.css` + `AS_red.css` + `AS_SJTU.css` (optional) |
| AS_basic / SJTU (blue) | [themes/as_basic.md](themes/as_basic.md) | `AS_basic.css` + `AS_blue.css` + `AS_SJTU.css` (optional) |
| AS_basic only | [themes/as_basic.md](themes/as_basic.md) | `AS_basic.css` |

Load these via the frontmatter `remoteCSS:` array using **GitHub raw URLs** (any vault can use them). Remote URLs go in `remoteCSS:`; the `css:` array is for vault-local files. This skill ships its CSS at [`assets/css/`](assets/css/):

```yaml
remoteCSS:
  - https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/slides-extended/assets/css/AS_basic.css
  - https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/slides-extended/assets/css/AS_blue.css
```

Local alternative: copy `assets/css/` into the vault and use the `css:` array with vault-relative paths instead.

> Fallback: if raw GitHub fails (MIME type rejected), switch to the jsDelivr mirror `https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/slides-extended/assets/css/AS_basic.css` (returns `Content-Type: text/css`).

Workflow:

1. Write deck using this skill (frontmatter, separators, annotations, templates)
2. When user specifies SJTU theme, `AS_basic`, nav header/footer, or `academia`/`scrollbox`/`gallery` classes → **Read** [themes/as_basic.md](themes/as_basic.md), then lazy-load vault docs it points to
3. Apply theme-specific slide classes, `ASTp-nav-*` templates, and CSS load order from the companion

## Antai Layout Templates

Vault templates in [assets/templates/](assets/templates/) (`ASTp-*.md`) provide **structural** layouts migrated from Marp_basic.css (cols/rows/cover/toc). No Marp visual CSS — pair with `AS_basic.css` or default reveal theme.

### When to use template vs CSS panel class

| Need | Approach | Example |
|:-----|:----------|:--------|
| Proportional columns (fixed Grid boxes) | ASTp template | `ASTp-grid-cols2-64` + `::: left` / `right` |
| Columns / 上+左右 / 下+左右（`auto`/`1fr`） | **Slide class + block** | `class="cols-2"` / `rows-1-2` + `::: block` + `ldiv`/`tdiv` — [themes/as_basic.md](themes/as_basic.md) § Panel layouts |
| Top/bottom or 上+左右（弹性高度） | Slide class + block | `rows-2` / `rows-1-2` / `rows-2-1`; nav → `ASTp-nav-shell` + class |
| Cover / TOC / fixed zones | Grid only | `AsTp-Cover`, `ASTp-toc-*` |
| Multi-column list | Slide class | `list-grid` + `list-grid--*` |
| Card matrix | Slide class | `list-card-grid` + modifiers |
| Simple 1:1 template | Grid only | `ASTp-grid-lr` |
| Multi-block wrap (no template slot) | Inline `<split wrap>` | [[AS_Split Component]] — **not** inside ASTp templates |

### Invoke a column template

```markdown
<!-- slide template="[[ASTp-grid-cols2-64]]" -->

::: left
## Slide heading

Wide column (6/10)
:::

::: right
Narrow column (4/10)
:::
```

Do **not** write `::: left` without a template. CSS panel (`cols-*` / `rows-*` + `::: block` + `ldiv`/`tdiv`) → [themes/as_basic.md](themes/as_basic.md) § Panel layouts.

Full catalog → [references.md](references.md) **ASTp Layout Templates**. Demo → [showcase/AS_Basic Showcase.md](showcase/AS_Basic%20Showcase.md).

Marp_basic mapping: `cols-2-73` → slide class `cols-2-73` **or** template `ASTp-grid-cols2-73`. Cover uses `AsTp-Cover`. See `Marp_Basic Showcase.md`.

## SJTU Nav Decks

Long research / group-meeting decks with top header nav, footer, and SJTU backgrounds.

**Full guide** → [themes/as_basic.md](themes/as_basic.md) (CSS load order, nav templates, header p+ul, scrollbox, gallery, slide classes).

Quick summary:

- CSS: `AS_basic.css` → `AS_red.css` or `AS_blue.css` → `AS_SJTU.css` (optional backgrounds)
- Structure: `AsTp-Cover` (`id="0"`, `grid-align-restore cover`) → TOC → `ASTp-nav-*` body → `ASTp-lastpage`
- Per-slide `<!-- slide id="c-N" template="[[ASTp-nav-shell]]" -->` — no `defaultTemplate`
- Demo → [showcase/AS_Basic Showcase.md](showcase/AS_Basic%20Showcase.md)
