---
tags:
  - code_snippet
language: CSS
description:
path:
modified: 2026-11-18
---
### 启用可组合卡片

演示见 [[AS_Basic Showcase]] 的「列表与卡片」章节。样式来自本目录的 `AS_basic.css` 与 `AS_blue.css`。

```markdown
<!-- slide class="list-cards list-layout-row card-tint card-rounded card-title-body list-marker-none list-title-center list-body-left" -->

- <!-- element class="fragment" -->
	**输入**
	- 整理已有材料
- <!-- element class="fragment" -->
	**处理**
	- 选择合适的方法
- <!-- element class="fragment" -->
	**输出**
	- 检查交付结果
```

`list-cards` 是启用边界，首级 `li` 是一张卡片。列表高度随内容产生，内部列表不再套用卡片排列；正文各层默认没有项目符号、外边距和缩进。新体系不与旧 `list-flex-*`、`list-card-grid*` 卡片类叠加。

### 排列、外观与圆角

| 控制项 | class | 默认及作用 |
|:--|:--|:--|
| 横排 | `list-layout-row` | 所有首级项横排、等宽 |
| 纵排 | `list-layout-col` | 首级项纵排、高度随内容 |
| 网格 | `list-layout-grid` | 默认 2 列，行数随条目数产生 |
| 列数 | `list-cols-2` / `list-cols-3` / `list-cols-4` | 只改变网格列数 |
| 浅色底 | `card-tint` | 浅蓝背景、无边框 |
| 顶边 | `card-top` | 透明背景、6px 深蓝顶边 |
| 描边 | `card-outline` | 透明背景、2px 蓝色描边 |
| 跨符号描边 | `card-border-marker` | 透明背景、2px 蓝色描边；上边框穿过符号中心，边线位于符号下层 |
| 透明 | `card-plain` | 透明、无边框；默认外观 |
| 圆角 | `card-rounded` / `card-square` | 8px / 0；默认直角 |

每组只选一种。排列不改变背景、边框、圆角或文字角色；普通外观不改变内容排列和文字；圆角不绑定某种外观。`card-border-marker` 是描边与顶边符号位置的组合预设，符号来源、形状、圆角和文字对齐仍分别选择。未声明排列时为单列。外观、圆角可在首级 `li` 局部覆盖。

### 四种结构模式

| 模式 | 首级主文字 | 直接子列表 | 允许省略的内容 |
|:--|:--|:--|:--|
| `card-title-body` | 标题 | 全部为正文 | 正文，可仅有标题 |
| `card-custom-title-body` | 自定义符号 | 第一项为标题，其余为正文 | 正文，可仅有符号与标题 |
| `card-custom-body` | 自定义符号 | 全部为正文，无标题 | 没有标题区域 |
| `card-body` | 正文 | 全部为正文，无标题 | 子列表；也是默认模式 |

自定义符号可以是字母、数字、文字或 emoji。模式决定角色，不以加粗、字符内容或正文数量猜测。推荐用 `**文字**` 包住首级主文字，提供可独立排版的元素；也支持 Markdown 的 `<p>` 包装或显式 `<span>`。没有包装的匿名文本不会获得标题或符号的独立排版。

`card-custom-title-body` 中，标题项还可以带更深一级的正文列表。所有正文均保持正文字号，不递归缩小。

```markdown
<!-- slide class="list-cards list-layout-row card-outline card-custom-title-body marker-side card-layout-inline" -->

- **A**
	- **输入**
	- 整理已有材料
- <!-- element class="card-custom-body" -->
	**B**
	- **这是一段加粗正文。**
	- 当前卡片没有标题
- **C**
	- **输出**
		- 检查交付结果
```

模式可声明在 section、外层 block、`ul` / `ol` 或首级 `li`，优先级为当前 `li` > 最近列表或宿主 > section > 默认正文模式。同一宿主只设一种模式；局部模式完整替换继承模式，不依赖 class 的书写顺序。选择正文模式后，首条加粗正文仍是正常字号；省略正文不会生成空的正文区域。

### 卡内排列预设

卡片之间的 `list-layout-*` 与卡片内部的 `card-layout-*` 分开控制。结构模式负责区分符号、标题和正文；下面的预设只决定这些内容如何排列，不改变内容角色、卡片外观或圆角。可在列表上设默认，在当前首级 `li` 换用另一种预设。

| 预设 | 排列 | 符号字号 |
|:--|:--|:--|
| `card-layout-center` | 符号、标题、正文逐行居中，整组在卡片内垂直居中 | 与标题相同 |
| `card-layout-side` | 先让标题与正文整体在卡片内垂直居中，再把符号放在整组左侧并垂直居中；水平默认靠左 | 跟随标题，无标题时跟随正文 |
| `card-layout-inline` | 先让标题与正文整体在卡片内垂直居中，再让符号与首行标题 / 正文同行垂直居中；水平默认靠左 | 跟随标题，无标题时跟随正文 |
| `card-layout-stack` | 符号一行、标题一行、正文一行；三者合为完整内容组在卡片内垂直居中，水平默认靠左 | 跟随标题，无标题时跟随正文 |

