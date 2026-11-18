---
UID: 20260521144006
tags:
aliases:
- AS-Charts support
up: "[[P_Advanced Slides]]"
description: 图表支持（Obsidian Charts / Reveal.js Charts）
status: developing
modified: 2026-05-21T14:40:00
---

[toc]

参考链接：
- [Charts support — Advanced Slides Documentation](https://mszturc.github.io/obsidian-advanced-slides/extend-syntax/charts/)
- [Obsidian Charts 文档](https://charts.phibr0.de/Chart%20Types/)
- [Reveal.js Charts 文档](https://github.com/rajgoel/reveal.js-plugins/tree/master/chart#usage)

# AS-Charts support

> [!note] slides extended
> obsidian-slides-extended 文档中品牌已改为 "Slides Extended"，功能与语法完全一致。

Advanced Slides 支持两种图表语法：

## Obsidian Charts 语法

````md
```chart
type: bar
labels: [Monday,Tuesday,Wednesday,Thursday,Friday, Saturday, Sunday]
series:
  - title: Title 1
    data: [1,2,3,4,5,6,7]
  - title: Title 2
    data: [5,4,3,2,1,0,-1]
```
````

目前**不支持**的功能：
- Dataview Integration
- Chart from Table

## Reveal.js Charts 语法

```md
<canvas data-chart="line">
<!--
{
 "data": {
  "labels": ["January"," February"," March"," April"," May"," June"," July"],
  "datasets":[
   {
    "data":[65,59,80,81,56,55,40],
    "label":"My first dataset",
    "backgroundColor":"rgba(20,220,220,.8)"
   },
   {
    "data":[28,48,40,19,86,27,90],
    "label":"My second dataset",
    "backgroundColor":"rgba(220,120,120,.8)"
   }
  ]
 }
}
-->
</canvas>
```
