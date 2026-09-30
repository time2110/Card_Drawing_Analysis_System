# -*- coding: utf-8 -*-
"""
鸣潮 & 原神 抽卡分析系统 - 桌面原生客户端启动入口
纯标准库零额外依赖，通过 Windows 现代化 WebView / Edge App 独立视窗运行
支持完全隐藏 CMD 命令行黑框、沉浸式无边框界面、HTTP 稳定就绪探活与生命周期自动管控
"""

import os
import sys
import time
import socket
import subprocess
import threading
import json
import urllib.request

# 环境与日志重定向
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = getattr(sys, "_MEIPASS", APP_DIR)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = APP_DIR

BASE_DIR = APP_DIR
LOG_FILE = os.path.join(BASE_DIR, "data", "desktop.log")
try:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    _log_f = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
    sys.stdout = _log_f
    sys.stderr = _log_f
except Exception:
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [PID={os.getpid()}] {msg}", flush=True)
sys.path.insert(0, RESOURCE_DIR)
sys.path.insert(0, APP_DIR)

from app import ServerClass, GachaRequestHandler, find_available_port, run_auto_sync_all

def find_chromium_browser():
    """查找系统中可用的 Chromium 内核浏览器 (优先 Windows 预装的 Edge)"""
    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def check_existing_service(port=8765):
    """检查是否已有抽卡分析后台服务常驻运行 (直连本地回环，绕过系统代理)"""
    try:
        proxy_handler = urllib.request.ProxyHandler({})
        opener = urllib.request.build_opener(proxy_handler)
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/ping", headers={"User-Agent": "Ping"})
        with opener.open(req, timeout=0.5) as resp:
            if resp.status == 200:
                return True
    except Exception:
        pass
    return False

def wait_http_ready(url, max_wait=10.0):
    """
    通过轻量级 /api/ping 接口探活 (毫秒级响应，零 IO 阻塞)，
    显式绕过任何代理直连 127.0.0.1，直到 HTTP 服务彻底准备就绪
    """
    start_t = time.time()
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler)
    while time.time() - start_t < max_wait:
        try:
            req = urllib.request.Request(f"{url}/api/ping", headers={"User-Agent": "ReadyChecker"})
            with opener.open(req, timeout=1.5) as resp:
                if resp.status == 200:
                    time.sleep(0.15)  # 给操作系统网络栈留出微小缓冲
                    return True
        except Exception:
            time.sleep(0.1)
    return False

MAIN_WINDOW_HWNDS = set()

def apply_window_icon_thread(ico_path):
    """
    在独立线程中监视并为 Edge / Chromium 独立视窗强行绑定原生 HICON 图标
    覆盖 WM_SETICON (BIG/SMALL) 以及窗口类 ClassLongPtr，彻底杜绝任务栏显示 Edge 默认蓝标
    """
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    IMAGE_ICON = 1
    LR_LOADFROMFILE = 0x00000010
    LR_DEFAULTSIZE = 0x00000040
    WM_SETICON = 0x0080
    ICON_SMALL = 0
    ICON_BIG = 1
    GCL_HICON = -14
    GCL_HICONSM = -34

    SetClassLongPtrW = getattr(user32, 'SetClassLongPtrW', None)
    if not SetClassLongPtrW:
        SetClassLongPtrW = user32.SetClassLongW

    if not os.path.exists(ico_path):
        return

    try:
        h_big = user32.LoadImageW(None, ico_path, IMAGE_ICON, 256, 256, LR_LOADFROMFILE)
        if not h_big:
            h_big = user32.LoadImageW(None, ico_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
        h_small = user32.LoadImageW(None, ico_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
        if not h_small:
            h_small = h_big
    except Exception:
        return

    def _worker():
        applied_hwnds = set()
        start_t = time.time()
        while time.time() - start_t < 12.0:
            time.sleep(0.3)
            def enum_proc(hwnd, lparam):
                if not user32.IsWindowVisible(hwnd):
                    return True
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    
                    class_buff = ctypes.create_unicode_buffer(256)
                    user32.GetClassNameW(hwnd, class_buff, 256)
                    class_name = class_buff.value
                    
                    if "Chrome_WidgetWin" in class_name and any(k in title for k in ("鸣潮", "抽卡", "原神", "Gacha", "127.0.0.1")):
                        MAIN_WINDOW_HWNDS.add(hwnd)
                        if hwnd not in applied_hwnds:
                            try:
                                user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_big)
                                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_small)
                                SetClassLongPtrW(hwnd, GCL_HICON, h_big)
                                SetClassLongPtrW(hwnd, GCL_HICONSM, h_small)
                                user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0020)
                                applied_hwnds.add(hwnd)
                            except Exception:
                                pass
                return True

            enum_fn = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(enum_proc)
            try:
                user32.EnumWindows(enum_fn, 0)
            except Exception:
                pass
            if applied_hwnds and time.time() - start_t > 4.0:
                break

    threading.Thread(target=_worker, daemon=True).start()

