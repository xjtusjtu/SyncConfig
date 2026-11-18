---
UID: 20230716144642
tags: 
aliases: 
description: Slides Extended template 机制：语法、槽解析、Grid 嵌套与常见陷阱
status: developing
modified: 2026-07-09T23:45:00
---

up:: [[P_Advanced Slides]]

参考链接：
- [Templates — Advanced Slides Documentation (mszturc.github.io)](https://mszturc.github.io/obsidian-advanced-slides/templates/)

# AS-Templates

## 官方文档内容

> source: https://mszturc.github.io/obsidian-advanced-slides/templates/

Advanced Slides 允许基于 slide template 设计单页幻灯片。每个模板可拥有独立布局，减少重复代码。

### 基本用法

创建模板文件（如 `tpl-footer.md`），存储在 vault 中任意位置：

```md
<% content %>

<grid drag="100 6" drop="bottom">
<% footer %>
</grid>
```

在 slide 中引用模板：

```md
<!-- slide template="[[tpl-footer]]" -->

# This header will be part of the content section defined in the template

Everything define outside a block will be placed in the content section.
Therefore every template has to contain at least a content variable.

::: footer
#### This header will be placed in the footer section of the template
:::
```

> 每个模板 **必须** 包含 `<% content %>` 变量（即使不使用）。

### Optional Variables

默认模板变量必须通过 block comment 赋值，否则会显示占位提示。使用 `?` 标记可选变量，未定义时不显示：

```md
<% content %>

<grid drag="100 6" drop="bottom">
<%? footer %>
</grid>
```

### 模板槽平级解析与 scrollbox

- 写在**任何** `::: 名称` 块**之外**的正文 → 注入 `<% content %>` 位置（占位符名称与 CSS class **无关**）
- 每个 `::: 名称` 块 → 对应模板中的 `<% 名称 %>`；导出 DOM 为 **`div.block`** 包裹槽内 markdown（见 [[AS-Scrollbox#导出 DOM 注意]]）
- nav-shell 正文区 grid 使用 **`class="as-body"`**（[[ASTp-nav-shell]] 的 `<grid class="as-body" …>`），勿用 `content` 作 class 以免与 `<% content %>` 混淆
- 解析按 **slide 级平级** 切分：`::: left` 内再出现 `::: block`（或其它 `::: xxx`）会**终止 left**，不会嵌套

**勿在 ASTp 模板内使用 `<split>`**：每个 `::: 槽` 导出为单个 `div.block`，注入 `<% 槽名 %>` 后 Split 只看到一个（或少数几个）块级子节点，无法实现 `wrap="N"` 对列表项换列，也无法可靠按比例拆槽内多元素。列表分列请用 slide class `list-grid`（[[css_AS_Grid Listi网格列表]]）；多栏正文请用 **Grid** 模板（如 [[ASTp-grid-cols2]]、[[ASTp-grid-lr]]）。`<split>` 仅适用于 slide 正文内直接书写多个并列块、不经模板槽包裹的场景（见 [[AS_Split Component]]）。

**左栏 / 右栏内溢出滚动**（宽表、长表）见 [[AS-Scrollbox]]：

| 写法 | 要点 |
|:---|:---|
| 闭合 `:::` + `<!-- element class="scrollbox-x" -->` | 标题固定，table 等占剩余空间滚动 |
| `<div class="scrollbox-y">` 包在槽内 | 长列表或非 table 内容局部滚动 |

**勿**在 `::: left` 内嵌 `::: block` 包表格（内容会进 `content`）。**勿**在 legacy 无 header 槽模板（如 `AsTp-lText6-rImg4`）上同时使用 `::: header` / `::: footer`。

### Default Template

通过 frontmatter 的 `defaultTemplate` 属性为整个 deck 设置默认模板：

```yaml
---
defaultTemplate: "[[tpl-footer]]"
---
```

### 进阶示例：tpl-con-2-1-box

一个包含标题栏、双列内容、引用来源和页脚的复杂模板：

```md
<grid drag="100 10" drop="top" bg="white" align="left" pad="0 20px">
 <% title %>
</grid>

<grid drag="28 75" drop="69 15" bg="white" style="border-radius:15px"/>

<grid drag="64 70" drop="3 15" align="topleft">
<% left %>
</grid>

<grid drag="26 71" drop="70 17" align="topleft">
<% right %>
</grid>

<% content %>

<style>
.horizontal_dotted_line {
    border-bottom: 2px dotted gray;
} 
</style>

<grid drag="94 0" drop="3 -6" class="horizontal_dotted_line">
</grid>

<grid drag="100 30" drop="0 64" align="bottomleft" pad="0 30px" >
<%? source %>
</grid>

<grid drag="100 6" drop="bottom">
###### © 2022 Advanced Slides<!-- element style="font-weight:300" -->
</grid>
```

在展示中使用：

```md
---
theme: consult
height: 540
margin: 0
maxScale: 4
---
<!-- slide template="[[tpl-con-2-1-box]]" -->

::: title
### _**This is the Title of this Slide**_
:::

::: left
![[Image.jpg|1500]]
:::

::: right
**Header #1**
- Lorem ipsum dolor sit amet, consectetuer adipiscing elit.
- Cras dapibus. Vivamus elementum semper nisi.
:::

::: source
###### Source: Copied from Lorem ipsum dolor Generator
:::
```

## 拓展

### AS Templates支持 AS Grid Layouts 的嵌套

up:: [[Advanced Slides 技巧汇总（官方文档补充）]]
![[AS-Temlates嵌套调用正确思路.excalidraw]]

#### 嵌套方式一

嵌套方式一：模板文件-A中使用了Grid布局，MD源文件-M的具体某页使用了该模板，该具体页面依然可以使用 Grid Layout，MD源文件-M 具体页面的Grid的内容被解析为 模板文件-A 的Gird布局的 `<% content %>` 元素
- 只涉及 模板文件-A 和 MD源文件-M

例如：下面是模板文件-A的Grid布局（现实映射：[[ASTp-nav-shell]]）

![[ASTp-nav-shell]]


未实时预览的源代码

```
<grid drag="100 8" class="header steps bg-with-dark-color" drop="topleft" flow="row" pad="0 40px" align="justify">
<% header %>
</grid>

<grid class="as-body" drag="100 85" drop="0 10" align="topleft" pad="40px">
<% content %>
</grid>

<grid drag="100 4" drop="bottom" class="footer steps">
<% footer %>
</grid>
```

^mk-20231101231114

然后我们在MD源文件-M 具体页面的内容如下


```
---

<!-- slide template="[[ASTp-nav-shell]]" -->

<grid drag="55 100" drop="left" >

左内容

</grid>

<grid drag="43 100" drop="right" class="container" align="center" > 

右内容

</grid>


---
```


> [!info] 
> 再次强调，MD源文件-M 具体页面的内容被解析为了 [[ASTp-nav-shell]] 中模板文件的 `<% content %>` 元素
>  → 左内容盒子的实际宽度为 55×100%，实际高度为100×85%；右内容盒子的实际宽度为43×100%，实际高度为100×85%


#### 嵌套方式二


嵌套方式二：涉及两个模板文件 + MD源文件
- 模板文件-A中使用了Grid布局
- 模板文件-B使用 `<!-- slide template="[[模板文件A]]" -->` 语法调用了模板文件-A，并且模板文件-B也使用了Grid布局
	- 模板文件-B定义的grid布局的内容被解析为模板文件-A的 `<% content %>` 元素
- MD源文件-M的具体某个页面使用 `<!-- slide template="[[模板文件B]]" -->` 语法调用了模板文件-B

现实映射：模板文件-A = [[ASTp-nav-shell]]，模板文件-B = [[ASTp-nav-grid-lr]]（或其他 `ASTp-nav-*` layout）

具体使用时，MD源文件-M的具体某个页面的变量写对就行了，效果同嵌套方式一，也是两个模板文件效果的叠加





模板文件A源代码

![[AS-Templates#^mk-20231101231114]]

模板文件B源代码
```
<% content %>

<!-- slide template="[[模板文件A]]" -->

<grid drag="55 100" drop="left" >

<% left %>

</grid>

<grid drag="43 100" drop="right" class="container" align="center" > 

<% right %> <!-- element class="r-fit-text" -->

</grid>
```


MD源文件-M的具体某个页面代码


```
---

<!-- slide id="c-1" template="[[模板文件B]]" -->

::: left
## Introduction

- 知识付费越来越普遍，从事知识付费的个人越来越多：知乎付费咨询、微信的付费文章、小红书……
- 与专业的培训机构不一样，这类人往往从免费的知识贡献出发，在积累一定的“声誉”之后，开始从事一些付费咨询活动
- 从事知识付费的人的动机是**多样化**的: *money*, self-effcacy, self-worth, enjoy helping...

> [!question] 
> 除了以往纯粹的非物质收益外，还多出了一个物质收益，那么用户的知识贡献行为（包括有偿和无偿）与此前纯粹的无偿贡献**模式**有什么不同？

:::

::: right
![[知识付费.jpg]]
::: 


---
```



> 同样的效果：MD源文件-M 调用模板文件B，其中的内容使用模板文件B自定义的block，同时这些内容连同 <% content %> 都被解析为 模板文件A当中的 <% content %> （因为 block *left* *right* 的实际height都相应地缩水了，尽管相对 height 依然为100%）
> 这与嵌套方式一异曲同工！

各 ASTp 模板的具体用法与演示见 [[AS_Basic Showcase]]。

### 错误方式
但是你不可以将内层的 grid component 封装为模板，然后使用自定义的block 替换原本写在内层的grid componet。给出一个直白的例子：grid 布局实现上下布局，下布局嵌套了个左右对半的grid 布局，这个左右对半的grid 布局不能封装为一个左右对半的模板，然后使用自定义的 block component 替换原有的下布局grid

模板文件-A 上下布局

```
<!-- slide template="[[临时文件B]]" -->

<% content %>

<grid drag="100 20" drop="top" bg="blue">
<% top %>
</grid>

<grid drag="100 80" drop="bottom" bg="lightgray">
<% left %>
<% right %>
</grid>
```


临时文件B👇
- [[ASTp-grid-lr]] 源码

```
<% content %>

<grid drag="50 80" drop="0 10">
<% left %>
</grid>

<grid drag="50 80" drop="50 10" align="left">
<% right %>
</grid>
```

> 效果：模板文件A的 left right 块，后面还被解析成了AStp-lr 中的 left right 块 ← 这不是我们想要的效果


