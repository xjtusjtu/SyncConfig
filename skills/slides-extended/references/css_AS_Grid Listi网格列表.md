---
tags:
  - code_snippet
language: CSS
description:
path:
modified: 2026-07-10T19:45:00
---



Related:: [[CSS布局-Grid Layout 网格布局]] · 卡片矩阵演示 → [[AS_Basic Showcase]] §卡片矩阵


## 服从网格布局的2列列表

> DOM：`section.list-grid > div > ul|ol`（无模板）；模板槽为 `> div > .block > ul|ol`；nav-shell 正文为 `div.as-body > ul|ol`（模板内 `<grid class="as-body">`，与 `<% content %>` 占位符无关）。

```CSS
.reveal .slides section.list-grid > div > :is(ul, ol),
.reveal .slides section.list-grid > div > .block > :is(ul, ol),
.reveal .slides section.list-grid div.as-body > :is(ul, ol) {
    display: grid;
    grid-template-columns: var(--list-grid-columns);
    width: 95%;
    counter-reset: step;
    margin: 0 40px 0 10px;
    gap: 0.7em;
}

.reveal .slides section.list-grid > div > :is(ul, ol) > li,
.reveal .slides section.list-grid > div > .block > :is(ul, ol) > li,
.reveal .slides section.list-grid div.as-body > :is(ul, ol) > li {
    margin-right: 5%;
}
```


## 列比 modifier

与 `list-grid` 同 slide 空格组合；modifier 仅覆盖 `--list-grid-columns` token。

```css
.reveal .slides section.list-grid--1-2 { --list-grid-columns: 1fr 2fr; }
.reveal .slides section.list-grid--2-1 { --list-grid-columns: 2fr 1fr; }
.reveal .slides section.list-grid--3 { --list-grid-columns: repeat(3, 1fr); }
.reveal .slides section.list-grid--1-2-1 { --list-grid-columns: 1fr 2fr 1fr; }
.reveal .slides section.list-grid--1-1-2 { --list-grid-columns: 1fr 1fr 2fr; }
.reveal .slides section.list-grid--2-1-1 { --list-grid-columns: 2fr 1fr 1fr; }
.reveal .slides section.list-grid--4 { --list-grid-columns: repeat(4, 1fr); }
```

**示例**：`<!-- slide class="list-grid list-grid--3 fglass" -->` — 完整演示见 [[AS_Basic Showcase]] §列表分列。


