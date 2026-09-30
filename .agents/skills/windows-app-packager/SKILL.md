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

---

## 标准工程模板

本技能随附以下可直接复用的工业级模板：
- [templates/bootstrap.bat](./templates/bootstrap.bat)：纯 ASCII 极简引导批处理
- [templates/build_exe.py](./templates/build_exe.py)：跨平台健壮打包构建器
- [templates/create_shortcut.py](./templates/create_shortcut.py)：Windows 桌面快捷方式自动化创建工具
