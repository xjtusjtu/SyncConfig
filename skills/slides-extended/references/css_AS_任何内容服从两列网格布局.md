---
tags:
  - code_snippet
language: CSS
description:
path:
modified: 2024-09-24T11:57:09
---

up:: [[CSS布局-Grid Layout 网格布局]]
Related:: 


## 两列网格布局

```CSS
.reveal .slides div.g-columns {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    width: 100%;
    align-content: center;
    justify-items: center;
}
```

`g-columns` 通过 element 注解加在 **block / grid 节点自身**（`::: block` 闭合行），不是子级 `.as-body`。

![](https://s3.bmp.ovh/imgs/2024/09/25/0fc82890d2c29c44.png)