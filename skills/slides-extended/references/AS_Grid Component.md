---
UID: 20230716093559
aliases: 
tags: 
description: 
status: planning
modified: 2026-11-19
---

up:: [[P_Advanced Slides]]
Related:: [[CSS布局-Grid Layout 网格布局]]

参考链接
- [Grid Component — Advanced Slides Documentation (mszturc.github.io)](https://mszturc.github.io/obsidian-advanced-slides/layout/grid/)

# AS_Grid Component

使用 `<grid>` 标签进行精确的拖放式布局：

```html
<grid drag="width height" drop="x y">
```

- `drag`：定义内容显示区域的宽高（*默认百分比*，可加 `px`）
- `drop`：定义内容在幻灯片上的位置

## dropleft

### 坐标定位

- 正 x：相对左边缘；负 x：相对右边缘
- 正 y：相对顶部；负 y：相对底部

### 命名位置

`center` / `top` / `bottom` / `left` / `right` / `topleft` / `topright` / `bottomleft` / `bottomright`

```md
<grid drag="40 30" drop="topleft" bg="red">
Top Left
</grid>

<grid drop="right" bg="green">
Right with default size
</grid>

<grid drag="80 30" drop="bottom" bg="coral">
Bottom
</grid>
```

未指定 drag 时默认为 `50 100`。

### 常见误用：`drop="x y"` 坐标语义

> [!warning] 先 x 后 y，不是「版面节奏百分比」
> `drop="48 0"` 表示 **距左 48%、距顶 0%**，**不是**「从顶部往下 48% 处放一块」。从 Marp Antai 迁移封面时，勿把纵向版面百分比直接抄进 `drop` 第一个或第二个数。

| 写法 | 含义 |
|------|------|
| `drag="100 25"` | 区域宽 100%、高 25%（百分比，可写 `px`） |
| `drop="0 25"` | 区域左上角在幻灯片 (0%, 25%) |
| `drop="bottom"` | 命名位置：贴底（见上表） |
| `drop="-5 10"` | x 为负：相对**右**边缘偏移 |

封面推荐对照 [[AsTp-Cover]]：

```html
<grid drag="100 25" drop="0 25" align="center"><% title %></grid>
<grid drag="100 50" drop="bottom" align="center"><% content %></grid>
```

`center: false` 时 grid 会被注入 `align-items: start`，需 slide class `grid-align-restore` — 详见 [P_obsidian-slides-extended.md](P_obsidian-slides-extended.md)。

## Flow 布局方向

```md
<grid drag="width height" drop="x y" flow="col | row">
```

- `flow="col"`：子元素垂直排列，均分间距
- `flow="row"`：子元素水平排列，均分间距

## Attributes

### Background `bg`

```html
<grid drag="55 50" drop="topleft" bg="orange">
```

支持 CSS Color Value（`orange`, `rgb(0,0,0)`, `#425232` 等）

### Padding `pad`

```html
<grid drag="50 50" drop="topleft" bg="orange" pad="0 50px">
```

### Border

```html
<grid drag="30 25" drop="left" border="thick dotted blue">
```

格式：`width style color`

### Animation `animate`

类型：`fadeIn` / `fadeOut` / `slideRightIn` / `slideLeftIn` / `slideUpIn` / `slideDownIn` / `scaleUp` / `scaleDown` 等

```html
<grid drag="..." drop="..." animate="fadeIn slower">
```


### Opacity

取值范围 `0.0` ~ `1.0`

### Rotate

```html
<grid drag="30 25" drop="12 15" bg="#B565A7" rotate="-10">
```

### Filter

类型：`blur` / `grayscale` / `contrast` / `invert` / `sepia` / `hue` / `saturate` / `bright`

### Fragments `frag`

```html
<grid drag="60 55" drop="5 10" bg="red" frag="1">
```

## Justify Content

控制 grid 组件如何在子元素之间分配空间：

| 值 | 效果 |
|------|------|
| `start` | 开头对齐 |
| `center` | 居中 |
| `space-between` | 两端对齐，项目之间间距相等 |
| `space-around` | 每个项目两侧间距相等 |
| `space-evenly` | 项目之间间距相等（默认） |
| `end` | 末尾对齐 |

## align

语义 shorthand，**不是**单一 CSS 属性。Slides Extended 在有 `align` 或 `flow` 时把 grid 变成 flex 容器，再按 `getAlignment()` 拆成多条样式：

- **`align-items`** — 子元素在交叉轴上的对齐：`flow="col"` 时控制左右，`flow="row"` 时控制上下。
- **`justify-content`** — 子元素在主轴上的分布：`flow="col"` 时控制上下，`flow="row"` 时控制左右；可被 grid 上的 `justify-content` 属性覆盖。
- **HTML `align="..."`** — 少数取值额外写入元素属性（`left` / `right` / `justify`），影响块内文字对齐
- **class `stretch-column` / `stretch-row`** — `align="stretch"` 时追加，子元素 `flex: 1` 撑满
- **不涉及 `align-content`**

取值：`left` / `right` / `center`（默认） / `justify` / `block` / `top` / `bottom` / `topleft` / `topright` / `bottomleft` / `bottomright` / `stretch`（`block` 与 `justify` 等价）

### 原理：grid → flex

| `flow` | 注入样式 | 额外 class |
|--------|----------|------------|
| 默认 / `col` | `display:flex; flex-direction:column` | — |
| `row` | `display:flex; flex-direction:row` | `flex-even` |

主轴就是子元素的排列方向，交叉轴与主轴垂直。默认横排、从左到右书写时，方向随 `flow` 变化：

| `flow` | 主轴（`justify-content`） | 交叉轴（`align-items`） |
|--------|---------------------------|-------------------------|
| `col`（默认） | 垂直，上 → 下 | 水平，左 → 右 |
| `row` | 水平，左 → 右 | 垂直，上 → 下 |

例如，使用 `justify-content="center"`：

- `flow="col"`：子元素整体在垂直方向（上下）居中。
- `flow="row"`：子元素整体在水平方向（左右）居中。

`align-items: center` 控制另一条轴：`col` 时左右居中，`row` 时上下居中。

注意：Slides Extended 的 Grid 属性写 `flow="col|row"`；对应的 CSS 属性是 `flex-direction: column|row`，其中 CSS 写 `column`，不写 `col`。

### 与 `justify-content` 属性的关系

- `align` 会**顺带**设定默认 `justify-content`（见下表第三列）。
- grid 上若**另写** `justify-content="..."`，以该属性为准，覆盖 `align` 给出的默认值。
- `align` 对 `align-items` 的设定**不受** `justify-content` 属性影响。

### `center: false` 覆盖

演示稿 frontmatter 设 `center: false` 时，插件会对所有 grid **强制注入**内联 `align-items: start`，覆盖 `align` 映射出的 `align-items`（例如封面 `align="center"` 仍可能靠左）。解法：slide 加 class `grid-align-restore`（[`AS_basic.css`](../assets/css/AS_basic.css)），并配合 [AsTp-Cover](../assets/templates/AsTp-Cover.md) 等模板的 `align="center"`。详见 [P_obsidian-slides-extended.md](P_obsidian-slides-extended.md) § center: false 与 grid align-items。

### 映射表：`flow="col"`（默认）

| `align` | `align-items` | 默认 `justify-content` | HTML `align` | 额外 class |
|---------|---------------|------------------------|--------------|------------|
| `center`（默认） | `center` | `center` | — | — |
| `left` | `flex-start` | `space-evenly` | `left` | — |
| `right` | `flex-end` | `space-evenly` | `right` | — |
| `top` | `center` | `flex-start` | — | — |
| `bottom` | `center` | `flex-end` | — | — |
| `topleft` | `flex-start` | `flex-start` | `left` | — |
| `topright` | `flex-end` | `flex-start` | `right` | — |
| `bottomleft` | `flex-start` | `flex-end` | `left` | — |
| `bottomright` | `flex-end` | `flex-end` | `right` | — |
| `stretch` | `center` | `space-evenly` | — | `stretch-column` |
| `justify` / `block` | `center` | `space-evenly` | `justify` | — |

在 `flow="col"` 下：`left` / `right` / `center` → **`align-items`**（水平）；`top` / `bottom` → **`justify-content`**（垂直）；角落值同时改两者。

### 映射表：`flow="row"`

| `align` | `align-items` | 默认 `justify-content` | HTML `align` | 额外 class |
|---------|---------------|------------------------|--------------|------------|
| `center`（默认） | `center` | `center` | — | — |
| `left` | `center` | `space-evenly` | `left` | — |
| `right` | `center` | `space-evenly` | `right` | — |
| `top` | `flex-start` | `space-evenly` | — | — |
| `bottom` | `flex-end` | `space-evenly` | — | — |
| `topleft` | `flex-start` | `space-evenly` | `left` | — |
| `topright` | `flex-start` | `space-evenly` | `right` | — |
| `bottomleft` | `flex-end` | `space-evenly` | `left` | — |
| `bottomright` | `flex-end` | `space-evenly` | `right` | — |
| `stretch` | `center` | `space-evenly` | — | `stretch-row` |
| `justify` / `block` | `center` | `space-evenly` | `justify` | — |

### 速记

```
align = 语义 shorthand
      → align-items      （交叉轴）
      → justify-content  （主轴默认值，可被 justify-content 属性覆盖）
      → 有时 HTML align  （块内文字）
      → stretch 时加 class
      ✗ 不涉及 align-content
```

## 完整属性速查

- **drag**=*width height*
- **drop**=*x y | topleft | top | topright | left | center | right | bottomleft | bottom | bottomright*
- **flow**=*col | row*
- **bg**=*color name | #425232 | rgb(255, 99, 71) | hsl(0, 100%, 50%)*
- **pad**=*all sides | vertical horizontal | top right bottom left*
- **align**=*left | right | center | justify | block | top | bottom | topleft | topright | bottomleft | bottomright | stretch*
- **border**=*width style color*
- **animate**=*fadeIn | fadeOut | slideRightIn | slideLeftIn | slideUpIn | slideDownIn | slideRightOut | slideLeftOut | slideUpOut | slideDownOut | scaleUp | scaleUpOut | scaleDown | scaleDownOut* | slower | faster
- **opacity**=*0.1…1*
- **rotate**=*0…360*
- **filter**=*blur | bright | contrast | grayscale | hue | invert | saturate | sepia*
- **frag**=*1*
- **justify-content**=*start | center | space-between | space-around | space-evenly | end*
- **style**=*<any>*
- **class**=*<any>*
