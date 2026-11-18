---
UID: 20260521144000
tags:
aliases:
- AS-Horizontal Vertical Slides
up: "[[P_Advanced Slides]]"
description: 幻灯片的水平/垂直分隔符语法
status: developing
modified: 2026-05-21T14:40:00
---

[toc]

参考链接：
- [Horizontal / Vertical Slides — Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/slides/)

# AS-Horizontal Vertical Slides

## 基本语法

- 水平 Slide 分隔符：`---`（两侧各一个空行）
- 垂直 Slide 分隔符：`--`（两侧各一个空行）

```md
# Slide 1

---

# Slide 2.1

--

# Slide 2.2
```

## 自定义分隔符

可通过 frontmatter 的 `separator` 和 `verticalSeparator` 属性自定义：

```yaml
---
separator: ^( ?| )—( ?| )$
verticalSeparator: ^( ?| )–( ?| )$
---
```
