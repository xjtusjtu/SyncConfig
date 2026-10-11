---
name: marp
description: "Create and edit Marp presentation markdown (directives, slide separators, frontmatter). Use when the user asks for Marp slides or `marp: true` decks. Do not use for Slides Extended (reveal.js) or native PowerPoint (.pptx). Load theme companion files when a specific theme is requested."
compatibility: opencode
---

# Marp Presentation Skill

This skill enables agents to create and edit **Marp** presentation markdown in this vault. Marp syntax is theme-agnostic; theme-specific layout classes live in companion files at `themes/<name>.md` (Read tool — not registered skills).

## When to Use

Apply when the user explicitly requests:

- Marp slides or presentation markdown
- Help with Marp directives, slide pagination, or deck structure

**Do not** apply `obsidian-markdown` note conventions (UID, `[toc]`, agent-note frontmatter) to presentation files. Use Marp frontmatter instead.

## Output Conventions

Follow vault `AGENTS.md` presentation rules:

| Item | Convention |
|:-----|:-----------|
| Location | `Spaces/Presentation/`, `Calendar/`, or project directories |
| Naming | `*pre.md`, `*presentation.md`, or project-specific names |
| Frontmatter | `marp: true`, `theme`, slide directives |
| Avoid | UID, `[toc]`, `up`/`Related`, agent-note template fields |

## Lazy-Load References

Read vault Marp docs **only when needed**:

| Need | File |
|:-----|:-----|
| Directives (global / local) | `Sources/Equipments/PPT/Marp/Marpit Markdown_Directives.md` |
| Marp ecosystem overview | `Sources/Equipments/PPT/Marp/Marp.md` |
| Other Marp syntax | `Sources/Equipments/PPT/Marp/` directory |

## Environment Setup

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

- Register each custom theme CSS in `markdown.marp.themes`
- Local alternative: copy this skill's `assets/css/` into the vault and use a vault-relative path
- Set `enableHtml: true` when using HTML blocks, `<div>` layouts, or Mermaid

> Fallback: if raw GitHub fails (e.g. VS Code rejects the MIME type), switch to the jsDelivr mirror `https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/marp/assets/css/Marp_basic.css` (returns `Content-Type: text/css`).

## Creation Workflow

```
Task Progress:
- [ ] Step 1: Plan deck structure (cover → sections → closing)
- [ ] Step 2: Write global frontmatter
- [ ] Step 3: Split slides with `---`
- [ ] Step 4: Add per-slide directives
- [ ] Step 5: Write slide content
- [ ] Step 6: Load theme extension if using a custom theme
- [ ] Step 7: Add Mermaid script at end if used
```

### Step 1: Plan structure

Typical deck order: cover → optional TOC → body sections → closing/thanks slide.

