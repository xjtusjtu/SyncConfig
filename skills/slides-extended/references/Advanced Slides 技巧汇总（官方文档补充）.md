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



## 统一标题样式与页面 class 的作用范围

Slides Extended 没有与 Marp 完全对应的“从当前页开始，后续页面沿用”的原生指令。页面注解只作用于当前页，不会自动传递给下一页：

```markdown
<!-- slide class="fancyhead_1r fadehead" -->
```

根据需要区分三种做法：

| 目标 | 方式 |
|:-----|:-----|
| 只设置当前页 | 页面注解 `<!-- slide ... -->` |
| 整份演示稿统一 | frontmatter 的 `css:`、主题，或通过 `defaultTemplate` 提供默认页面 class |
| 从某页开始影响后续页 | 用 CSS 范围选择器模拟，不是页面注解继承 |

### 用 defaultTemplate 设置默认标题 class

除了逐页声明 class，也可以把标题样式写进默认模板。模板只提供页面 class 和正文占位符即可，不必承担分栏等布局。以下以示例模板 `tpl-fancyhead` 为例，使用时需准备对应的模板笔记：

```markdown
<!-- slide class="fancyhead_1r fadehead" -->

<% content %>
```

演示稿的 frontmatter 指向该模板，并加载对应 CSS：

```yaml
---
defaultTemplate: "[[tpl-fancyhead]]"
css: ["Extras/SyncConfig/skills/slides-extended/assets/css/AS_basic.css", "Extras/SyncConfig/skills/slides-extended/assets/css/AS_blue.css"]
---
```

这样，使用该默认模板、且未局部指定 `class` 的页面会得到 `fancyhead_1r fadehead`，无需每页重复声明。`defaultTemplate` 面向整份演示稿，不是从某页起改变后续页面的指令；显式指定其他 `template=` 的页面也不应假定会继续叠加这个默认模板。模板机制见 [[AS-Templates#Default Template]]。

> [!warning] 局部 class 会整体覆盖默认 class
> 模板与页面的 `class` 不会自动合并。例如某页写 `class="list-grid"`，会替换模板中的整组 `fancyhead_1r fadehead`。需要同时保留标题样式时，必须在该页手动补全所有 class。

例如，这一页保留默认标题样式，同时使用列表分栏：

```markdown
<!-- slide class="fancyhead_1r fadehead list-grid" -->

## 分栏页面

- 第一项
- 第二项
```

多个 class 合并在同一个 `class` 属性内，不要重复书写多个 `class` 属性。默认模板只是提供默认值，不能代替局部组合时的显式声明。

### 用范围 CSS 从某页开始生效

给起始页设置锚点：

```markdown
<!-- slide id="style-start" -->
```

再用 CSS 选择该页和后续水平页，例如统一修改二级标题颜色：

```css
.reveal .slides > #style-start h2,
.reveal .slides > #style-start ~ section h2 {
	color: var(--r-accent-color);
}
```

这里的起始页必须是水平页。选择器覆盖它和其后的同级水平页，也覆盖这些页中的垂直子页；此前页面不受影响。它只把声明的 CSS 应用到指定范围，不会自动给后续页面加上 `fancyhead_1r` 等 class。若要在该范围启用整套标题装饰，需要将整套规则写成范围选择器，或逐页声明对应 class；若整份稿件都使用同一套标题样式，则优先考虑前面的默认模板做法。

## 用 grid 叠加透明着重框

加载 `AS_basic.css` 后，在 `<grid>` 上加 `class="focus-box"`，即可用透明矩形框标注图片、表格或文字中的重点区域：

```markdown
<grid class="focus-box" drag="42 24" drop="8 35" align="bottomleft">
**重点**：比较这两组结果。*这里是简短说明。*
</grid>
```

- `drag="42 24"`：框宽为页面的 42%，高为 24%。
- `drop="8 35"`：框左上角距左侧 8%、顶部 35%，顺序为 x、y。
- `align="bottomleft"`：说明文字放在框内左下角；不需要文字时，将内容留空。
- `focus-box`：3px 实线边框，使用主题着重色 `--r-accent-color`；背景透明，尺寸计算包含边框。
- 字号以正文变量 `--r-main-font-size` 为基准：粗体（含粗斜体）为正文大小，普通文字和斜体为正文的 0.8 倍。例如正文为 30px 时，分别为 30px 和 24px。

配色直接复用现有主题变量，无须新增颜色变量或逐页写色值：框线使用 `--r-accent-color`，粗体默认使用 `--r-strong-color`，普通文字继承页面正文色（默认来自 `--r-main-color`），斜体默认使用 `--r-em-color`。文字继续遵循主题已有的深浅背景适配规则。

框的外观由 CSS 统一管理，每页主要修改位置、尺寸和说明。原有 grid 若写了 `border` 或 `bg`，应删除这些覆盖属性，使用类中的默认样式。

> [!warning] 透明填充不等于整体透明
> `focus-box` 已设置透明背景，无须再加 `bg="transparent"`。不要使用 `opacity="0"`，否则边框和文字也会一起隐藏。

需要跨分栏标注时，将框放在分栏的 `::: block` 外部。位置通过修改数值调整，并非鼠标拖拽；正文或图片重新排版后，应在预览中核对框的位置。

详细定位和文字对齐属性见 [[AS_Grid Component]]。

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