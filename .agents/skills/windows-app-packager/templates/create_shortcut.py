# -*- coding: utf-8 -*-
"""
通用的 Windows 桌面快捷方式自动化创建工具模板
基于 Windows Script Host (WScript.Shell)，零外部模块依赖
"""

import os
import sys
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def make_shortcut(target_exe_path, shortcut_name="我的应用", icon_path=None, description=""):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    target_lnk = os.path.join(desktop, f"{shortcut_name}.lnk")
    work_dir = os.path.dirname(os.path.abspath(target_exe_path))

    tmp_vbs = os.path.join(work_dir, "_tmp_make_lnk.vbs")
    icon_line = f'oLink.IconLocation = "{icon_path},0"' if (icon_path and os.path.exists(icon_path)) else ""

    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oLink = WshShell.CreateShortcut(strDesktop & "\\{shortcut_name}.lnk")
oLink.TargetPath = "{target_exe_path}"
oLink.WorkingDirectory = "{work_dir}"
{icon_line}
oLink.Description = "{description}"
oLink.Save
'''
    try:
        with open(tmp_vbs, "w", encoding="ansi") as f:
            f.write(vbs_content)
        subprocess.run(["cscript", "//nologo", tmp_vbs], check=True)
        if os.path.exists(tmp_vbs):
            os.remove(tmp_vbs)
        print(f"[OK] 桌面快捷方式已创建: {target_lnk}")
        return True
    except Exception as e:
        print(f"[ERROR] 创建桌面快捷方式失败: {e}")
        if os.path.exists(tmp_vbs):
            os.remove(tmp_vbs)
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        make_shortcut(sys.argv[1])
    else:
        print("用法: python create_shortcut.py <目标程序完整路径> [快捷方式名称]")
