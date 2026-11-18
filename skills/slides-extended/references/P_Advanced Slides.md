---
UID: 202203171545
aliases:
tags:
  - Obsidian
  - plugin
  - deprecated
realName: obsidian-advanced-slides
set: manual
checked: false
status: developing
modified: 2023-01-20T17:51:13
---

up:: [[用Markdown制作幻灯片]]
Related:: [[Johnny-AS-01]]

[toc]

参考链接

- Johnny<u>都是一些介绍性质的课程，要学东西得花钱买他的专业课</u>
	- 简介：[用Obsidian做PPT，我是认真的 Advanced Slides 专业PPT制作课程来了_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1kF411F7Pc?spm_id_from=333.999.0.0&vd_source=52f7a67d9e75268bf3a92a30143a1244)
	- 公开课：[Obsidian演示文稿插件 Advanced Slides 基本功能介绍 Johnny的公开课_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1ce4y197BT?spm_id_from=333.999.0.0&vd_source=52f7a67d9e75268bf3a92a30143a1244)
- [GitHub - MSzturc/obsidian-advanced-slides: Create markdown-based reveal.js presentations in Obsidian](https://github.com/MSzturc/obsidian-advanced-slides)

- 第三方
	- 
# Advanced Slides

首先要说明的是，OB本身是有 **幻灯片** 插件的！

将 [[Reveal.js]] 和 Obsidian 进行联动，本质是 [[Reveal.js]] 在 OB 中的实现

>[!question] 为什么要用 Advanced Slides 来制作课件
> 
> 1. 只用去写Markdown
> 2. 生态成熟的Reveal JS
> 3. 借助MD语法实现简单动画
> 4. 插件优秀

## 更新日志

### @2022-12-26 

- 演示时，跳过某些页
- 激光笔插件
- 在 FM 中设置默认模板
- 演示模式设置
- 增强 mermaid 的支持

### @2023-03-06

![[OB-S3-07#^mk-20240306170323]]



## Advanced Slides Documentation 
> 参考文档解析

source
- ⭐[Advanced Slides Documentation (mszturc.github.io)](https://mszturc.github.io/obsidian-advanced-slides/)
	- 简单的中译版本 [链接](https://www.cnblogs.com/liuzhongkun/p/17096534.html#tid-rptzfJ)
- [GitHub - MSzturc/obsidian-advanced-slides](https://github.com/MSzturc/obsidian-advanced-slides)
- [reveal.js 官方文档](https://revealjs.com/)

内容
- Basic Markdown Syntax
	- ...
	- [[AS_Images]]
	- [[AS_Links]]
    - [[AS_Footnotes]]
	- [[AS_Mermaid]]
	- [[AS_Callouts]]
- Extended Syntax
	- [[AS-Horizontal Vertical Slides]]
	- [[AS-Element Annotations]]
	- [[AS-Slide Annotations]]
	- [[AS-Block Comments]]
	- [[AS-Scrollbox]]
	- [[AS-Fragments]]
	- [[AS-Inline Styling]]
	- [[AS-Slide Backgrounds]]
	- [[AS-Speaker Notes]]
	- [[AS-Fragmented list]]
	- [[AS-Excalidraw support]]
	- [[AS-Icons]]
	- [[AS-Emojis]]
	- [[AS-Charts support]]
	- [[AS-Slide Animation]]
- Features
	- [Auto Completion for Advanced Slides](https://mszturc.github.io/obsidian-advanced-slides/features/autocomplete/) *Video*
	- [[AS_Embed Slides]]
- Layouts
	- [[AS_Grid Component]]
	- [[AS_Split Component]]
- [[AS-Templates]]
- [[AS_Basic Showcase]]
- [[AS_Frontmatter Options]]
- [[AS_Plugins]]
	- Menu
	- Overview
	- Chalkboard
	- Elapsed Time Bar
	- Laser Pointer


## 使用技巧

- PPT内容整体左对齐：在YAML区添加 `center: false` ^mk-20230721110735
- 只想让标题左对齐 ^mk-20230721150743
	```css
	.reveal h2 {
	  align-self: start;
	}
	```

- 所有内容从左上角开始

```css
.reveal .slides section>div {
  justify-content: start !important;
}
```


- 修改默认flex布局的方向

```css
.reveal .slides section>div {
  flex-direction: row !important;
}
```


- [Set center: false cannot align everything to the left · Issue #133 · MSzturc/obsidian-advanced-slides (github.com)](https://github.com/MSzturc/obsidian-advanced-slides/issues/133)
	- yaml区的`center: false` 导致 white 主题时，行间公式也会居中 ← 这不是我们想要的结果
	- 根据这个Issue的提示，我们发现是 `center: false` 导致 `.reveal .slides section>div` 下增加了一个 `align-items: start;` 属性，我们在自己的CSS中将其修改为 `align-items: unset !important;` 即可
		- 注意，不是设置为center，否则会导致所有PPT全部又变回 `center: true` 的效果


- 单纯的将某张图片居中，可借助[[AS-Element Annotations]]的align属性
	- yaml配置
		- theme: white
		- center: false

```
![[202307171535Method.excalidraw|500]] <!-- element align="center" -->
```

- [[AS_Grid Component]] 是允许在原代码中嵌套的，参见[[AS-Templates#AS Templates支持 AS Grid Layouts 的嵌套]]
	- 其中的drag，drop属性都是百分比！
- [[如何从PPT文件中得到某张slide背景的SVG格式]]
	- 用处：作为我们Advanced Slides 的高清背景图
	- 前提：PPT当中背景图片本就是高清的，而不是简单地插入别的图片


## 使用问题


- @2025-02-08 https://forum.obsidian.md/t/discontinued-advanced-slides-create-markdown-based-reveal-js-presentations-in-obsidian/28243/256?u=wangxiaobu
  The original plugin by MSzturc was discontinued.  A fork maintained by ebullient is discussed [here](https://forum.obsidian.md/t/slides-extended/85825) [[P_obsidian-slides-extended]] 本插件不再更新，请使用 
- @2024-09-22 footnote 的序号是不正常的 [Incorrectly numbered footnotes across slides · Issue #304 · MSzturc/obsidian-advanced-slides (github.com)](https://github.com/MSzturc/obsidian-advanced-slides/issues/304)
	- 为此，我们重新定义了 sup 标签的功能，感觉使用效果比 原生的 footnote 还要好 
- [Set center: false cannot align everything to the left · Issue #133 · MSzturc/obsidian-advanced-slides (github.com)](https://github.com/MSzturc/obsidian-advanced-slides/issues/236)
	- using a "\newline", it works
	- It may because the first backslash is used as an escape character, so it cannot be identified in HTML.




## 安装与配置

与一般插件不同，插件安装目录下还有4个子文件夹（与[[Reveal.js]]有关）

- css
- dist
- plugin
	- chalkboard
	- chart
	- customcontrols
	- elapsed-time-bar
	- fullscreen
	- highlight
	- markdown
	- math
	- menu
	- mermaid
	- notes
	- search
	- verticator
	- zoom
- template
  - embed.html
  - reveal.html

---


- Theme 幻灯片主题
- Highlight Theme 高亮主题
- Transition Style 幻灯片切换主题
- Transition Speed 切换速度

## 打印

- Advanced slides 预览界面，右上角-更多选项-Print Presentation，在默认浏览器打开，并弹出打印界面
- 注意，请选择【另存为 PDF】，此时每页大小就是我们在 OB 中设置的幻灯片页面大小

> [!question] 多少页面大小恰好是 A4 呢？
> 
> - height: 1000
> - width: 707
 
## 基本用法

### yaml

页面比例

- width:
- height:

修改主题

- theme

导入 css，注意，允许路径当中有空格！

### 样式示例

- 图片+说明，[[AS-图片+说明]]

### 全局模板

0.18版本更新，例如每页的Slide我们都会田间footer作一个简短的介绍，如何简单地穰治

## 拓展用法

### 插入本地Geogebra文件

Related:: [[Geogebra]]

参考链接

- [一位60岁的数学老师在用Advanced Slides做课件，他想直接嵌入本地Geogebra文件……_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1Fv4y1M7b8?spm_id_from=333.999.0.0&vd_source=52f7a67d9e75268bf3a92a30143a1244)

### Advanced Slides 用作阅读器

参考链接

- [Johnny学OB 一个绝对被低估的插件 用Advanced Slides在Obsidian里做一个阅读器_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1bS4y1Y75Z?spm_id_from=333.999.0.0&vd_source=52f7a67d9e75268bf3a92a30143a1244)


```
---
preloadIframes: true
---

---

<!-- slide bg="https://picsum.photos/seed/picsum/800/600" data-background-opacity="0.5" -->

---

<!-- slide data-background-iframe="https://slides.com" data-background-interactive -->


note: 
## Page
content
```

- `preloadIframes: true` 预加载iframe内容
- `data-background-interactive` 建议加上，加上之后iframee背景始终可互动，不加有些时候无法互动（点击）

#### 嵌入微信读书

Related::[[P_Custom Frames]]

参考链接：

- [Johnny学OB 在Obsidian里使用微信读书，真的得劲！_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1aa411v7pw?spm_id_from=333.999.0.0)


1. 首先创建*微信读书.md*
```
---
preloadIframes: true
---

<!-- slide data-background-iframe="https://weread.qq.com/" data-background-interactive -->
```

2. 然后编写quickadd-macro

- [x] 登录有问题 ⚠

使用 custom frames 完美解决登陆问题

#### 嵌入飞书妙记

参考链接：[Johnny学OB 听我的，你也应该把飞书妙记嵌入到你的Obsidian_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1Yr4y1H7DA?spm_id_from=333.999.0.0&vd_source=52f7a67d9e75268bf3a92a30143a1244)

#### 记代码笔记

##### 代码特定行高亮

呈现行号： *空格* + `[]`

````
``` []
```
````

直接高亮特定行

- 逗号`,`隔开
- `-`切片

````
``` [1,5-10]

```
````

单页PPT高亮行切换

````
``` [1|5|10]

```
````
