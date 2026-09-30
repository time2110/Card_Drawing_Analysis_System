# Chromium / Edge 独立视窗生命周期与多进程托管

## 核心痛点与根因
* **启动器秒退误杀服务**：Windows 11 下 Edge 是多进程应用。执行 `msedge.exe --app=...` 时，若后台已有 Edge 驻留，启动器进程会在 1 秒内将 URL 委托给主进程并退出（返回 0）。
* **盲目 shutdown**：若 Python 服务端依凭 `proc.wait()` 退出就误判为用户关闭了视窗而调用 `httpd.shutdown()`，会直接在用户眼前把正在加载的本地服务器杀掉。
* **会话恢复污染**：Edge 在 `--user-data-dir` 下会将崩溃或报错页缓存在 `Sessions` 目录。启动时会自动还原上一次报错的旧标签页。

## 黄金解决方案
1. **Win32 HWND 真实视窗看门狗**：
   若启动器退出耗时 `< 3s`，不得直接关机，转入 Win32 原生窗口句柄（HWND）巡检：
   ```python
   # 监听带有特征标题的主窗口句柄
   while True:
       time.sleep(0.8)
       alive = False
       for h in list(MAIN_WINDOW_HWNDS):
           if user32.IsWindow(h) and user32.IsWindowVisible(h):
               alive = True
               break
       if not alive:
           break  # 只有当真实窗口真正被叉掉时才退出
   ```
2. **启动前清空会话恢复历史**：
   删除 `profile_dir/Default/Sessions`，并追加启动参数：
   ```python
   args = [
       browser_exe,
       f"--app={url}",
       f"--user-data-dir={profile_dir}",
       "--disable-features=Translate,OptimizationHints,msEdgeContinueWhereYouLeftOff",
       "--disable-session-crashed-bubble",
       "--hide-crash-restore-bubble",
       "--no-first-run",
       "--no-default-browser-check"
   ]
   ```
