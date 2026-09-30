# -*- coding: utf-8 -*-
"""
一键打包单文件绿色 EXE 桌面版构建脚本
自动检测 PyInstaller 依赖，调用标准参数构建单文件无黑框 EXE，并刷新桌面快捷方式
"""

import os
import sys
import subprocess
import shutil

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def run_build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    print("=" * 60)
    print("   鸣潮 & 原神 抽卡分析系统 - 单文件绿色版 EXE 打包工具")
    print("=" * 60)

    # 0. 清理正在运行的旧进程与残留的崩溃会话缓存
    try:
        subprocess.run(["taskkill", "/F", "/IM", "抽卡分析系统.exe", "/T"], capture_output=True)
    except Exception:
        pass
    try:
        sessions_dir = os.path.join(base_dir, "dist", "data", "desktop_profile", "Default", "Sessions")
        if os.path.exists(sessions_dir):
            shutil.rmtree(sessions_dir, ignore_errors=True)
    except Exception:
        pass

    # 1. 检测 PyInstaller
    print("\n[1/3] 正在检查打包工具 (PyInstaller)...")
    try:
        import PyInstaller
        print(f"      PyInstaller 已安装 (版本: {PyInstaller.__version__})")
    except ImportError:
        print("      未检测到 PyInstaller，正在自动安装...")
        ret = subprocess.call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        if ret != 0:
            print("      [ERROR] PyInstaller 安装失败，请检查网络连接或手动运行 pip install pyinstaller")
            return False

    # 2. 准备图标
    ico_path = os.path.join(base_dir, "app.ico")
    if not os.path.exists(ico_path):
        print("      [WARN] 未找到 app.ico 图标文件，将尝试从 static/favicon.ico 复制...")
        fav = os.path.join(base_dir, "static", "favicon.ico")
        if os.path.exists(fav):
            shutil.copyfile(fav, ico_path)

    # 3. 执行 PyInstaller 打包
    print("\n[2/3] 正在构建单文件 Exe (应用图标: 绯雪，独立沉浸式视窗模式)...")
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        f"--icon={ico_path}",
        "--name=抽卡分析系统",
        "--add-data=static;static",
        "--add-data=app.ico;.",
        "--clean",
        "desktop.py"
    ]
    print(f"      执行命令: {' '.join(cmd)}")
    ret = subprocess.call(cmd)

    if ret != 0:
        print("\n[ERROR] 打包过程中出现错误，请检查上方日志。")
        return False

    target_exe = os.path.join(base_dir, "dist", "抽卡分析系统.exe")
    if os.path.exists(target_exe):
        size_mb = round(os.path.getsize(target_exe) / (1024 * 1024), 2)
        print("\n" + "=" * 60)
        print("   [OK] 单文件绿色版 EXE 打包成功！")
        print(f"   生成路径: {target_exe}")
        print(f"   文件大小: {size_mb} MB")
        print("   特色: 零黑框终端、原生内嵌绯雪立体图标、开箱即用")
        print("=" * 60)

        # 4. 自动刷新桌面快捷方式
        print("\n[3/3] 正在更新桌面快捷方式...")
        shortcut_script = os.path.join(base_dir, "create_desktop_shortcut.py")
        if os.path.exists(shortcut_script):
            try:
                subprocess.call([sys.executable, shortcut_script])
            except Exception as e:
                print(f"      创建快捷方式提示: {e}")

        return True
    else:
        print("\n[ERROR] 未在 dist 目录找到生成的 EXE 文件！")
        return False

if __name__ == "__main__":
    success = run_build()
    if not success:
        sys.exit(1)
