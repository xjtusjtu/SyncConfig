---
UID: 20230716144533
tags: 
aliases: 
description: block + element style
status: developing
modified: 2026-07-14T20:20:00
---

up:: [[P_Advanced Slides]]

参考链接：
- [Block Comments — Advanced Slides Documentation (mszturc.github.io)](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/blockcomment/)

# AS-Block Comments

> [!warning] 
> 虽然不知道为什么官方的 block comments 建议写在 `<name>` 后面，但是我们实践中发现，写在 结尾的 `:::` 是更推荐的做法，如下所示
> 
> ```
> ::: block 
> 
> blue
> 
> :::<!-- element style="background-color: blue;" -->
> ```


```
::: block

#### Header
_and_
Paragraph content
*in same block*

:::

---

no color

::: block <!-- element style="background-color: red;" -->

everything inside this block has red background color

::: block <!-- element style="background-color: blue;" -->

blue

:::

red

:::

no color

```

- 第二页的 block 是 *嵌套*

### 闭合 annotation

除写在开头的 `::: block <!-- element … -->` 外，更推荐把 `<!-- element … -->` 写在**闭合** `:::` 行（见文首 warning）。该技巧同样适用于 **模板槽**（如 `::: left` / `::: right`）的结束行，用于给整槽内容加 class（如 `scrollbox-x`）。详见 [[AS-Scrollbox#写法 A：闭合 ::: 加 element annotation（整栏滚动）]]。

### 模板槽与 block 的冲突

`::: block` **仅适合 slide 根级**的 styling 分组（上文红/蓝嵌套示例）。**禁止**在 `::: left`、`::: right`、`::: header` 等**模板变量槽**内再写 `::: block`：

- 解析器将所有 `::: 名称` 视为**平级**模板块，不会嵌套解析
- `::: left` 内的 `::: block` 会**截断 left**，开启名为 `block` 的新槽
- 模板通常无 `<% block %>` → 内容落入 `<% content %>`，表现为表格跑到错误区域

模板槽内需要滚动时，用 [[AS-Scrollbox]] 的两种写法（闭合 `:::` + scrollbox class，或 HTML `<div class="scrollbox-*">`），**不要**嵌套 `::: block`。

### 面板布局（无模板）：slide class + block

左右 / 上+下 / 上+左右等用 **路径 B**（`AS_basic.css` §3.x）。`cols-*` 分栏行随内容（等高取最高栏）；`rows-*` 的 bottom 或左右填充带占剩余高度。带导航：`template="[[ASTp-nav-shell]]" class="rows-1-2"`。**不要**无模板写 `::: left`：

```markdown
<!-- slide class="rows-1-2" -->

## 标题

::: block
顶部全宽
::: <!-- element class="tdiv" -->

::: block
左下
::: <!-- element class="ldiv" -->

::: block
右下
::: <!-- element class="rdiv" -->
```

面板 class：`ldiv` `rdiv` `mdiv` `tdiv` `bdiv`（及 `*img`）。见 [themes/as_basic.md](../themes/as_basic.md) § Panel layouts；演示 [AS_Basic Showcase](../showcase/AS_Basic%20Showcase.md)。

