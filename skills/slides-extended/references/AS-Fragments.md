---
UID: 20230721165338
tags: 
aliases: 
description: 
status: planning
modified: 2023-07-21T16:53:38
---

up:: 
Related:: [[AS-Fragmented list]]

参考链接：
- [Fragments — Advanced Slides Documentation (mszturc.github.io)](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/fragments/)

# AS-Fragments


![[OB-S3-04#^mk-20240922100908]]
![[OB-S3-04#^mk-20240922100913]]


Fragments are used to highlight or incrementally reveal individual elements on a slide. Every element with the class fragment will be stepped through before moving on to the next slide. The default fragment style is to start out invisible and fade in. This style can be changed by appending a different class to the fragment.  

> A list of all possible fragment types could be found [here](https://revealjs.com/fragments/)
> Reveal.js 支持的各种 fragment ，对应不同的动画效果

```md
Fade in <!-- element class="fragment" -->

Fade out <!-- element class="fragment fade-out" -->

Highlight red <!-- element class="fragment highlight-red" -->

Fade in, then out <!-- element class="fragment fade-in-then-out" -->

Slide up while fading in <!-- element class="fragment fade-up" -->

---

- Permanent item
- Appear Fourth <!-- element class="fragment" data-fragment-index="4" -->
- Appear Third <!-- element class="fragment" data-fragment-index="3" -->
- Appear Second <!-- element class="fragment" data-fragment-index="2" -->
- Appear First <!-- element class="fragment" data-fragment-index="1" -->
```


---


Fade in <!-- element class="fragment" -->

Fade out <!-- element class="fragment fade-out" -->

Highlight red <!-- element class="fragment highlight-red" -->

Fade in, then out <!-- element class="fragment fade-in-then-out" -->

Slide up while fading in <!-- element class="fragment fade-up" -->

---

- Permanent item
- Appear Fourth <!-- element class="fragment" data-fragment-index="4" -->
- Appear Third <!-- element class="fragment" data-fragment-index="3" -->
- Appear Second <!-- element class="fragment" data-fragment-index="2" -->
- Appear First <!-- element class="fragment" data-fragment-index="1" -->