四种预设均适用于样式自动编号和首级手写符号。默认采用同行排列；原生 `::marker` 保留浏览器列表语义，并与首行标题采用相同字号、字重及行高。无符号时不增加空符号盒；无标题时不增加空标题行，符号字号改为跟随首行正文。

例如 `card-custom-title-body card-layout-inline` 表示符号与标题同字号、同行垂直居中，后续正文与标题共用左边界；正文既可作为标题的同级条目，也可嵌在标题项内。某项只改为 `card-custom-body` 后不生成标题区域，符号跟随正常正文的字号，并与首行正文垂直居中。普通自定义符号按实际文字宽度占位，不再额外预留固定符号列；默认间距为 12px。需要符号对整组正文居中时，再显式选 `card-layout-side`。

水平靠左、垂直居中是默认，两个方向分别控制。符号独占一行时，将符号、标题和正文合为一组垂直居中；符号在侧边或与首行同行时，先将标题和正文这一组垂直居中，再分别让符号对齐整组中心或首行中心。没有标题时，将首行正文视为符号的同行参照。

需要额外的水平整体居中时加 `card-align-center`；同行自定义符号与文字列一起参与水平居中，不会只居中文字列而向右偏。`card-align-left` 在当前项恢复水平靠左，不改变垂直居中。`card-layout-center` 是水平也居中的堆叠预设；`card-layout-stack` 保持水平靠左。`list-title-left/center`、`list-body-left/center` 仍分别控制文字列内的对齐。

所有布局的符号默认与首行标题同字号，没有标题时与首行正文同字号，包括不加 `card-layout-*` 的情况。需要放大时显式加 `card-marker-large`（1.15 倍），或设置 `--as-card-marker-scale`；`card-marker-normal` 可让当前项恢复 1 倍。它们可用于整列表或当前首级 `li`，与结构模式、排列和符号来源独立。显式 `--as-card-marker-font-size` 优先于比例。

`marker-badge card-layout-center` 保留圆环形状，但将徽章放入内容流，与标题和正文作为整体居中。单独使用 `marker-badge` 仍保留跨顶边的原有布局。

需要上边框从符号中心经过时，改用 `card-border-marker`，可与 `marker-badge` 组合成圆环跨顶边样式。该预设将自动编号或自定义符号固定在顶边，覆盖继承的卡内位置；符号高于边框绘制，圆环的独立实色底遮住下方边线，线条不会穿过符号文字。卡片上方预留半个符号盒的空间，标题正文与符号不重叠。

```markdown
<!-- slide class="list-cards list-layout-row card-border-marker card-title-body list-marker-auto marker-badge card-align-center" -->

1. **输入**
	- 整理已有材料
2. <!-- element class="card-custom-title-body card-rounded" -->
	**A**
	- **处理**
	- 选择合适的方法
```

### 符号来源与呈现

| 控制项 | class | 行为 |
|:--|:--|:--|
| 原生符号 | `list-marker-native` | 默认；显示 `ul` 项目符号或 `ol` 序号 |
| 自动编号 | `list-marker-auto` | 用于 `ol`，以 `decimal-leading-zero` 显示 `01`、`09`、`10` |
| 不显示符号 | `list-marker-none` | 关闭外层原生及自动符号 |
| 行内符号 | `marker-inline` | 自动编号或自定义符号与标题同行 |
| 侧边符号 | `marker-side` | 自动编号或自定义符号在左，默认位置 |
| 圆环徽章 | `marker-badge` | 自动编号或自定义符号跨在卡片顶边 |
| 正文无符号 | `list-body-markers-none` | 默认，取消正文项目符号 |
| 正文原生符号 | `list-body-markers-native` | 显示正文 `ul` / `ol` 符号，仍不引入嵌套缩进 |

自定义符号模式自动关闭当前卡片的原生或自动编号，不需另加一个 marker 类；父列表用了自动编号，局部自定义卡也不会出现双符号。普通模式与符号来源独立，例如 `card-title-body list-marker-auto marker-badge`。

自动编号使用浏览器内建的 `list-item` counter，保留 `ol start`、`li value` 的语义；不会把第 10 项写成 `010`。原生 marker 同样跟随标题字号，保留在卡片内部；标题和正文共用符号右侧的内容列。形状与位置类只用于自动编号或自定义符号。

卡片的首级 `li` 保持 `display: list-item`，外层列表负责 flex/grid 排列。将 `li` 自身改为 `flex` 或 `grid` 会丢失原生 `::marker`，不应以这种方式修复内部排版。

