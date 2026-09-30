# -*- coding: utf-8 -*-
"""
通用的 PyInstaller 单文件绿色桌面应用打包引导器模板
自动检测依赖、重配置输出编码、执行跨平台无黑框打包并生成桌面快捷方式
"""

import os
import sys
import subprocess
import shutil

# 保证 Windows 控制台 UTF-8 输出防乱码与防崩溃
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def build_app(app_name="桌面客户端", entry_script="desktop.py", icon_file="app.ico", static_folder="static"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    print("=" * 60)
    print(f"   [构建器] 开始打包单文件绿色版 EXE: {app_name}")
    print("=" * 60)

    # 0. 优雅终结旧运行进程与清理历史崩溃会话
    try:
        subprocess.run(["taskkill", "/F", "/IM", f"{app_name}.exe", "/T"], capture_output=True)
    except Exception:
        pass
    try:
        import shutil
        sessions_dir = os.path.join(base_dir, "dist", "data", "desktop_profile", "Default", "Sessions")
        if os.path.exists(sessions_dir):
            shutil.rmtree(sessions_dir, ignore_errors=True)
    except Exception:
        pass

    # 1. 检查 PyInstaller
    print("\n[1/3] 检查打包依赖 (PyInstaller)...")
    try:
        import PyInstaller
        print(f"      PyInstaller 就绪 (版本: {PyInstaller.__version__})")
    except ImportError:
        print("      自动安装 PyInstaller...")
        ret = subprocess.call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        if ret != 0:
            print("[ERROR] PyInstaller 安装失败，请检查网络连接")
            return False

    # 2. 准备图标
    ico_path = os.path.join(base_dir, icon_file) if icon_file else None
    icon_arg = [f"--icon={ico_path}"] if (ico_path and os.path.exists(ico_path)) else []

    # 3. 组装参数
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        f"--name={app_name}",
        "--clean"
    ] + icon_arg

    if static_folder and os.path.exists(os.path.join(base_dir, static_folder)):
        # Windows 下使用分号分隔
        cmd.append(f"--add-data={static_folder};{static_folder}")

    cmd.append(entry_script)

    print("\n[2/3] 执行 PyInstaller 编译...")
    ret = subprocess.call(cmd)
    if ret != 0:
        print("\n[ERROR] 构建失败，请查看上方编译日志")
        return False

    out_exe = os.path.join(base_dir, "dist", f"{app_name}.exe")
    if os.path.exists(out_exe):
        size_mb = round(os.path.getsize(out_exe) / (1024 * 1024), 2)
        print("\n" + "=" * 60)
        print(f"   [OK] 单文件绿色版打包成功！")
        print(f"   生成路径: {out_exe}")
        print(f"   文件体积: {size_mb} MB")
        print("=" * 60)
        return True
    else:
        print("\n[ERROR] 未在 dist 目录中找到生成文件")
        return False

if __name__ == "__main__":
    build_app()
