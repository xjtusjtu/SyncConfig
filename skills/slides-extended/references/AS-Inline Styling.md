---
UID: 20231030150320
tags: 
aliases: 
description: 
status: planning
modified: 2023-10-30T15:04:46
source:
---

up:: 

参考链接：
- 

# AS-Inline Styling


you may define css styles inside your markdown: 就是不定义在YAML区，而是定义在Markdown的正文

### by using the `<style>` compoment

```md
<style>
	.with-border{
		border: 1px solid red;
	}
</style>

styled text <!-- element class="with-border" -->
```

> [!warning] 全局生效
> `<style>` 标签在当前 slide deck（即整个演示文稿）中 **全局生效**，而非仅当前幻灯片。因为 reveal.js 将所有 slide 渲染在同一个 HTML 页面中，CSS 样式天然是全局的。
> 
> 这点和 [[Marp]] 一致


- [See it fullscreen](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/inlinestyling/#)

### by including them through css file

it is possible to add further css files beside theme and highlight theme to slide deck:

```md
---
css: [css/layout.css,css/customFonts.css]
---
```

> [!note] slides extended 新增
> These files will be found relative to either the configured custom Theme Directory or 
> the Slides Extended plugin folder.
> obsidian-slides-extended 中 CSS 文件查找路径改为：自定义主题目录或 Slides Extended 插件文件夹







