---
UID: 20260521143000
tags: 
aliases:
- AS_Split Component
up: "[[P_Advanced Slides]]"
description: 
status: developing
modified: 2026-05-21T14:40:00
---

[toc]

参考链接：
- [Split Component — Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/layout/split/)


# AS_Split Component

使用 `<split>` 标签将 slide 内容分割为 rows 和 columns

## 属性

### `even`

设置 `even` 属性后，split 元素内的内容被均匀分割

```md
<split even>

![](https://picsum.photos/id/1005/250/250)
![](https://picsum.photos/id/1010/250/250)
![](https://picsum.photos/id/1025/250/250)
</split>
```

Example: 在包含 3 个子元素的 split 中，每个子元素占据 slide 宽度的 1/3

### `gap`

添加 `gap` 属性后，每个元素之间会出现间距

```md
<split even gap="3">

**Lorem Ipsum** is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s

when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap

into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem
</split>
```

Example: 此 split 中每个元素之间有 3em 的间距

### `left` & `right`

按比例分割 slide，`left` 和 `right` 代表 slide 列的宽度比例

```md
<split left="2" right="1" gap="2">

**Lorem Ipsum** is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s
when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap
	
into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem
</split>
```

Example: 此 split 中左侧元素的宽度是右侧元素的两倍

### `wrap`

设置 `wrap` 属性可以定义每行显示多少个子元素后换行

```md
<split wrap="4">

![](https://picsum.photos/id/1010/250/250)

![](https://picsum.photos/id/1011/250/250)

![](https://picsum.photos/id/1012/250/250)

![](https://picsum.photos/id/1013/250/250)

![](https://picsum.photos/id/1014/250/250)

![](https://picsum.photos/id/1015/250/250)
</split>
```

Example: 此 split 有 2 行，第一行 4 张图片，第二行 2 张图片

## `no-margin`

By adding no margin attribute automatic gaps between rows and column gets removed:
添加 `no-margin` 属性后，行与列之间的自动间距会被移除

```md
<split no-margin>

![](https://picsum.photos/id/1001/250/250)
![](https://picsum.photos/id/1002/250/250)
![](https://picsum.photos/id/1003/250/250)
![](https://picsum.photos/id/1004/250/250)
![](https://picsum.photos/id/1005/250/250)
![](https://picsum.photos/id/1006/250/250)
![](https://picsum.photos/id/1009/250/250)
![](https://picsum.photos/id/1008/250/250)
</split>
```

Example: 此 split 的行列之间没有间距
