---
UID: 20231030150318
tags: 
aliases: 
description: 幻灯片间的自动动画效果
status: developing
modified: 2026-05-21T14:40:00
---

up:: [[P_Advanced Slides]]

参考链接：
- [Slide Animation — Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/slideanimation/)
- [Reveal.js Auto-Animate](https://revealjs.com/auto-animate/)

# AS-Slide Animation

> [!note] slides extended
> obsidian-slides-extended 文档中品牌已改为 "Slides Extended"，功能与语法完全一致。

Advanced Slides 可以自动在相邻幻灯片之间为匹配元素添加动画。只需在相邻的两个 slide annotation 中添加 `data-auto-animate`：

```md
<!-- .slide: data-auto-animate -->
# Title

---
<!-- .slide: data-auto-animate -->

# Title
##### **Subtitle**
###### *Author - 2022* 
```

> 前往 Reveal.js 查看具体效果，注意和 [[AS-Fragments]] 区分开。Fragments 是单张 slide 内的元素逐步显示，Slide Animation 是跨 slide 的平滑过渡。
