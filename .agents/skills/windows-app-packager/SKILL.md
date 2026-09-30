---
name: windows-app-packager
description: >-
  Use this skill when developing Windows applications, writing Windows batch (.bat) files,
  packaging Python applications into standalone EXE files with PyInstaller, generating desktop shortcuts,
  handling Windows console encoding (GBK/UTF-8), or serving local static assets with non-ASCII filenames.
---

# Windows 桌面应用打包与批处理开发安全规范 (windows-app-packager)

本技能总结了在 Windows 平台下进行应用打包、批处理启动器开发、字符编码处理及静态资源路由时的**四大高频陷阱与黄金解决范式**，旨在从根本上杜绝“乱码报错”、“找不到外部命令”、“控制台崩溃”及“图片 404”等问题。

---

## 核心避坑铁律 (Golden Rules)

### 1. 批处理 (.bat) 纯 ASCII 极简引导法则 (杜绝乱码崩溃)
* **根因**：Windows 中文版 `cmd.exe` 默认代码页为 CP936 (GBK)。若 `.bat` 以 UTF-8 保存，中文字符的多字节序列极易被 CMD 拆分为 `&` (0x26)、`|` (0x7C) 等控制符，导致 CMD 将中文碎片误当成外部命令执行（如 `'鏉?EXE' 不是内部或外部命令`）。
* **铁律**：**严禁在 `.bat` 文件中硬编码中文字符、特殊符号（如 `&`）或复杂业务逻辑**！
* **标准范式**：`.bat` 文件仅充当轻量级 Bootstrapper（纯 ASCII），将逻辑委托给 Python 或 PowerShell：
  ```bat
  @echo off
  cd /d "%~dp0"
  python build_exe.py
  if %errorlevel% neq 0 (
      echo.
      echo Build failed with error code %errorlevel%.
  )
  pause
  ```

### 2. Python Windows 控制台编码重配置 (防 UnicodeEncodeError)
* **根因**：在 Windows GBK 控制台下直接 `print()` 包含未收录字符或 emoji（如 `✅`、`❌`）时，会抛出 `UnicodeEncodeError: 'gbk' codec can't encode character` 导致程序异常终止。
* **铁律**：任何面向终端的 Python CLI 或打包脚本，必须在入口处重配置输出流，并优先采用安全标记（如 `[OK]`、`[ERROR]`、`[INFO]`）：
  ```python
  import sys
  if sys.platform == "win32":
      try:
          sys.stdout.reconfigure(encoding="utf-8", errors="replace")
          sys.stderr.reconfigure(encoding="utf-8", errors="replace")
      except Exception:
          pass
  ```

### 3. Web 服务静态资源中文 URL 反转义 (防 404 图片丢失)
* **根因**：前端浏览器请求包含中文的静态资源（如 `/images/avatars/绯雪.png`）时，会自动进行 URL 编码（变成 `/images/avatars/%E7%BB%AF%E9%9B%AA.png`）。若后端未解码直接与磁盘路径拼接，文件系统因查找字面量 `%E7...` 而返回 404。
* **铁律**：处理静态资源文件路由时，必须在读取本地磁盘前执行 `urllib.parse.unquote()`，并在前端为核心资源（如立绘）提供回退机制（Fallback）：
  ```python
  import os
  import urllib.parse

  decoded_path = urllib.parse.unquote(path)
  rel_path = decoded_path.lstrip("/")
  file_path = os.path.join(STATIC_DIR, rel_path)
  ```

### 4. PyInstaller 单文件绿色 EXE 桌面化最佳实践
* **防静默崩溃**：在 `--noconsole` 模式下，`sys.stdout` 和 `sys.stderr` 为 `None`，调用 `print()` 会引发静默闪退。必须在应用入口重定向：
  ```python
  if sys.stdout is None:
      sys.stdout = open(os.devnull, "w", encoding="utf-8")
  if sys.stderr is None:
      sys.stderr = open(os.devnull, "w", encoding="utf-8")
  ```
* **资源路径动态定位**：兼容源码运行与 PyInstaller 解包运行（`_MEIPASS`）：
  ```python
  if getattr(sys, "frozen", False):
      APP_DIR = os.path.dirname(sys.executable)
      RESOURCE_DIR = getattr(sys, "_MEIPASS", APP_DIR)
  else:
      APP_DIR = os.path.dirname(os.path.abspath(__file__))
      RESOURCE_DIR = APP_DIR
  ```
