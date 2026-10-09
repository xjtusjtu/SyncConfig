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

Blue variant: set `theme: Marp_blue`.

## Layout Selection

```
cover_a~e → toc_a/b → cols-2/3/rows-* → cols2_* (+ fglass) → scrollbox-y/x → navbar → lastpage
```

- Section class via `<!-- _class: cols-2-64 -->`; content in `<div class="ldiv">` / `rdiv` / etc.
- Left image + right text → `cols-2` + `limg` + `rdiv`
- Old `info` → use `cover_a`
- Transition slide → `trans`

## Key Pitfalls

| Issue | Fix |
|:------|:----|
| Cover/toc/lastpage shows page number | `<!-- _paginate: "" -->` on that slide |
| scrollbox-y not scrolling in column | Put scrollbox **before** blockquote |
| Centered image | Alt text ending in `C`: `![C](image.svg)` |
| HTML layouts broken | Confirm `markdown.marp.enableHtml: true` |
| Hold-to-peek on decorative images | 按住正文 `img` / `.mermaid > svg` 可放大预览；装饰图加 `class="as-no-peek"`（header/footer 图默认不触发） |

Per-slide directives (`_header`, `_footer`, etc.) → see [SKILL.md](../SKILL.md).

## Authoritative Reference (lazy-load)

| Need | File |
|:-----|:-----|
| 类名、令牌、scrollbox、布局与可复制 slide（唯一权威） | [showcase/Marp_Basic Showcase.md](../showcase/Marp_Basic%20Showcase.md) |

Search Showcase for `<!-- AGENT: layout=` comments to find working Marp slide snippets.