For theme-specific layout classes (cover templates, multi-column grids), load the matching theme extension (see [Theme Extensions](#theme-extensions)).

### Step 2: Global frontmatter

Must be the **first** block in the file, wrapped in `---`:

```yaml
---
marp: true
theme: default
paginate: true
size: 16:9
header: 'Optional header text'
footer: 'Optional footer text'
math: katex
style: |
  section { background-color: #fff; }
---
```

Common global directives:

| Directive | Purpose | Example |
|:----------|:--------|:--------|
| `marp` | Enable Marp mode | `marp: true` |
| `theme` | Registered theme name | `theme: default` |
| `size` | Slide aspect ratio | `size: 16:9` or `size: 4:3` |
| `paginate` | Show page numbers | `paginate: true` |
| `header` | Global header | `header: 'Title'` |
| `footer` | Global footer | `footer: 'Page footer'` |
| `style` | Inline CSS overrides | `style: \|` block |
| `math` | Math renderer | `math: katex` or `math: mathjax` |

Values with Markdown, images, or YAML special characters must be wrapped in quotes:

```yaml
footer: '![width:130px](logo.png) **bold** _italic_'
```

### Step 3: Slide separators

Use `---` on its own line **between slides**.

**Do not confuse** frontmatter delimiters (`---` at file start) with slide page breaks. Slide content begins after the closing `---` of frontmatter.

Do not use horizontal rules inside slide content unless intentional.

### Step 4: Per-slide directives

HTML comments at the top of a slide override global settings for **that page only**. Prefix with `_`:

```markdown
<!-- _class: cover_f -->
<!-- _header: "Custom header" -->
<!-- _footer: "" -->
<!-- _paginate: false -->
<!-- _backgroundColor: #f0f0f0 -->
```

| Directive | Scope | Notes |
|:----------|:------|:------|
| `_class` | Current slide | Space-separated CSS classes on `<section>` |
| `_header` | Current slide | Override global header; `""` to hide |
| `_footer` | Current slide | Override global footer; `""` to hide |
| `_paginate` | Current slide | `false` or `""` to hide page number |
| `_backgroundColor` | Current slide | Slide background color |

Without `_` prefix, directives apply from current slide **onward** (spot directives).

### Step 5: Slide content

Standard Markdown inside each slide: headings, lists, tables, code blocks, blockquotes, images.

Fragmented lists (reveal item-by-item): use `-*` or `1)` syntax — see `Marpit Markdown_Fragmented list.md` in vault.

### Step 6: Theme extension

If the user specifies a custom theme (e.g. Marp_basic), read the matching theme companion file with the Read tool before applying layout classes. See [Theme Extensions](#theme-extensions).

### Step 7: Mermaid (if used)

Wrap diagram in HTML block; append script after the last slide:

```markdown
<div class="mermaid">
flowchart LR
    A --> B
</div>
```

```html
<script src="https://unpkg.com/mermaid@11.15.0/dist/mermaid.min.js"></script>
<script>mermaid.initialize({ startOnLoad: true });</script>
```

Theme extensions may add scroll containers or sizing options for wide diagrams.

**Emoji**: never put emoji inside Mermaid labels — Marp Core replaces them with twemoji `<img alt="🧑" …/>` before Mermaid parses, and the `alt="…"` quotes terminate `["…"]` strings → `Syntax error in text`. Use plain text (see vault doc `P_Marp for VS Code.md`).

**Font size & label centering**: set fontSize via `themeVariables` (in `%%{init}%%` or `mermaid.initialize` — both work). Do NOT pin font-size in theme CSS. If node text sits below center after enlarging fontSize (multi-line/cylinder nodes worst), the root cause is Mermaid measuring line height (~16.6px/line @18px) smaller than the rendered `line-height: 1.5` (27px/line) — no CSS fix; use the post-render label-centering script from vault doc `P_Marp for VS Code.md` (§ 调大 fontSize 后节点文字不垂直居中). Do not reset `p` margins inside mermaid — that worsens it.

## Images

Marp image syntax extensions:

```markdown
![width:200px](image.png)
![height:300px](image.png)
![width:200px height:100px](image.png)
![bg](background.jpg)
```

For images in `header`/`footer`, use quoted YAML values with inline size:

```yaml
header: '![width:130px](logo.png) Organization Name'
```

## Math

Enable in frontmatter:

```yaml
math: katex
```

Inline: `$E = mc^2$` — Block: `$$...$$`

## Common Pitfalls

| Issue | Fix |
|:------|:----|
| Slides not splitting | Use `---` alone on a line between slides |
| Frontmatter parsed as slide | Frontmatter must be first; only one block at file start |
| Header/footer with Markdown/images breaks YAML | Wrap in single quotes |
| HTML / div layouts not rendering | Set `markdown.marp.enableHtml: true` |
| Plain note frontmatter on deck | Remove UID, `[toc]`, agent-note fields |
| Theme not found | Register CSS path in `markdown.marp.themes` |
| Same global directive repeated | Marp uses the **last** value only |
| Emoji in Mermaid label → `Syntax error in text` | Remove emoji from labels; twemoji replacement injects `alt="…"` quotes before Mermaid parses |
| Mermaid node text not vertically centered after fontSize change | Mermaid line-height measure/render mismatch — apply post-render label-centering script (see `P_Marp for VS Code.md`) |

## Theme Extensions

Custom themes add CSS classes and layout patterns on top of standard Marp syntax. When a theme is requested, **Read** its companion file (not via the skill tool):

| Theme | Companion file | CSS |
|:------|:---------------|:----|
| Marp_basic / Marp_blue | [themes/marp_basic.md](themes/marp_basic.md) | `assets/css/Marp_basic.css`, `assets/css/Marp_blue.css` |
| Marp_slate | [themes/marp_slate.md](themes/marp_slate.md) | `assets/css/Marp_slate.css` (child theme — `@import "Marp_basic"`) |

Workflow:

1. Write deck using this skill (Marp syntax, frontmatter, directives, `---` pagination)
2. When user specifies `theme: Marp_basic` or asks for Marp_basic layout → **Read** [themes/marp_basic.md](themes/marp_basic.md), then lazy-load vault docs it points to
3. Apply theme-specific section classes, panel divs, and scroll containers from those references

Future themes follow the same pattern: add `marp/themes/<theme>.md` and register here.
