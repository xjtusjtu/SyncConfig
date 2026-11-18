# AS Callouts

Slides Extended 支持 Obsidian 风格 callout。基础写法与 element / grid 调样式见下。

## 基础示例

```markdown
> [!tip] This tip has a custom Header
> This is an Tip with a custom Title
<!-- element style="width:40%"-->

> [!warning] 
> This warning is aligned left
<!-- element style="width:20%;font-size:24px" align="left"-->

<br>

> [!error] 
> Callouts support manipulation through annotations
<!-- element style="width:20%;font-size:24px" rotate="15"-->

<grid drag="30 30" drop="11 68" style="font-size:36px">
> [!example]
> Here is an Example for an Callout in a Slide. Callouts support dark and white backgrounds and could be sized by annotations
</grid>
```

两种方法调整样式：

1. 后面紧跟 [[AS-Element Annotations]]（`style` / `width` / `font-size` / `align` 等）
2. 整个 callout 置于 grid 布局中，用 grid attributes 调显示

## 自定义 `data-type`

```markdown
> [!qq]
> ddada
```

渲染为：

```html
<div class="callout callout-color-default" data-type="qq">
  <div class="callout-title">…</div>
  <div class="callout-content">…</div>
</div>
```

`[!type]` 中的 type（及空格分隔的多个词）进入 `data-type`，可用 CSS 按属性选择器定制。

### AS_basic 已支持的修饰

见 `AS_basic.css` §6。写法：`> [!note blank]`、`> [!warning noborder]` 等（空格叠词 → `data-type="note blank"`）。

| 修饰 | 效果 |
|:-----|:-----|
| `blank` | 透明外壳；隐藏标题 |
| `notitle` | 仅隐藏标题 |
| `noborder` | 去掉左边条 / 底色 / 阴影（标题仍显示，除非再叠 `blank` / `notitle`） |

多图 / mermaid 等**横排长廊**不要用 callout，改用独立类 [[AS-Scrollbox#gallery]]（`gallery`）。

## 坑：多行图片会截断 callout

Slides Extended 把行内/块级图嵌处理进 markdown 管线后，callout 常在**第一张图**处结束；后面仍带 `>` 的行变成普通 `<blockquote>`，不再带 `data-type`。

**`![[wikilink]]` 与 `![](url)` 多行都会触发。**

```markdown
<!-- ❌ 第二行起掉出 callout -->
> [!noborder blank]
> ![](./a.svg)
> ![](./b.svg)

<!-- ❌ 同理 -->
> [!noborder blank]
> ![[a.svg|1000]]
> ![[b.svg|1000]]
```

可行写法：

1. **推荐**：`gallery` 容器（多行图合法）— 见 [[AS-Scrollbox#gallery]]
2. 同行走多张图（仍用 callout 时）
3. 手写 HTML `<div class="callout" data-type="…">…</div>`

这是插件解析限制，不能靠 CSS 合并 DOM。
