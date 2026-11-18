---
UID: 20260521144001
tags:
aliases:
- AS-Slide Annotations
up: "[[P_Advanced Slides]]"
description: 为整张幻灯片设置样式/class
status: developing
modified: 2026-05-21T14:40:00
---

[toc]

参考链接：
- [Slide Annotations — Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/slideannotations/)

# AS-Slide Annotations

为整张幻灯片传递 style 或 class 属性：

```md
<!-- .slide: style="background-color: coral;" -->

# Header with coral background color

Paragraph has coral background color, too!

---

<!-- .slide: style="background-color: green;" -->

- All Bullet points
- have green
- background color
```

## 用途

- 为单张 slide 设置独立背景色
- 结合 `data-auto-animate` 实现跨 slide 动画
- 结合 `data-background` 等 reveal.js 属性
