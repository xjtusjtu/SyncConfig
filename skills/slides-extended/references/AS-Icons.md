---
UID: 20260521144004
tags:
aliases:
- AS-Icons
up: "[[P_Advanced Slides]]"
description: Font Awesome 图标支持
status: developing
modified: 2026-05-21T14:40:00
---

[toc]

参考链接：
- [Icons — Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/fontawesome/)
- [Font Awesome 5 Icons](https://fontawesome.com/v5.15/icons?d=gallery&p=2&m=free)
- [Font Awesome 文档](https://fontawesome.com/v5.15/how-to-use/on-the-web/referencing-icons/basic-use)

# AS-Icons

Advanced Slides 内置 Font Awesome 图标支持，可使用以下语法插入图标：

## 基本语法

```md
![](fas fa-envelope fa-4x) <!-- .element: color="coral" -->
```

## 多种写法

HTML 写法：
```html
<i color="coral" class="fas fa-envelope fa-4x"/>
```

ShortCode 写法：
```
:fas_envelope:
```

## 尺寸控制

```md
<i class="fas fa-camera fa-xs"></i>
<i class="fas fa-camera fa-sm"></i>
<i class="fas fa-camera fa-lg"></i>
<i class="fas fa-camera fa-2x"></i>
<i class="fas fa-camera fa-3x"></i>
<i class="fas fa-camera fa-5x"></i>
<i class="fas fa-camera fa-7x"></i>
```

## 旋转与翻转

```md
<i class="fas fa-snowboarding fa-rotate-90"></i>
<i class="fas fa-snowboarding fa-rotate-180"></i>
<i class="fas fa-snowboarding fa-flip-horizontal"></i>
<i class="fas fa-snowboarding fa-flip-vertical"></i>
```

## 动画图标

```md
<i class="fas fa-spinner fa-spin fa-3x"></i>
<i class="fas fa-circle-notch fa-spin fa-3x"></i>
<i class="fas fa-spinner fa-pulse fa-3x"></i>
```

## 边框与浮动

```md
<i class="fas fa-quote-left fa-2x fa-pull-left"></i>
<i class="fas fa-arrow-right fa-2x fa-pull-right fa-border"></i>
```
