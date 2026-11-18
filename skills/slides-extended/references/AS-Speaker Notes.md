---
UID: 20231030152113
tags: 
aliases: 
description: 类似PPT的演讲者模式
status: planning
modified: 2023-10-30T15:21:13
source: https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/speakernotes/
---

up:: 

参考链接：
- 

# AS-Speaker Notes


> obsidian-slides-extended 框架下，品牌名称从 Advanced Slides 改为 "Slides Extended"，功能无变化。

Advanced Slides comes with a speaker notes function which can be used to present per-slide notes in a speaker view.

To access the speaker view you have to open `Slide Preview` and click on the `Open in Browser` Button in the top right corner. Your Slide will open in your default web browser. Press the »S« key on your keyboard to open the notes window.

The notes window also gives you a preview of the next upcoming slide so it may be helpful even if you haven’t written any notes.

```md
## My Slide

This is part of my Presentation


note: this is not! Only the speaker might see this text.

- and this bulletpoint
- or this picture

![](https://picsum.photos/id/1005/250/250) 
```

> [!info] 
> It is possible to change the notes indicator by changing the `notesSeparator` property in frontmatter see yaml docs

## 使用日志

@2024-12-24 当前页面 ==没有任何内容时==，不允许写 speaker notes，否则会影响渲染框架，导致渲染不正常（抽风） ^none