def open_window_and_wait(url, browser_exe):
    """以独立视窗模式调起 Edge / Chrome，并阻塞等待用户关闭窗口"""
    profile_dir = os.path.join(BASE_DIR, "data", "desktop_profile")
    os.makedirs(profile_dir, exist_ok=True)
    
    # 动态探测应用图标路径
    ico_path = os.path.join(RESOURCE_DIR, "app.ico")
    if not os.path.exists(ico_path):
        ico_path = os.path.join(BASE_DIR, "app.ico")
    if not os.path.exists(ico_path):
        ico_path = os.path.join(RESOURCE_DIR, "static", "favicon.ico")

    # 启动原生 Win32 图标守护线程强行绑定
    if os.path.exists(ico_path):
        apply_window_icon_thread(ico_path)

    # 清除历史崩溃状态与会话恢复标记，彻底杜绝 Chromium 还原上一次的无法连接错误页
    try:
        import shutil
        sessions_dir = os.path.join(profile_dir, "Default", "Sessions")
        if os.path.exists(sessions_dir):
            shutil.rmtree(sessions_dir, ignore_errors=True)
            log("Cleared historical Edge Sessions directory")
    except Exception as e:
        log(f"Failed to clear sessions: {e}")

    try:
        pref_file = os.path.join(profile_dir, "Default", "Preferences")
        if os.path.exists(pref_file):
            with open(pref_file, "r", encoding="utf-8", errors="ignore") as f:
                pref_content = f.read()
            if '"exit_type":"Crashed"' in pref_content or '"exit_type": "Crashed"' in pref_content:
                pref_content = pref_content.replace('"exit_type":"Crashed"', '"exit_type":"Normal"').replace('"exit_type": "Crashed"', '"exit_type": "Normal"')
                with open(pref_file, "w", encoding="utf-8") as f:
                    f.write(pref_content)
    except Exception:
        pass

    effective_url = url if url.endswith("/") else (url + "/")
    args = [
        browser_exe,
        f"--app={effective_url}",
        "--window-size=1380,880",
        f"--user-data-dir={profile_dir}",
        "--no-proxy-server",
        "--proxy-bypass-list=<-loopback>;127.0.0.1;localhost",
        "--disable-session-crashed-bubble",
        "--hide-crash-restore-bubble",
        "--disable-features=Translate,OptimizationHints,msEdgeContinueWhereYouLeftOff",
        "--disable-extensions",
        "--disable-background-mode",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    log(f"Launching Edge subprocess: {' '.join(args)}")
    proc = subprocess.Popen(args)
    log(f"Edge process spawned with PID={proc.pid}")
    start_edge_t = time.time()
    ret = proc.wait()
    edge_duration = time.time() - start_edge_t
    log(f"Edge process PID={proc.pid} exited with code {ret} after {edge_duration:.2f}s")
    
    # 防御 Edge 启动器进程秒退导致服务器被连带误杀 (Chromium 多进程委托机制)
    if edge_duration < 3.0:
        log("Edge starter process exited (<3s). Monitoring window HWND lifecycle...")
        import ctypes
        user32 = ctypes.windll.user32
        
        # 等待应用主窗口出现并被 HWND 钩子捕获 (最多给 6 秒)
        t_wait = time.time()
        while time.time() - t_wait < 6.0:
            if MAIN_WINDOW_HWNDS:
                break
            time.sleep(0.2)
            
        log(f"Tracked window HWNDs: {list(MAIN_WINDOW_HWNDS)}")
        if MAIN_WINDOW_HWNDS:
            # 持续监视窗口存活状态：只要用户的视窗未被关闭，HTTP 服务就必须持续稳定运行！
            while True:
                time.sleep(0.8)
                alive = False
                for h in list(MAIN_WINDOW_HWNDS):
                    if user32.IsWindow(h) and user32.IsWindowVisible(h):
                        alive = True
                        break
                if not alive:
                    log("All monitored app windows have been closed by user. Exiting.")
                    break
        else:
            log("No HWND captured, keeping alive for safe session fallback...")
            time.sleep(3.0)

def start_delayed_sync():
    """首屏渲染完成后 3 秒再启动后台全量同步，零抢占启动 CPU/IO"""
    def _worker():
        time.sleep(3.0)
        run_auto_sync_all()
    threading.Thread(target=_worker, daemon=True).start()

def main():
    log(f"=== App Desktop Main Starting (sys.argv={sys.argv}, frozen={getattr(sys, 'frozen', False)}) ===")
    # 设置显式 AppUserModelID，使 Windows 任务栏精准识别本应用并脱离默认浏览器归组
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WuwaGenshinTracker.App.1.0")
    except Exception:
        pass

    DEFAULT_PORT = 8765
    browser_exe = find_chromium_browser()
    log(f"Detected browser_exe: {browser_exe}")

    # 单实例互斥量保护，防止用户连续快速双击导致两个实例抢占端口
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        mutex = kernel32.CreateMutexW(None, False, "Global\\WuwaGenshinTrackerSingleInstanceMutex")
        if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            time.sleep(1.2)
            url = f"http://127.0.0.1:{DEFAULT_PORT}"
            if check_existing_service(DEFAULT_PORT):
                if browser_exe:
                    open_window_and_wait(url, browser_exe)
                else:
                    import webbrowser
                    webbrowser.open(url)
            sys.exit(0)
    except Exception:
        pass

    # 1. 检查若已有后台服务在运行，直接唤起窗口
    if check_existing_service(DEFAULT_PORT):
        url = f"http://127.0.0.1:{DEFAULT_PORT}"
        if browser_exe:
            open_window_and_wait(url, browser_exe)
        else:
            import webbrowser
            webbrowser.open(url)
        sys.exit(0)

    # 2. 寻找可用端口并启动本地 HTTP 服务
    port = find_available_port(DEFAULT_PORT)
    server_address = ("127.0.0.1", port)
    try:
        ServerClass.allow_reuse_address = False
    except Exception:
        pass
    log(f"Starting HTTP server on port {port} (clean socket bind)...")
    httpd = ServerClass(server_address, GachaRequestHandler)
    
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    url = f"http://127.0.0.1:{port}"

    # 3. 稳健的 HTTP 真实就绪探活 (必须收到 200 响应才放行唤起浏览器，彻底杜绝 ERR_CONNECTION_REFUSED)
    ready = wait_http_ready(url, max_wait=10.0)
    if not ready:
        time.sleep(1.0)
        wait_http_ready(url, max_wait=5.0)

    # 4. 首屏就绪后，延时启动静默后台自动同步
    start_delayed_sync()

    # 5. 检查用户是否有可选的 pywebview
    use_pywebview = False
    try:
        import webview
        use_pywebview = True
    except ImportError:
        pass

    if use_pywebview and "--app" not in sys.argv:
        try:
            webview.create_window(
                title="鸣潮 & 原神 抽卡分析系统",
                url=url,
                width=1380,
                height=880,
                min_size=(1024, 700),
                background_color="#0a0d14"
            )
            webview.start()
            httpd.shutdown()
            httpd.server_close()
            sys.exit(0)
        except Exception:
            pass

    # 6. 原生独立桌面 App 视窗 (Edge / Chrome App 独立沉浸式窗口)
    if browser_exe:
        try:
            open_window_and_wait(url, browser_exe)
        finally:
            try:
                httpd.shutdown()
                httpd.server_close()
            except Exception:
                pass
            sys.exit(0)
    else:
        # 兜底：调起系统默认浏览器
        import webbrowser
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            httpd.shutdown()
            httpd.server_close()

if __name__ == "__main__":
    main()
