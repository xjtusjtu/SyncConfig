up:: [[P_Advanced Slides]]


```dataview
LIST 
WHERE icontains(file.name, "css_as")
```

常用搭配
-  `<!-- slide class="fglass list-grid fancy-ol-sq" -->`


所以实现左右布局的时候未必非得借助 [[AsTp-tb]] 等模板，使用我们自定义的 css 样式也可以








r-stack [[OB-S3-04]] 堆叠


> [!question] class 属性 多个取值如何书写？

![[AS-Templates#^mk-20231101231114]]



## 内置类


### r-fit-text


```
<!-- element class="r-fit-text" -->
```

r-fit-text 不适用于图片，仅适合文字 [[OB-S3-05]]


下面三种写法最后 r-fit-text 的class 会被设置给 这个 div 块，而不是给里面的 items 所在的 标签 / 元素

```
<grid drag="60 80" drop="-5 10" align="center" pad="0 40px">

<% items %> <!-- element class="r-fit-text" -->

</grid>
```


```
<grid drag="60 80" drop="-5 10" align="center" pad="0 40px">

<% items %> 

<!-- element class="r-fit-text" -->

</grid>
```


```
<grid drag="60 80" drop="-5 10" align="center" pad="0 40px" class="r-fit-text">

<% items %> 

</grid>
```


## 官方文档未显示指出的警告


![[AS-Speaker Notes#^none]]





## Export 导出用在第三方电脑上汇报

Obsdian 渲染界面，右上角 - Export as html

导出路径由插件设置里的 决定

导出包括以md文件命名的文件夹，下面有Css、dist、plugin  三个子文件夹和 一个 index.html 文件

注意，需要做以下处理，才能得到在我们自己电脑上的效果
1. 新建一个 attachments 子文件夹，将涉及到的本地视频、图片等其它附件放进去
2. 对 index.html 进行全局替换，例如 `Projects/Zhihu-Paid & Free/imgs/微信截图_20240617002636.png` 前面的路径全部替换为 `attachments/`
	1. 可以看到路径用的是以库目录为根路径的相对路径！


个人配置
- SJTU 主题 CSS（按顺序加载，见 [themes/as_basic.md](../themes/as_basic.md)）
	- `AS_basic.css` — 布局、header/footer、表格/列表样式
	- `AS_red.css` **或** `AS_blue.css` — 红/蓝 token（**二选一**）
	- `AS_SJTU.css` — **自动背景**（首张 `SJTU-cover-bg.svg`，其余 `SJTU-bg1.svg`）；加载后源码中**不必**再写 `bg:` / `bg="..."`
	- 蓝色主题时 `AS_blue.css` 用 CSS `filter` 将红色 SVG 偏蓝，背景 URL 仍由 `AS_SJTU.css` 提供
- 背景图 URL（`AS_SJTU.css` 内已引用，手动 `bg` 时也可用）
	- 本地：[[SJTU-bg1.svg]]、[[SJTU-cover-bg.svg]]
	- 在线：
		- https://raw.githubusercontent.com/xjtusjtu/images/master/img/SJTU-bg1.svg
		- https://raw.githubusercontent.com/xjtusjtu/images/master/img/SJTU-cover-bg.svg




### @2024-08-27 数学公式渲染错误

[Problematic rendering in the math formula · Issue #302 · MSzturc/obsidian-advanced-slides (github.com)](https://github.com/MSzturc/obsidian-advanced-slides/issues/302)
1. 换行不执行 → 需要加 `\` 转义，最终结果 `\\\\` ↔ `\\`
2. 行间公式 多个 `\text` 搭配下标 `_` 不渲染 → 需要加 `\` 转义




Render wrongly

```
$$
\begin{vmatrix}
  a & b \\
  c & d
\end{vmatrix} = a d - b c
$$
```

Render correctly

```
$$
\begin{vmatrix}
  a & b \\\\
  c & d
\end{vmatrix} = a d - b c
$$
```

按理来说，多余的转义符号是不需要加的！


---

Render wrongly

```
$$
\\underbrace{a_{i}}_{d_{i}}
$$
```

Render correctly

```
$$
\\underbrace{a_{i}}_{d\_{i}}
$$
```

按理来说，这个转义符号是不需要加的