* **跨平台参数语法**：`--add-data` 在 Windows 下必须使用**分号 `;`** 分隔源路径与目标路径（Linux/macOS 为 `:`）：
  `--add-data="static;static"`
* **多阶图标生成**：应用图标 `.ico` 必须包含 16x16, 32x32, 48x48, 64x64, 128x128, 256x256 多尺寸，保证桌面、任务栏及高分屏下均清晰无锯齿。

### 5. Windows Sockets TIME_WAIT 与本地端口安全探测 (防冷启动 ERR_CONNECTION_REFUSED)
* **根因**：
  - 进程重启或快速关开时，Windows 内核网络栈会将本地 TCP 端口置于 `TIME_WAIT` 状态（持续 30~60 秒）。
  - 若使用 `connect_ex` 探测端口，由于无进程监听，会返回非零从而误判为“端口空闲”。
  - 随后若在 Windows 下使用 `SO_REUSEADDR` 强行绑定该端口，**Windows 内核将丢弃所有进入的新 TCP 连接并回复 TCP RST，前端浏览器直接崩溃报 ERR_CONNECTION_REFUSED（无法访问此页面）**；关掉等 30 秒后再打开才恢复。
* **铁律**：
  1. **必须使用真实物理 bind 探测**（严禁仅用 `connect_ex`）：
     ```python
     def find_available_port(start_port=8765, max_attempts=20):
         for port in range(start_port, start_port + max_attempts):
             s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
             try:
                 s.bind(('127.0.0.1', port))
                 s.close()
                 return port
             except OSError:
                 try:
                     s.close()
                 except Exception:
                     pass
                 continue
         return start_port
     ```
  2. **在 Windows 下显式禁用 SO_REUSEADDR**：
     `ServerClass.allow_reuse_address = False`，绝不强行借用脏端口。

### 6. Chromium / Edge 独立视窗生命周期与多进程托管 (防早退误杀服务器)
* **根因**：
  - Windows 11 下 Edge 是多进程应用。执行 `msedge.exe --app=...` 时，若后台已有 Edge 驻留，启动器进程会在 1 秒内将 URL 委托给主进程并退出（返回 0）。
  - 若 Python 仅通过 `proc.wait()` 监听启动器，会误以为“用户已关闭窗口”，在 `finally` 块中提前关闭 HTTP 服务，导致眼前刚打开的 Edge 窗口断网报错。
* **铁律**：
  1. **Win32 HWND 真实视窗看门狗**：若启动器退出耗时 `< 3s`，不得直接关机，转入 Win32 原生窗口句柄（HWND）巡检，通过 `user32.IsWindow()` 监听主窗口。只要用户的真实视窗还在，本地 HTTP 服务就持续坚守，窗口关闭后才优雅退出。
  2. **启动前清空会话恢复历史**：Edge 在 `--user-data-dir` 下会将崩溃或报错页缓存在 `Sessions` 目录。启动前必须删除 `profile_dir/Default/Sessions`，并追加启动参数 `--disable-features=msEdgeContinueWhereYouLeftOff` 与 `--disable-session-crashed-bubble`，杜绝还原错误页。

### 7. 桌面端 Web 前端导航栏与按钮绝对防折行铁律 (防 UI 挤压变形)
* **根因**：
  - Flex 容器在无强制换行限制下，遇宽度受限（如窗口收窄、高 DPI 缩放 125%/150%、动态状态标签插入）时，中文无空格会被自动从任意汉字处切断折行（如“手 动 链 / 接”）。
* **铁律**：
  1. **全局强制单行与绝对不折行**：
     ```css
     button, button *, .badge, select, option, .nowrap-btn {
       white-space: nowrap !important;
       word-break: keep-all !important;
     }
     button, select, .badge, .nowrap-btn {
       flex-shrink: 0 !important;
     }
     ```
  2. **外层容器横向滚动兜底**：导航条容器配置 `overflow-x-auto thin-scroll`，宽度极端不足时采用平滑横向滚动条，杜绝按钮被挤扁或换行。

---

## 标准工程模板

本技能随附以下可直接复用的工业级模板：
- [templates/bootstrap.bat](./templates/bootstrap.bat)：纯 ASCII 极简引导批处理
- [templates/build_exe.py](./templates/build_exe.py)：跨平台健壮打包构建器（自带旧进程清理与会话缓存净化）
- [templates/create_shortcut.py](./templates/create_shortcut.py)：Windows 桌面快捷方式自动化创建工具

