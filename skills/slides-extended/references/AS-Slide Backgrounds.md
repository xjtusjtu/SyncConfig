---
UID: 20260521144002
tags:
aliases:
- AS-Slide Backgrounds
up: "[[P_Advanced Slides]]"
description: 幻灯片背景设置
status: developing
modified: 2026-05-21T14:40:00
---

[toc]

参考链接：
- [Slide Backgrounds — Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/slidebackground/)

# AS-Slide Backgrounds

## 单页背景

通过 `<!-- slide bg="..." -->` 注解设置：

```md
<!-- slide bg="aquamarine" -->
## Slide with text based background

---

<!-- slide bg="#ff0000" -->
## Slide with hex based background

---

<!-- slide bg="rgb(70, 70, 255)" -->
## Slide with rgb based background

---

<!-- slide bg="hsla(315, 100%, 50%, 1)" -->
## Slide with hsl based background

---

# Slide without background

---

<!-- slide bg="https://picsum.photos/seed/picsum/800/600" -->
## Slide with image background

---

<!-- slide bg="[[image.jpg]]" -->
## Slide with image background via wikilink

---

<!-- slide bg="https://picsum.photos/seed/picsum/800/600" data-background-opacity="0.5" -->
## with opacity
```

## 全局背景

通过 frontmatter 的 `bg` 属性设置：

```yaml
---
bg: red
---
```

```yaml
---
bg: '#ff0000'
---
```

```yaml
---
bg: transparent
---
```

`bg: transparent` 适用于 OBS 直播叠加场景。

## 使用日志


- @2026-07-07  `<!-- slide bg="var(--r-grid-bg-front-color)" -->` :x:
    - 但是使用 [[AS-Slide Annotations]] style 是可以引用属性的  `<grid drag="100 30" drop="0 0" align="center" style="background-color: var(--r-grid-bg-front-color);">`

## 更多选项

参见 [reveal.js backgrounds](https://revealjs.com/backgrounds/)


