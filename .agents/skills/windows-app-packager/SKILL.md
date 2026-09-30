---
name: windows-app-packager
description: >-
  Use this skill when developing Windows applications, writing Windows batch (.bat) files,
  packaging Python applications into standalone EXE files with PyInstaller, generating desktop shortcuts,
  handling Windows console encoding (GBK/UTF-8), fixing ERR_CONNECTION_REFUSED socket issues,
  managing Chromium/Edge window lifecycles, or serving local static assets with non-ASCII filenames.
---

# Windows 桌面应用开发与打包决策路由字典 (windows-app-packager)

本技能采用**模块化条件字典索引**架构。遇到对应故障场景时，直接查阅对应的专题分卷，避免无谓的上下文消耗。

---

## 故障与场景路由字典 (Diagnostic Routing Matrix)

| 触发场景 / 报错特征 (Condition) | 根因要点 (Key Cause) | 专项目标分卷 (Reference) |
| :--- | :--- | :--- |
| **冷启动报 `ERR_CONNECTION_REFUSED`**<br>（关掉等一会儿再开才恢复） | Windows 端口处于 `TIME_WAIT`；`connect_ex` 假阳性；`SO_REUSEADDR` 引发内核 TCP RST | 📘 [sockets-and-ports.md](./references/sockets-and-ports.md) |
| **应用视窗一闪而过 / 本地服务秒退**<br>（多进程启动器异常） | Edge 多进程委托导致启动器 `< 3s` 早退；服务端依凭 `proc.wait()` 误判自杀 | 📘 [chromium-lifecycle.md](./references/chromium-lifecycle.md) |
| **按钮或徽章内文字被挤压断行**<br>（如“手 动 链 / 接”） | Flex 容器默认收缩；无空格中文被切断折行；动态状态标签膨胀挤压 | 📘 [ui-layout-safety.md](./references/ui-layout-safety.md) |
| **批处理报错 `'XXX' 不是内部或外部命令`** | UTF-8 编码的 `.bat` 含中文导致 CMD (GBK) 将字节碎片解析为控制符断裂 | 📘 [batch-and-encoding.md](./references/batch-and-encoding.md) |
| **中文或空格文件名图片显示 404** | 浏览器自动 URL 转义（如 `%E7...`），后端未解码直拼磁盘路径 | 📘 [static-assets-unquote.md](./references/static-assets-unquote.md) |
| **打包单文件 Exe 运行时静默闪退** | `--noconsole` 下 `sys.stdout` 为 `None`；未动态兼容 `_MEIPASS` 资源目录 | 📘 [pyinstaller-best-practices.md](./references/pyinstaller-best-practices.md) |

---

## 工业级标准工程模板 (Templates)

- [templates/bootstrap.bat](./templates/bootstrap.bat)：纯 ASCII 极简引导批处理（零乱码崩溃）
- [templates/build_exe.py](./templates/build_exe.py)：单文件 EXE 健壮构建器（自动清理旧进程与 Sessions 缓存）
- [templates/create_shortcut.py](./templates/create_shortcut.py)：Windows 桌面快捷方式自动化生成脚本
