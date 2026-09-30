# -*- coding: utf-8 -*-
"""在 Windows 桌面上一键创建【抽卡分析系统】快捷方式"""
import os
import sys
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    tracker_dir = os.path.dirname(os.path.abspath(__file__))
    dist_exe = os.path.join(tracker_dir, "dist", "抽卡分析系统.exe")
    if os.path.exists(dist_exe):
        target_path = dist_exe
    else:
        target_path = os.path.join(tracker_dir, "启动抽卡分析(无黑框桌面版).vbs")

    ico_path = os.path.join(tracker_dir, "app.ico")
    target_lnk = os.path.join(desktop, "抽卡分析系统.lnk")

    tmp_vbs = os.path.join(tracker_dir, "_tmp_make_lnk.vbs")
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oLink = WshShell.CreateShortcut(strDesktop & "\\抽卡分析系统.lnk")
oLink.TargetPath = "{target_path}"
oLink.WorkingDirectory = "{tracker_dir}"
oLink.IconLocation = "{ico_path},0"
oLink.Description = "鸣潮 & 原神 抽卡分析系统"
oLink.Save
'''
    try:
        with open(tmp_vbs, "w", encoding="ansi") as f:
            f.write(vbs_content)
        subprocess.run(["cscript", "//nologo", tmp_vbs], check=True)
        if os.path.exists(tmp_vbs):
            os.remove(tmp_vbs)
        print("=" * 60)
        print(f"   [OK] 桌面快捷方式创建成功！")
        print(f"   路径: {target_lnk}")
        print("   你可以直接在桌面上双击【抽卡分析系统】图标启动客户端！")
        print("=" * 60)
    except Exception as e:
        print(f"创建桌面快捷方式失败: {e}")
        if os.path.exists(tmp_vbs):
            os.remove(tmp_vbs)

if __name__ == "__main__":
    main()
