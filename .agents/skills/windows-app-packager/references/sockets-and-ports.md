# Windows Sockets TIME_WAIT 与本地端口安全绑定

## 核心痛点与根因
* **TIME_WAIT 假阳性**：旧进程退出后，Windows 网络栈将端口保持在 `TIME_WAIT`（持续 30~60 秒）。
* **connect_ex 误判**：若仅用 `connect_ex` 探测，由于无进程监听，会返回非零从而误判为“端口空闲”。
* **SO_REUSEADDR 致命重置**：若随后在 Windows 下开启 `SO_REUSEADDR` 强行绑定该端口，**Windows 内核将丢弃所有进入的新 TCP 连接并直接回复 TCP RST，前端浏览器直接崩溃报 ERR_CONNECTION_REFUSED（无法访问此页面）**；关掉等 30 秒后再打开才恢复。

## 黄金解决方案
1. **物理真实 bind 探测（严禁仅用 `connect_ex`）**：
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
2. **Windows 下显式禁用 SO_REUSEADDR**：
   ```python
   ServerClass.allow_reuse_address = False
   ```
   绝不强行借用处于 TIME_WAIT 的脏端口，遇到冲突立即顺延至干净端口（如 8766）。
