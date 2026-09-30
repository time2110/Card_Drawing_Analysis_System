# 静态资源中文 URL 反转义

## 核心痛点与根因
* 前端浏览器请求包含中文的静态资源（如 `/images/avatars/绯雪.png`）时，会自动进行 URL 编码（变成 `/images/avatars/%E7%BB%AF%E9%9B%AA.png`）。
* 若后端未解码直接与磁盘路径拼接，文件系统因查找字面量 `%E7...` 而返回 404 图片或资源丢失。

## 黄金解决方案
处理静态资源文件路由时，必须在读取本地磁盘前显式调用 `urllib.parse.unquote()`：
```python
import os
import urllib.parse

decoded_path = urllib.parse.unquote(path)
rel_path = decoded_path.lstrip("/")
file_path = os.path.join(STATIC_DIR, rel_path)
```
并在前端为核心资源（如头像、立绘）提供 SVG 或默认头像回退机制（Fallback `onerror`）。
