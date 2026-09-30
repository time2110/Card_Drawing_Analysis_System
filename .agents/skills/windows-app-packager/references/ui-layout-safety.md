# 桌面端 Web 前端排版防折行铁律

## 核心痛点与根因
* **Flex 弹性收缩与断行**：Flex 容器在无强制换行限制下，遇宽度受限（如窗口收窄、高 DPI 缩放 125%/150%、动态状态标签插入）时，中文无空格会被自动从任意汉字处切断折行（如“手 动 链 / 接”）。

## 黄金解决方案
1. **全局强制单行与绝对不折行**：
   ```css
   /* 强制所有按钮及其内部所有子元素禁止断行折行 */
   button, button *, .badge, select, option, .nowrap-btn {
     white-space: nowrap !important;
     word-break: keep-all !important;
   }
   button, select, .badge, .nowrap-btn {
     flex-shrink: 0 !important;
   }
   ```
2. **外层容器横向滚动兜底**：
   导航条容器配置 `overflow-x-auto thin-scroll`，宽度极端不足时采用平滑横向滚动条，杜绝按钮被挤扁或换行。
3. **精简动态状态文本**：
   启动时动态插入的状态胶囊文字应简洁（如“🔄 自动同步中...”而非长篇大论），避免突发剧烈膨胀挤压右侧按钮群。