### 字号与独立对齐

每张卡片是 `inline-size` 查询容器。标题默认 `clamp(1.1 × 主题正文字号, 12cqw, 1.8 × 主题正文字号)`，按卡片内容宽度缩放；达到最小字号后，长标题正常换行。正文保持主题字号，包括第三层及更深内容。

| 层级 | 靠左 | 居中 | 对齐变量 |
|:--|:--|:--|:--|
| 标题 | `list-title-left` | `list-title-center` | `--list-title-align` |
| 正文 | `list-body-left` | `list-body-center` | `--list-body-align` |

两级在水平方向默认均靠左，可显式组合成四种对齐方式。`card-align-center` 控制水平整体居中，`card-layout-center` 显式选择水平也居中的堆叠；这些水平设置与默认的垂直居中独立。靠左时，无项目符号的正文文字与标题左边界对齐；开启正文项目符号后，符号位置与标题左边界对齐，符号后的文字按原生列表排版。多层正文沿用同一左边界，不逐级增加缩进。标题模式只影响模式定义的标题，不会把自定义符号或正文误当成标题。

| 变量 | 默认值 / 作用 |
|:--|:--|
| `--list-title-font-size` | 完整自适应表达式；设为 `48px` 可固定标题字号 |
| `--list-item-font-size` | 标题上限，默认主题正文字号的 1.8 倍 |
| `--list-body-font-size` | 所有深度的正文字号，默认主题正文 |
| `--as-list-gap` | 卡片间距，默认 36px |
| `--as-card-padding-block` / `--as-card-padding-inline` | 卡片内边距，默认 30px / 28px |
| `--as-card-content-gap` | 标题与正文间距，默认 10px |
| `--as-card-radius` | 卡片圆角；`card-rounded` 设为 8px |
| `--as-card-marker-size` / `--as-card-marker-font-size` | 符号盒尺寸 / 显式字号；普通同行自定义符号按文字宽度占位，徽章固定盒默认 84px；字号跟随首行标题或正文 |
| `--as-card-marker-scale` | 符号与首行标题 / 正文字号比例，默认 1；`card-marker-large` 为 1.15，`card-marker-normal` 恢复 1 |
| `--as-card-content-align` | 内容组的垂直对齐，默认 `center`；同行 / 侧边以标题正文组为基准，独占一行时以完整内容组为基准 |
| `--as-card-min-height` | 可选的卡片最小高度；便于固定高度场景检查整组居中 |
| `--as-card-marker-gap` | 符号与文字间距，默认 12px |

在 slide annotation 的 `style` 中设置变量即可调整本页；也可以在 block 或 `li` 调整局部参数。

### AS_blue 配色

新卡片沿用深蓝、亮蓝、白色、中性色及少量金色强调，不再循环使用红、绿、紫等额外色系。

| 配色变量 | 来源与用途 |
|:--|:--|
| `--as-card-surface` | 主题白背景 |
| `--as-card-surface-tint` / `--as-card-surface-hover` | 深蓝与白底按 8% / 12% 混色 |
| `--as-card-border` / `--as-card-border-strong` | 35% 深蓝混色描边 / 主题深蓝顶边 |
| `--as-card-title` / `--as-card-text` / `--as-card-text-muted` | 深蓝标题 / 正文 / 弱化文字 |
| `--as-card-marker` | 亮蓝符号 |
| `--as-card-badge-surface` / `--as-card-badge-border` | 独立白底 / 深蓝圆环，不读取卡片透明底 |
| `--as-card-accent` / `--as-card-focus` | 金色强调 / 亮蓝焦点 |

局部 `on-dark-bg` / `on-light-bg` 使用现有主题的深浅色文字令牌。透明卡片跟随局部背景；`card-tint` 按自身浅色背景选择深色文字，白底徽章也始终保持深色符号。

整卡 fragment 的注解独占条目第一行，主文字换行缩进。符号、标题和正文一起出现，当前状态强调符号；正文保持正常颜色，卡片尺寸不变。未选卡内布局预设的跨顶边徽章仍不裁切。

### 在正文 block 中使用

```markdown
::: block
- **输入**
	- 整理已有材料
- **输出**
	- 检查交付结果
::: <!-- element class="list-cards list-layout-row card-tint card-title-body list-marker-none" -->
```

section 上的默认模式可由 block、列表或首级 `li` 覆盖。模板中只选择正文列表，不将 header、footer 或导航列表作为卡片。

### 旧接口

`list-flex-row`、`list-flex-col`、`list-flex-step`、`list-card-grid*` 继续保留原有行为，其他演示稿无需迁移。新示例使用上述独立类；不要把旧类的 padding、计数器或角色规则与 `list-cards` 混用。


