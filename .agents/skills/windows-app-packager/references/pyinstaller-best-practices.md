# PyInstaller 单文件绿色 EXE 最佳实践

## 核心痛点与根因
* `--noconsole` 模式下 `sys.stdout` 和 `sys.stderr` 为 `None`，调用 `print()` 会静默闪退。
* 打包后解压目录与源码目录不一致，导致静态资源找不到。
* 打包前若有旧程序进程运行，会导致覆盖失败。

## 黄金解决方案
1. **输入输出流安全重定向**：
   ```python
   if sys.stdout is None:
       sys.stdout = open(os.devnull, "w", encoding="utf-8")
   if sys.stderr is None:
       sys.stderr = open(os.devnull, "w", encoding="utf-8")
   ```
2. **动态资源路径定位 (`_MEIPASS`)**：
   ```python
   if getattr(sys, "frozen", False):
       APP_DIR = os.path.dirname(sys.executable)
       RESOURCE_DIR = getattr(sys, "_MEIPASS", APP_DIR)
   else:
       APP_DIR = os.path.dirname(os.path.abspath(__file__))
       RESOURCE_DIR = APP_DIR
   ```
3. **打包构建器内置自愈与清理**：
   打包前自动执行 `taskkill` 杀掉旧实例，并清空 `desktop_profile/Default/Sessions` 会话缓存。
4. **Windows 分号路径语法**：
   `--add-data="static;static"`（Windows 严格使用分号 `;` 分隔）。
