---
UID: 20260521144003
tags:
aliases:
- AS-Excalidraw support
up: "[[P_Advanced Slides]]"
description: 在幻灯片中嵌入 Excalidraw 手绘图形
status: developing
modified: 2026-05-21T14:40:00
---

[toc]

参考链接：
- [Excalidraw support — Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/excalidraw/)

# AS-Excalidraw support

## 前置条件

需要在 Excalidraw 设置中启用 **Auto-Export SVG / PNG** 自动导出功能。

## 使用方式

```md
#### Excalidraw support

![[Sample.excalidraw|100]]

![[Sample.excalidraw]] <!-- element style="width:300px; height:400px" -->
```

可直接使用 [[AS-Element Annotations]] 调整 Excalidraw 图形的尺寸和样式。
