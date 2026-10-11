---
marp: true
theme: Marp_slate
paginate: true
size: 16:9
header: 'Customized Marp Layout Showcase'
footer: 'Xiaobu'
style: |
  mark {
    background-color: rgba(251, 211, 234, 0.6);
    border-radius: 2px;
    padding: 2px 4px;
  }
---

<!-- AGENT: Marp_basic layout demo deck (unique authority). Search <!-- AGENT: layout= --> for copy-paste slides. CSS: skills/marp/assets/css/Marp_basic.css, Marp_blue.css. -->

<!-- AGENT: layout=cover_a | 封面信息表 -->
<!-- _class: cover_a -->
<!-- _header: "" -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

# Marp Basic Showcase

## Marp_basic / Marp_blue 主题布局与样式演示

| 汇报人：| 吕小布 |
|:--:|:--:|
| 导师： | 顾锋教授 |
| 单位： | Example Org |

---

<!-- AGENT: layout=toc_a | 目录页，需 _header: CONTENTS -->
<!-- _class: toc_a -->
<!-- _header: "CONTENTS" -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

- [启用主题](#启用主题)
- [类名速查](#类名速查)
- [设计令牌与全局样式](#设计令牌与全局样式)
- [封面页](#封面页)
- [目录页](#目录页)
- [分栏与分区](#分栏与分区)
- [列表分列](#列表分列)
- [其他版式](#其他版式)
- [滚动容器](#滚动容器)
- [图片与 HTML](#图片与-html)
- [导航栏与尾页](#导航栏与尾页)
- [调试](#调试)

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 启用主题

注册 CSS、开启 `enableHtml`、文稿 frontmatter；蓝主题用 `theme: Marp_blue`。

---

<!-- AGENT: layout=setup-vscode | VS Code 注册主题 CSS -->
<!-- _footer: "" -->

## VS Code 注册

用 **GitHub raw 直链**（任意库通用）：

```json
{
  "markdown.marp.themes": [
    "https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/marp/assets/css/Marp_basic.css",
    "https://raw.githubusercontent.com/xjtusjtu/SyncConfig/main/skills/marp/assets/css/Marp_blue.css"
  ],
  "markdown.marp.enableHtml": true
}
```

本地替代：把本 skill 的 `assets/css/` 复制进库，改用 vault 相对路径。

> 回退：若 raw 失败（MIME 被拒），改用 jsDelivr 镜像 `https://cdn.jsdelivr.net/gh/xjtusjtu/SyncConfig@main/skills/marp/assets/css/Marp_basic.css`。

`cols-*`、面板 `div`、`scrollbox-*`、Mermaid 均需 `enableHtml: true`。

---

<!-- AGENT: layout=setup-frontmatter | 标准 frontmatter -->
<!-- _footer: "" -->

## 文稿 frontmatter

```yaml
---
marp: true
theme: Marp_basic   # 或 Marp_blue
paginate: true
size: 16:9
header: '![width:130px](logo.png) Org Name'
footer: '汇报标题'
math: katex
---
```

CSS 头：`@theme Marp_basic` / `@theme Marp_blue`（一般无需改）。

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 类名速查

section / div / img 常用 class 一览；检索 `<!-- AGENT: layout=` 可定位演示页。

---

<!-- AGENT: layout=cheatsheet-section | section 类速查 -->
<!-- _footer: "" -->

## section 类

| 类 | 作用 |
|:---|:-----|
| `cover_a`–`cover_e` | 五种封面 |
| `cover_f` | 深色渐变封面 / 章节过渡页 |
| `toc_a` / `toc_b` | 目录页 |
| `cols-2` / `cols-3` | 1:1 / 三栏 |
| `cols-2-73` / `64` / `37` / `46` | 比例双栏 |
| `rows-2` / `rows-1-2` / `rows-2-1` | 上下分区 |
| `cols2_ol_sq` / `ol_ci` / `ul_sq` / `ul_ci` | 两列列表 |
| `fglass` | 列表装饰（与 `cols2_*` 联用） |
| `fixedtitleB` / `footnote` | 固定标题 / 脚注 |
| `navbar` / `lastpage` / `trans` | 顶栏 / 致谢 / 过渡页 |
| `th_fill` | 表头填充主题强调色 |
| `quote_mark` | 引用框改回「引号装饰」样式 |
| `zebra_bar` | 顶部 9px 主题强调色条（默认无） |

---

<!-- AGENT: layout=cheatsheet-panel | 面板与工具类速查 -->
<!-- _footer: "" -->

## 面板与工具类

| 类 | 作用域 | 说明 |
|:---|:-------|:-----|
| `ldiv` / `mdiv` / `rdiv` | div | 左中右内容区 |
| `tdiv` / `bdiv` | div | 上下区 |
| `limg` / `mimg` / `rimg` / `timg` / `bimg` | div | 图片面板（自动居中） |
| `.div` | div | `fixedtitleB` 正文区 |
| `scrollbox` / `scrollbox-x` / `scrollbox-y` | div | 双向 / 横 / 纵滚动 |
| `alt` 以 `C` 结尾 | img | 块级居中 |

写法：`<!-- _class: cols-2-64 -->` + `<div class="ldiv">` / `rdiv`。

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 设计令牌与全局样式

`:root` 变量与标题 / 强调色默认值；单稿可用 frontmatter `style:` 覆盖。

---

<!-- AGENT: layout=tokens | 设计令牌表 -->
<!-- _footer: "" -->

## 设计令牌（节选）

| 变量 | 默认（basic） | 用途 |
|:-----|:--------------|:-----|
| `--font-size-main` | 18px | section 根字号、正文 |
| `--font-size-1` | 45px | `h1` |
| `--font-size-2-3` | 30px | `h2` |
| `--font-size-h3` | 25px | `h3` |
| `--font-size-code` | 14px | `pre code` |
| `--font-size-cover-title` | `max(52px, --font-size-1 * 1.2)` | 封面主标题（cover_a–e） |
| `--font-size-cover-body` | `max(22px, --font-size-main * 1.08)` | 封面正文 / cover_a 信息表 |
| `--foot-size-subtitle` | 兼容别名（见 `:root`） | 封面副标题（cover_a–e / lastpage） |
| `--color-strong` | `#dc143c` | `**粗体**` |
| `--color-em` | `#20b2aa` | `*斜体*` |
| `--color-blockquote-bg` / `-border` | `--color-quote` / `--color-much` | 引用框底色 / 左边框 |
| `--color-table-header-bg` / `-fg` | `--color-much` / `--color-title` | `th_fill` 表头背景 / 文字 |
| `--color-cover-from` / `-to` | `#592b32` / `#773f49` | `cover_f` 渐变 |
| `--color-coverbg` | `var(--color-cover-to)` | `cover_a`–`cover_e` 色块 |
| `--color-cover-accent` / `-muted` | `#ffd5d9` / `#ead8db` | 封面副标题/强调文字、正文/斜体 |

`Marp_blue` / `Marp_slate` 覆盖配色令牌（含引用框、表头、封面渐变），布局类不变。

---

<!-- AGENT: layout=tokens-override | style 覆盖示例 -->
<!-- _footer: "" -->

## 覆盖令牌

```yaml
style: |
  :root {
    --font-size-main: 16px;
    --font-size-1: 40px;
  }
```

本稿另用 `style:` 为 `<mark>` 补了主题未内置的高亮样式。

---

<!-- AGENT: layout=global-styles | 全局样式要点 -->
<!-- _footer: "" -->

## 全局样式要点

| 元素 / Markdown | 效果 |
|:----------------|:-----|
| `h1` | 45px，居中 |
| `h2`–`h6` | 主题色字号阶梯；`h4` 前有 🍀；封面/尾页副标题用 `h2` |
| `**粗体**` / `*斜体*` | 红 / 青绿 |
| `<u>下划线</u>` | 红色底边线 |
| `paginate: true` | 右下角 `Page n / total` |
| `table` | `0.8em`、满宽、`table-layout: fixed`；表头默认仅描边 |
| `th_fill`（class） | 表头填充主题强调色 |
| `blockquote` | 浅底 + 左侧强调色粗边框（默认） |
| `quote_mark`（class） | 引用框改为「引号装饰」样式 |
| `zebra_bar`（class） | 顶部 9px 色条，颜色为 `--color-much`；三套主题默认均无 |

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 封面页

六种 `cover_*` 版式（`cover_a`–`cover_e` + 深色渐变 `cover_f`）；`cover_a` 使用 **table** 呈现个人信息。**副标题用 `##`（h2）**，勿用 `######`；封面 / toc / lastpage 建议 `<!-- _paginate: "" -->`。

---

<!-- AGENT: layout=cover_b | 居中封面 -->
<!-- _class: cover_b -->
<!-- _header: "" -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

# cover_b

## 副标题示例

@Xiaobu
学科：组织管理系
发布时间：2026年10月1日
mail@example.com
通讯地址：上海市徐汇区华山路1954号

---

<!-- AGENT: layout=cover_c | header logo + footer 校训 -->
<!-- _class: cover_c -->
<!-- _paginate: "" -->
<!-- _footer: 饮水思源 爱国荣校 -->
<!-- _header: ![图片](https://raw.githubusercontent.com/weijianwen/SJTU-logo-banner/master/SJTU_BANNER/PNG/sjtubannersilver.png) -->

# cover_c

## 副标题示例（header 放 logo，footer 放校训）

@Xiaobu
学科：组织管理系
发布时间：2026年10月1日
mail@example.com
通讯地址：上海市徐汇区华山路1954号

---

<!-- AGENT: layout=cover_d | 仅 footer 校训 -->
<!-- _class: cover_d -->
<!-- _paginate: "" -->
<!-- _footer: "饮水思源 爱国荣校" -->

# cover_d

## 副标题示例（仅 footer 校训）

@Xiaobu
学科：组织管理系
发布时间：2026年10月1日
mail@example.com
通讯地址：上海市徐汇区华山路1954号

---

<!-- AGENT: layout=cover_e | header + footer 均可放 logo -->
<!-- _class: cover_e -->
<!-- _paginate: "" -->
<!-- _header: ![图片](https://raw.githubusercontent.com/weijianwen/SJTU-logo-banner/master/SJTU_LOGO/PNG/sjtulogosilver.png) -->
<!-- _footer: ![图片](https://raw.githubusercontent.com/weijianwen/SJTU-logo-banner/master/SJTU_BANNER/PNG/sjtubannersilver.png) -->

# cover_e

## 副标题示例（header + footer 均可放 logo）

@Xiaobu
学科：组织管理系
发布时间：2026年10月1日
mail@example.com
通讯地址：上海市徐汇区华山路1954号

---

<!-- AGENT: layout=cover_f | 深色渐变封面 / 章节过渡页 -->
<!-- _class: cover_f -->
<!-- _header: "" -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

# 标题：cover_f

## 副标题：深色渐变封面 / 章节过渡页

**加粗**

*配色来自 `--color-cover-*` 令牌*

正文

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 目录页

`toc_a` 需 `<!-- _header: "CONTENTS" -->`；`toc_b` 需多行 header（目录 / CONTENTS / logo）。

---

<!-- AGENT: layout=toc_b | 多行 header 目录 -->
<!-- _class: toc_b -->
<!-- _header: 目录<br>CONTENTS<br>![图片](https://raw.githubusercontent.com/weijianwen/SJTU-logo-banner/master/SJTU_LOGO/PNG/sjtulogosilver.png) -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

- 第一章：背景与目标
- 第二章：方法与过程
- 第三章：结果与建议
- 第四章：总结与展望

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 分栏与分区

`cols-*` / `rows-*` 分栏布局（1:1 用 `cols-2`，6:4 用 `cols-2-64`；上 1+下 2 用 `rows-1-2`，上 2+下 1 用 `rows-2-1`）。

---

<!-- AGENT: layout=cols-2 | 1:1 双栏 + ldiv/rdiv -->
<!-- _class: cols-2 -->

## cols-2 (1:1)

<div class="ldiv">

- 左栏要点 A
- 左栏要点 B
- 左栏要点 C

</div>

<div class="rdiv">

| 指标 | 数值 |
|:---|---:|
| A | 12 |
| B | 34 |
| C | 56 |

</div>

---

<!-- AGENT: layout=cols-3 | 三栏 + ldiv/mdiv/rdiv -->
<!-- _class: cols-3 -->

## cols-3 (1:1:1)

<div class="ldiv">

### 左
- A
- B

</div>

<div class="mdiv">

### 中
- C
- D

</div>

<div class="rdiv">

### 右
- E
- F

</div>

---

<!-- AGENT: layout=cols-2-73 | 7:3 双栏 -->
<!-- _class: cols-2-73 -->

## cols-2-73 (7:3)

<div class="ldiv">

宽列正文：适合长文本、图表说明或多层列表。

- 第一部分
- 第二部分
- 第三部分

</div>

<div class="rdiv">

窄列补充信息：

- 结论 1
- 结论 2

</div>

---

<!-- AGENT: layout=cols-2-64 | 6:4 双栏 -->
<!-- _class: cols-2-64 -->

## cols-2-64 (6:4)

<div class="ldiv">

左宽右窄布局示例。

</div>

<div class="rdiv">

- 侧栏
- 标签
- 备注

</div>

---

<!-- AGENT: layout=cols-2-37 | 3:7 双栏 -->
<!-- _class: cols-2-37 -->

## cols-2-37 (3:7)

<div class="ldiv">

左侧导航：

- 目录一
- 目录二
- 目录三

</div>

<div class="rdiv">

右侧主体内容区域。

</div>

---

<!-- AGENT: layout=cols-2-46 | 4:6 双栏 -->
<!-- _class: cols-2-46 -->

## cols-2-46 (4:6)

<div class="ldiv">

左侧摘要区。

</div>

<div class="rdiv">

右侧主叙述区。

</div>

---

<!-- AGENT: layout=rows-2 | 上下双区 + tdiv/bdiv -->
<!-- _class: rows-2 -->

## rows-2 (Top + Bottom)

<div class="tdiv">

上半部分内容（可放图、表、代码）。

</div>

<div class="bdiv">

下半部分内容（可放结论、补充说明）。

</div>

---

<!-- AGENT: layout=rows-1-2 | 上全宽 + 下左右 -->
<!-- _class: rows-1-2 -->

## rows-1-2 (上 1 + 下 2)

<div class="tdiv">

顶部全宽内容。

</div>

<div class="ldiv">

左下区内容。

</div>

<div class="rdiv">

右下区内容。

</div>

---

<!-- AGENT: layout=rows-2-1 | 上左右 + 下全宽 -->
<!-- _class: rows-2-1 -->

## rows-2-1 (上 2 + 下 1)

<div class="ldiv">

左上区内容。

</div>

<div class="rdiv">

右上区内容。

</div>

<div class="bdiv">

底部全宽内容。

</div>

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 列表分列

两列列表 `cols2_*`（先填满左列：1–3 左、4–6 右）；`cols2_ol_sq` / `cols2_ol_ci` 为有序列表（方形 / 圆形序号），`cols2_ul_*` 为无序小色块；常配合 `fglass`。

---

<!-- AGENT: layout=cols2_ol_sq | 有序列表两列方形序号 -->
<!-- _class: cols2_ol_sq fglass -->

## cols2_ol_sq

`<!-- _class: cols2_ol_sq fglass -->`

1. 列表项 1
2. 列表项 2
3. 列表项 3
4. 列表项 4
5. 列表项 5
6. 列表项 6

---

<!-- AGENT: layout=cols2_ol_ci | 有序列表两列圆形序号 -->
<!-- _class: cols2_ol_ci fglass -->

## cols2_ol_ci

有序列表为**圆形**序号块（`ol_ci`）；无序列表小色块为方形。对比 `cols2_ol_sq` 的方形序号。

`<!-- _class: cols2_ol_ci fglass -->`

1. 章节 A
2. 章节 B
3. 章节 C
4. 章节 D
5. 章节 E
6. 章节 F

---

<!-- AGENT: layout=cols2_ul_ci | 无序列表两列圆形色块 -->
<!-- _class: cols2_ul_ci fglass -->

## cols2_ul_ci

`<!-- _class: cols2_ul_ci fglass -->`

- 模块 A
- 模块 B
- 模块 C
- 模块 D
- 模块 E
- 模块 F

---

<!-- AGENT: layout=cols2_ul_sq | 无序列表两列方形色块 -->
<!-- _class: cols2_ul_sq fglass -->

## cols2_ul_sq

`<!-- _class: cols2_ul_sq fglass -->`

- 模块 A
- 模块 B
- 模块 C
- 模块 D
- 模块 E
- 模块 F

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 其他版式

`fixedtitleB`、`footnote`、`trans`；左图右文 / 双图并列见下方 `cols-2` 示例。

---

<!-- AGENT: layout=fixedtitleB | 固定标题区 + .div 正文 -->
<!-- _class: fixedtitleB -->

## fixedtitleB

<div class="div">

该页使用 `fixedtitleB` 的内容区 `.div`。

- 标题由 `slideheading` 区控制
- 正文位于 `content` 区

</div>

---

<!-- AGENT: layout=footnote | 正文 tdiv + 脚注 bdiv -->
<!-- _class: footnote -->

<div class="tdiv">

## footnote

正文区域：用于主要结论与图表说明。

</div>

<div class="bdiv">

脚注区域：数据口径、样本范围、更新时间等。

</div>

---

<!-- AGENT: layout=trans | 过渡页 -->
<!-- _class: trans -->
<!-- _header: "" -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## trans

过渡 / 章节分隔页（`section.trans` 背景色令牌 `--color-trans`）。

---

<!-- AGENT: layout=zebra_bar | 按需启用顶部主题色条 -->
<!-- _class: zebra_bar -->
<!-- _footer: "" -->

## 顶部色条 `zebra_bar`

三套主题默认均无顶部色条，只有调用 `zebra_bar` 才显示。

```markdown
<!-- _class: zebra_bar -->
<!-- _class: cols-2 zebra_bar -->
<!-- _class: cover_f zebra_bar -->
```

每页选用一条 class 指令；色条为 9px，颜色随主题的 `--color-much` 变化。

---

<!-- AGENT: layout=th_fill | 表头填充主题强调色 -->
<!-- _class: th_fill -->
<!-- _footer: "" -->

## 表头填充 `th_fill`

| 变量 | 含义 | 默认 |
|:-----|:-----|:-----|
| `--color-table-header-bg` | 表头背景 | `--color-much` |
| `--color-table-header-fg` | 表头文字 | `--color-title` |

默认表格仅描边；`th_fill` 给表头填充主题强调色，配色随主题变化。

---

<!-- AGENT: layout=quote_mark | 引用框引号装饰 -->
<!-- _class: quote_mark -->
<!-- _footer: "" -->

## 引用框 `quote_mark`

> 默认引用框为浅底 + 左侧强调色粗边框。
> `quote_mark` 改回带引号装饰的旧版式（原 Marp_basic 样式）。

---

<!-- AGENT: layout=cols-2+limg+rdiv | 左图右文 -->
<!-- _class: cols-2 -->

## 左图右文（cols-2 替代 illustration）

<div class="limg">

![width:280px](https://dummyimage.com/280x480/cccccc/333333&text=Figure)

图 A

</div>

<div class="rdiv">

**说明文字**

- 子要点一
- 子要点二
- 子要点三

</div>

---

<!-- AGENT: layout=cols-2+limg+rimg | 双图并列 -->
<!-- _class: cols-2 -->

## 双图并列（cols-2 替代 sidebyside）

<div class="limg">

![width:280px](https://dummyimage.com/280x180/cccccc/333333&text=A)

图 A

</div>

<div class="rimg">

![width:280px](https://dummyimage.com/280x180/cccccc/333333&text=B)

图 B

</div>

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 滚动容器

`scrollbox` / `scrollbox-x` / `scrollbox-y`；分栏内 `scrollbox-y` 须放在 blockquote **之前**。

---

<!-- AGENT: layout=scrollbox-y | 纵向滚动长表 -->
<!-- _footer: "" -->

## scrollbox-y（长表）

<div class="scrollbox-y" style="width: 100%; max-height: 420px">

| 机构 Code | 医生编号 | 医生ID |
|:----------|:---------|:-------|
| H202507250028 | D202602240030 | `3d467967-aab7-4c2e-9f01-0001` |
| H202507250029 | D202602240031 | `3d467967-aab7-4c2e-9f01-0002` |
| H202507250030 | D202602240032 | `3d467967-aab7-4c2e-9f01-0003` |
| H202507250031 | D202602240033 | `3d467967-aab7-4c2e-9f01-0004` |
| H202507250032 | D202602240034 | `3d467967-aab7-4c2e-9f01-0005` |
| H202507250033 | D202602240035 | `3d467967-aab7-4c2e-9f01-0006` |
| H202507250034 | D202602240036 | `3d467967-aab7-4c2e-9f01-0007` |
| H202507250035 | D202602240037 | `3d467967-aab7-4c2e-9f01-0008` |
| H202507250036 | D202602240038 | `3d467967-aab7-4c2e-9f01-0009` |
| H202507250037 | D202602240039 | `3d467967-aab7-4c2e-9f01-0010` |

</div>

---

<!-- AGENT: layout=scrollbox-y-in-cols | 分栏内 scrollbox-y，须在 blockquote 前 -->
<!-- _class: cols-2-64 -->

## 分栏内 scrollbox-y

<div class="ldiv">

标 ★ 者为 A 中 3 家机构相关医生。

</div>

<div class="rdiv">

<div class="scrollbox-y">

| 机构 | 医生 | 备注 |
|:-----|:-----|:-----|
| H001 | D001 | ★ |
| H002 | D002 | |
| H003 | D003 | ★ |
| H004 | D004 | |
| H005 | D005 | ★ |
| H006 | D006 | |
| H007 | D007 | |
| H008 | D008 | |

</div>

> 顺序：scrollbox-y **先于** blockquote，才能占满中间高度。

</div>

---

<!-- AGENT: layout=scrollbox-x-mermaid | 横向滚动 + Mermaid -->
<!-- _footer: "" -->

## scrollbox-x + Mermaid

宽流程图关闭 `useMaxWidth`，包在 `scrollbox-x` 中：

<div class="scrollbox-x">

<div class="mermaid">
%%{init: {"flowchart": {"useMaxWidth": false}}}%%
flowchart LR
    A[机构线索信息] --> B{电话外呼}
    B -->|接通| C[跟进记录]
    B -->|未接通| D[再次外呼]
    C --> E[合作意向]
</div>

</div>

---

<!-- AGENT: layout=scrollbox-table-rules | scrollbox 内表格行为 -->
<!-- _footer: "" -->

## scrollbox 内表格

| 容器 | 表格宽度 | 说明 |
|:-----|:---------|:-----|
| `scrollbox` / `scrollbox-x` | `width: max-content` | 保持原始宽度，触发横向滚动 |
| `scrollbox-y` | `width: 100%` + `fixed` | 随容器换行，纵向滚动 |
| 普通 slide / grid | `width: 100%` | 单元格换行，不撑破列宽 |

全页宽表可直接写 Markdown 表格，无需 scrollbox。

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 图片与 HTML

居中用 `alt` 以 `C` 结尾；`mark` / checkbox 等非布局元素。

---

<!-- AGENT: layout=img-center-C | alt 以 C 结尾居中 -->
<!-- _footer: "" -->

## 图片居中：`alt` 以 `C` 结尾

![width:320px C](https://dummyimage.com/320x180/cccccc/333333&text=Centered)

```markdown
![C](Overview.svg)
![width:320px C](image.png)
```

对应 CSS：`img[alt$="C"] { display: block; margin: auto; }`。header logo：`header: '![width:130px](logo.png) Org'`。

---

<!-- AGENT: layout=html-extras | mark 与 checkbox -->
<!-- _footer: "" -->

## mark 与 checkbox

主题 **未内置** `mark`；本稿在 frontmatter `style:` 中追加。示例：<mark>高亮片段</mark>

<form>
<input type="checkbox"> 选项 A
<input type="checkbox" checked> 选项 B
</form>

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 导航栏与尾页

`navbar` 通过 `<!-- _header: ... -->` 实现顶栏导航；`lastpage` 用于致谢与联系方式。

---

<!-- AGENT: layout=navbar | 顶栏导航 -->
<!-- _class: navbar -->
<!-- _header: \ ***Marp_basic Showcase*** *封面* *目录* *分栏* *列表* **导航栏** *尾页*-->
<!-- _footer: "" -->

## navbar

本页演示 `section.navbar` 顶栏导航与正文避让。

---

<!-- AGENT: layout=section-intro | 章节说明页 -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## 调试

scroll 不生效时检查内容高度与 `scrollbox-y` 在 slide 内的顺序。

---

<!-- AGENT: layout=debug | 调试清单 -->
<!-- _footer: "" -->

## 调试清单

1. **VS Code**：Developer: Open Webview Developer Tools → 检查 `<section>` 的 class / grid。
2. **浏览器**：导出 HTML，F12 看 `.scrollbox-y` 是否出现滚动条。
3. **常见原因**：内容未超出容器高度；或 `scrollbox-y` 放在会撑开高度的元素之后。
4. 分栏内优先：`scrollbox-y` 放在 blockquote **之前**，或设明确 `max-height`。

---

<!-- AGENT: layout=lastpage | 致谢联系方式 -->
<!-- _class: lastpage -->
<!-- _footer: "" -->
<!-- _paginate: "" -->

## Thank You

<div class="icons">

- &nbsp;
  - 邮箱：mail@example.com
- &nbsp;
  - 微信：your-wechat-id
- &nbsp;
  - 主页：example.com

</div>

<script src="https://unpkg.com/mermaid@11.15.0/dist/mermaid.min.js"></script>
<script>mermaid.initialize({
  startOnLoad: true,
  themeVariables: { fontSize: "18px" }
});</script>
