# 批处理纯 ASCII 与控制台编码安全

## 核心痛点与根因
* **CMD GBK 语法截断**：Windows 中文版 `cmd.exe` 默认代码页为 CP936 (GBK)。若 `.bat` 以 UTF-8 保存，中文字符的多字节序列极易被 CMD 拆分为 `&` (0x26)、`|` (0x7C) 等控制符，导致 CMD 将中文碎片误当成外部命令执行（如 `'鏉?EXE' 不是内部或外部命令`）。
* **控制台 UnicodeEncodeError**：在 Windows GBK 控制台下直接 `print()` 包含未收录字符或 emoji（如 `✅`、`❌`）时，会抛出 `UnicodeEncodeError: 'gbk' codec can't encode character` 导致程序异常终止。

## 黄金解决方案
1. **批处理 (.bat) 纯 ASCII 极简引导法则**：
   * 严禁在 `.bat` 中编写中文字符、特殊符号（如 `&`）或复杂业务逻辑。
   * `.bat` 仅充当轻量级 Bootstrapper，将逻辑委托给 Python 或 PowerShell：
     ```bat
     @echo off
     cd /d "%~dp0"
     python build_exe.py
     if %errorlevel% neq 0 pause
     ```
2. **Python 入口编码安全重配置**：
   ```python
   import sys
   if sys.platform == "win32":
       try:
           sys.stdout.reconfigure(encoding="utf-8", errors="replace")
           sys.stderr.reconfigure(encoding="utf-8", errors="replace")
       except Exception:
           pass
   ```
   控制台输出日志统一使用 `[OK]`、`[ERROR]`、`[INFO]`，杜绝特殊 Emoji。
