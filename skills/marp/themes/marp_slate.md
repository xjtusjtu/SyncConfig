# Marp Theme: Marp_slate

Brief entry for the **Marp_slate** theme — a research-report look (light slate
background, navy/teal accents). Assumes generic Marp syntax from [SKILL.md](../SKILL.md).

> Extracted from a deck that previously carried these styles inline via the `style:`
> frontmatter directive, so it can now be reused as `theme: Marp_slate`.

## When to Read

Load this file when:

- User sets `theme: Marp_slate`
- User asks for the slate/navy/teal research-report look
- User needs the `cover_f` / `compact` / `figure` / `diagram` slide classes
- Parent `marp` skill delegates via Theme Extensions

## Environment

Register theme CSS in `markdown.marp.themes`. Use the **GitHub raw URL** (any vault can use it directly):

```json
{
  "markdown.marp.themes": [
    "https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/marp/assets/css/Marp_slate.css"
  ],
  "markdown.marp.enableHtml": true
}
```

| Theme | CSS |
|:------|:----|
| Marp_slate | [../assets/css/Marp_slate.css](../assets/css/Marp_slate.css) |

Local alternative: copy `assets/css/` into the vault and use a vault-relative path instead of the raw URL.

> Fallback: if raw GitHub fails (MIME type rejected), switch to the jsDelivr mirror `https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/marp/assets/css/Marp_slate.css`.

`enableHtml: true` is required for `pre.mermaid` blocks.

## Relationship to Marp_basic

`Marp_slate` is a **child theme of `Marp_basic`** (same pattern as `Marp_blue`): it does
`@import "Marp_basic"`, then maps Marp_basic's design tokens onto slate values. It therefore
inherits **every** Marp_basic layout class — `cover_*` (incl. `cover_f`), `toc_*`, `cols-*`,
`rows-*`, `cols2_*`, `scrollbox*`, `navbar`, `lastpage`, `fglass`, `trans`, … — plus the
shared defaults that were ported from this theme into Marp_basic (default blockquote panel,
`cover_f` gradient, `th_fill` header). The opt-in `quote_mark` variant is available here too.

Traditional covers `cover_a`–`cover_e` use the slate gradient endpoint
(`--color-coverbg: var(--color-cover-to)`, resolving to `#155a70`),
not the parent's red. Titles are white on `cover_a`–`cover_d`; `cover_e` uses the
teal accent on its white title area.

The inherited cover layout model (h1/h2 in normal flow so `<!-- fit -->` pushes the
subtitle down; colour band = the title block's own background; `--gap-cover-title` /
`--gap-cover-body` / `--cover-seam`) is documented in
[marp_basic.md](marp_basic.md#封面布局模型cover_a--cover_b--cover_e).

## Standard Frontmatter

```yaml
---
marp: true
theme: Marp_slate
paginate: true
size: 16:9
math: mathjax
footer: 'Your footer text'
---
```

## Slide Classes

Slate-specific classes:

| Class | Effect |
|:------|:-------|
| `cover_f` | Dark navy→teal gradient cover / section opener; left-aligned white title with layered accent text |
| `compact` | Denser text (24px) and tables (20px) for data-heavy slides |
| `figure` | Centered figure slides; images `object-fit: contain` |
| `diagram` | Frames `pre` code blocks and Mermaid in a light panel with navy mono text |

Apply per slide with `<!-- _class: cover_f -->`. Combine sparingly (`compact` + `diagram` is fine).
All Marp_basic layout classes (`cols-*`, `rows-*`, `cover_*`, `toc_*`, `scrollbox*`, `navbar`,
`lastpage`, …) are also available — see [marp_basic.md](marp_basic.md).
The shared `zebra_bar` class adds a 9px top accent rule; slate has no top rule by default.

## Design Tokens

Like `Marp_blue`, `Marp_slate` **overrides Marp_basic's token values directly** (it does not
introduce a separate palette namespace). Recolor a deck by overriding any of these in
frontmatter `style:` or a child theme.

| Token | Slate value | Use |
|:------|:------------|:----|
| `--color-main` | `#172b4d` | Body text |
| `--color-coverbg` | `var(--color-cover-to)` → `#155a70` | Traditional cover backgrounds / title panels |
| `--color-much` | `#147d92` | `h2`/`h3`, accents, `zebra_bar`, links, blockquote rule |
| `--color-h1` | `var(--color-much)` → `#147d92` | Non-cover `h1` (inherited accent, no slate override) |
| `--color-strong` / `--color-em` | `#096a80` | `**strong**` / `*em*` |
| `--color-footer` | `#63758b` | Footer, page number, captions |
| `--color-cover-muted` | `#c1dbe5` | Cover body text, italic text, footer, page number |
| `--color-blockquote-bg` | `#eaf3f7` | Default blockquote / panel |
| `--color-blockquote-border` | `#147d92` | Blockquote left rule |
| `--color-blockquote-text` | `#113454` | Blockquote text |
| `--color-table-border` | `#dce5ed` | Table cell borders |
| `--color-table-header-bg` / `-fg` | `#113454` / `#ffffff` | `th_fill` header |
| `--color-cover-from` / `-to` | `#113454` / `#155a70` | `cover_f` gradient |
| `--color-cover-accent` / `-text` | `#a7e2e8` / `#ffffff` | Cover accent / title |
| `--font-family-main` / `-title` / `-table` | `"LXGW WenKai", "Noto Sans CJK SC", sans-serif` | Body font |
| `--font-size-main` / `-1` / `-2-3` / `-h3` / `-table` | `26px` / `40px` / `29px` / `25px` / `22px` | Type scale |

The slide background (`#f8fafc`) is set on `section` directly. The top rule is opt-in
via `<!-- _class: zebra_bar -->`, inherited from Marp_basic.

## Mermaid

`Marp_slate.css` styles the `pre.mermaid` **frame**; node colors come from a deck-level
Mermaid init script. Add at the **end** of the markdown file:

```html
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  themeVariables: {
    primaryColor: '#eaf3f7',
    primaryBorderColor: '#147d92',
    primaryTextColor: '#113454',
    lineColor: '#4a6b7c',
    fontSize: '18px',
    fontFamily: '"Microsoft YaHei", "Noto Sans CJK SC", sans-serif'
  },
  flowchart: { curve: 'basis', padding: 10, htmlLabels: false, useMaxWidth: true }
});
const renderMermaid = () => { if (mermaid.run) { mermaid.run(); } else { mermaid.init(); } };
document.fonts.ready.then(renderMermaid);
</script>
```

`htmlLabels: false` uses native SVG text and avoids `foreignObject` collapse; waiting on
`document.fonts.ready` prevents nodes measuring at zero width.

## Key Pitfalls

| Issue | Fix |
|:------|:----|
| Slate-specific classes do nothing | Only `compact` / `figure` / `diagram` are defined here; all other layouts come from Marp_basic |
| Mermaid nodes uncolored | Add the deck-level `mermaid.initialize(...)` script |
| Caption not muted | Caption must be a top-level paragraph that is *only* emphasis: `*note*` |
| Cover shows page number | `<!-- _paginate: "" -->` on the `cover_f` slide |
