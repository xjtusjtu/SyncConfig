导入另一个 CSS 文件，根据你使用的场景，主要有 **3 种写法**：

### 1. 在 HTML 中导入（最常用、最推荐）
在 HTML 文件的 `<head>` 中使用 `<link>` 标签。这是浏览器加载外部 CSS 的标准方式，**加载速度最快**（并行加载）。

```html
<head>
  <!-- 导入同级的 style.css 文件 -->
  <link rel="stylesheet" href="style.css">
  
  <!-- 导入子文件夹内的文件 -->
  <link rel="stylesheet" href="css/common.css">
  
  <!-- 导入网络上的 CDN 文件 -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap/dist/css/bootstrap.min.css">
</head>
```

---

### 2. 在 CSS 文件中导入（使用 @import）
在 CSS 文件的**最顶部**（必须是第一行），使用 `@import` 规则引入另一个 CSS 文件。

```css
/* main.css 文件中的第一行代码 */

/* 导入同级的 base.css */
@import url("base.css");

/* 或使用不带 url() 的写法 */
@import "reset.css";

/* 导入网络文件 */
@import "https://fonts.googleapis.com/css?family=Roboto";

body {
  background: #fff;
}
```
> **⚠️ 注意**：`@import` 会阻塞当前 CSS 的下载，导致页面渲染变慢。除非是配合构建工具（如 Vite/Webpack）或在 JS 中动态使用，否则**在纯前端项目中，优先推荐使用第 1 种 `<link>` 方式**。

---

### 3. 在 JavaScript（JS）中动态导入
如果你在使用前端框架或原生 JS，可以通过 JS 动态加载 CSS。

```javascript
// 在 JS 文件中动态导入
import "style.css"; // 适用于 Vite/Webpack 等构建工具

// 或者纯原生 JS 动态创建 link 标签
const link = document.createElement('link');
link.rel = 'stylesheet';
link.href = 'style.css';
document.head.appendChild(link);
```

---
