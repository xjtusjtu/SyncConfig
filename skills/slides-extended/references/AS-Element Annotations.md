---
UID: 20230716101913
tags: 
aliases: 
description: 
status: developing
modified: 2026-07-07T09:45:00
---

up:: [[P_Advanced Slides]]

参考链接：
- [Element Annotations — Advanced Slides Documentation (mszturc.github.io)](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/classes/)

# AS-Element Annotations

> Element Annotations 的作用，有点类似于 [[Marpit-Theme CSS#Scoped Style]] 的 style scoped 的作用

## 基本语法

通过 HTML 注释为单个元素添加 class、style 或 data 属性：

```md
text with border <!-- element class="with-border" -->

text with background <!-- element style="background:blue" -->

text with attribute <!-- element data-toggle="modal" -->
```

## 原理

无论是 yaml frontmatter 还是 HTML 注释，落到最后的 html 元素上，最终都会被浏览器解析为 / 都会作用于 对应 html 元素的 style 属性。

### 方式 A：frontmatter / slide 注解 `bg`（手动指定）

```yaml
---
bg: https://raw.githubusercontent.com/xjtusjtu/images/master/img/SJTU-bg1.svg
---
```

```md
<!-- slide class="grid-align-restore" bg="https://raw.githubusercontent.com/xjtusjtu/images/master/img/SJTU-cover-bg.svg" template="[[AsTp-Cover]]" -->
```

AS 会把 `bg` 写入 `div.backgrounds > div.slide-background.drop > div.slide-background-content` 的 `style` 属性，例如：

```css
background-image: url(https://raw.githubusercontent.com/xjtusjtu/images/master/img/SJTU-bg1.svg);
```

### 方式 B：`AS_SJTU.css` 自动注入（推荐，SJTU 主题 deck）

在 frontmatter `remoteCSS:` 中按顺序加载 `AS_basic.css`、`AS_red.css` 或 `AS_blue.css`，再加载 `AS_SJTU.css`。使用 jsDelivr URL；此时**无需**在 frontmatter 写 `bg:`，也**无需**在封面 slide 写 `bg="..."`：

红色主题：

```yaml
remoteCSS:
  - https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/slides-extended/assets/css/AS_basic.css
  - https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/slides-extended/assets/css/AS_red.css
  - https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/slides-extended/assets/css/AS_SJTU.css
```

蓝色主题（`AS_blue.css` 通过 CSS `filter` 将同一套红色 SVG 背景偏转为蓝色，URL 不变）：

```yaml
remoteCSS:
  - https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/slides-extended/assets/css/AS_basic.css
  - https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/slides-extended/assets/css/AS_blue.css
  - https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/slides-extended/assets/css/AS_SJTU.css
```

CSS 规则见 `AS_SJTU.css`：

- 第一张 slide → `SJTU-cover-bg.svg`
- 其余 slide → `SJTU-bg1.svg`

`AS_red.css` 与 `AS_blue.css` **二选一**，勿同时加载。

若某页需要自定义背景，不要加载 `AS_SJTU.css`，或改用方式 A 的 `bg` / `bg="..."` 覆盖。

## 用途

- 为特定段落/图片/列表单独设置样式
- 覆盖全局主题样式
- 添加自定义 HTML data 属性

