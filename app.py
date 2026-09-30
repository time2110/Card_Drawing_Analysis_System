# -*- coding: utf-8 -*-
"""
鸣潮抽卡分析应用 - 本地 Web 服务端
纯 Python 标准库构建，零第三方依赖，开箱即用
"""

import os
import sys
import json
import time
import socket
import urllib.parse
import webbrowser
try:
    from http.server import ThreadingHTTPServer as ServerClass
except ImportError:
    from socketserver import ThreadingMixIn
    from http.server import HTTPServer
    class ServerClass(ThreadingMixIn, HTTPServer):
        daemon_threads = True
from http.server import BaseHTTPRequestHandler
import threading
import base64

# 防御 noconsole 打包环境下 stdout/stderr 为 None 导致的静默崩溃
if sys.stdout is None:
    try:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        pass
if sys.stderr is None:
    try:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        pass

# 根目录与资源目录定义 (兼容源码运行与 PyInstaller 单文件打包)
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = getattr(sys, "_MEIPASS", APP_DIR)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = APP_DIR

BASE_DIR = APP_DIR
PARENT_DIR = os.path.dirname(APP_DIR)
sys.path.insert(0, RESOURCE_DIR)
sys.path.insert(0, APP_DIR)

from gacha_core import (
    extract_latest_gacha_url,
    extract_gacha_url_from_bytes,
    parse_gacha_url,
    query_official_records,
    GachaDataManager,
    POOL_NAMES,
    normalize_imported_records
)

from characters_db import (
    get_item_info,
    get_all_config_data,
    save_custom_config,
    load_custom_config,
    CONFIG_PATH as CUSTOM_CONFIG_PATH
)

from genshin_db import (
    GENSHIN_POOL_NAMES,
    GENSHIN_CHARACTERS_5STAR,
    GENSHIN_WEAPONS_5STAR,
    get_genshin_avatar_url,
    get_all_genshin_config_data,
    save_genshin_custom_config
)

from genshin_core import (
    GenshinDataManager,
    get_default_genshin_log_path,
    extract_genshin_gacha_url,
    extract_genshin_url_from_bytes,
    query_genshin_official_records,
    parse_genshin_url_params
)

from datetime import datetime
from webdav_backup import (
    load_webdav_config,
    save_webdav_config,
    sanitize_config_for_frontend,
    test_webdav_connection,
    upload_backup_to_webdav,
    restore_backup_from_webdav,
    build_full_backup_payload,
    restore_from_payload
)

DATA_PATH = os.path.join(APP_DIR, "data", "gacha_records.json")
KNOWN_GAME_LOG = r"C:\software\Wuthering Waves\Wuthering Waves Game\Client\Saved\Logs\Client.log"
LOG_PATH = KNOWN_GAME_LOG if os.path.exists(KNOWN_GAME_LOG) else os.path.join(PARENT_DIR, "Client.log")
STATIC_DIR = os.path.join(RESOURCE_DIR, "static")

# 原神数据与日志路径
GENSHIN_DATA_PATH = os.path.join(BASE_DIR, "data", "genshin_records.json")
GENSHIN_LOG_PATH = get_default_genshin_log_path()

# 初始化数据管理器
db_manager = GachaDataManager(DATA_PATH)
genshin_db_manager = GenshinDataManager(GENSHIN_DATA_PATH)

# ================= 后台自动同步调度器 (鸣潮 & 原神) =================
auto_sync_lock = threading.Lock()
latest_auto_sync_status = {
    "running": False,
    "lastTime": "",
    "wuwa": {"success": False, "added": 0, "message": "尚未执行"},
    "genshin": {"success": False, "added": 0, "message": "尚未执行"}
}

def sync_wuwa_background():
    """静默同步鸣潮"""
    try:
        custom_cfg = load_custom_config()
        effective_log = custom_cfg.get("customLogPath") or LOG_PATH
        url = None
        if os.path.exists(effective_log):
            url, _ = extract_latest_gacha_url(effective_log)
        if not url and custom_cfg.get("customUrl"):
            url = custom_cfg["customUrl"].strip()
        if not url:
            return False, "未在日志中检测到有效抽卡链接", 0
            
        parsed_info, err = parse_gacha_url(url)
        if not parsed_info:
            return False, f"鸣潮抽卡链接解析失败: {err}", 0
            
        player_id = parsed_info["playerId"]
        total_added = 0
        for p_type in range(1, 8):
            records, err = query_official_records(parsed_info, p_type)
            if not err and records:
                added, _ = db_manager.merge_records(player_id, p_type, records)
                total_added += added
            time.sleep(0.15)
        return True, f"鸣潮同步完成，新增 {total_added} 条", total_added
    except Exception as e:
        return False, f"鸣潮同步异常: {e}", 0

def sync_genshin_background():
    """静默同步原神"""
    try:
        url = None
        if os.path.exists(GENSHIN_LOG_PATH):
            url, _ = extract_genshin_gacha_url(GENSHIN_LOG_PATH)
        if not url:
            return False, "未在原神日志中检测到有效祈愿链接", 0
            
        ok, msg, fetched_pools, uid = query_genshin_official_records(url)
        if not ok or not fetched_pools:
            return False, f"原神祈愿接口响应: {msg}", 0
            
        uid = uid or "100000001"
        total_added = 0
        for pt, rlist in fetched_pools.items():
            total_added += genshin_db_manager.merge_records(uid, pt, rlist)
        return True, f"原神同步完成，新增 {total_added} 条", total_added
    except Exception as e:
        return False, f"原神同步异常: {e}", 0

def run_auto_sync_all():
    """执行鸣潮与原神的双端静默后台自动同步"""
    global latest_auto_sync_status
    if not auto_sync_lock.acquire(blocking=False):
        return
    try:
        latest_auto_sync_status["running"] = True
        latest_auto_sync_status["lastTime"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. 鸣潮后台同步
        w_ok, w_msg, w_added = sync_wuwa_background()
        latest_auto_sync_status["wuwa"] = {"success": w_ok, "added": w_added, "message": w_msg}
        
        # 2. 原神后台同步
        g_ok, g_msg, g_added = sync_genshin_background()
        latest_auto_sync_status["genshin"] = {"success": g_ok, "added": g_added, "message": g_msg}

        # 3. 若有新增记录且开启了坚果云自动备份，自动静默同步至云端
        if (w_added > 0 or g_added > 0):
            try:
                wcfg = load_webdav_config()
                if wcfg.get("enabled") and wcfg.get("autoBackupOnSync") and wcfg.get("username") and wcfg.get("password"):
                    upload_backup_to_webdav(wcfg)
            except Exception:
                pass
    finally:
        latest_auto_sync_status["running"] = False
        auto_sync_lock.release()

def find_available_port(start_port=8765, max_attempts=20):
    """
    通过真实 bind 测试寻找 100% 干净且未被占用的端口
    严禁使用单纯的 connect_ex，因为处于 TIME_WAIT 状态的端口 connect_ex 也会返回非零，
    但在 Windows 下强行绑定处于 TIME_WAIT 的端口会导致 TCP RST 拒绝连接 (ERR_CONNECTION_REFUSED)！
    """
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

class GachaRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 简化日志输出
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {args[0]} - {args[1]}\n")

    def send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # API: 极速探活接口 (零 IO 零 CPU，毫秒级响应，专门供客户端冷启动探活使用)
        if path == "/api/ping":
            self.send_json(200, {"success": True, "ping": "pong"})
            return

        # API: 状态检查
        if path == "/api/status":
            custom_cfg = load_custom_config()
            effective_log = custom_cfg.get("customLogPath") or LOG_PATH
            url, err = extract_latest_gacha_url(effective_log)
            parsed_info = None
            if url:
                parsed_info, _ = parse_gacha_url(url)
            
            analysis = db_manager.get_analysis_for_player()
            self.send_json(200, {
                "success": True,
                "hasLog": os.path.exists(effective_log),
                "defaultLogPath": LOG_PATH,
                "customLogPath": custom_cfg.get("customLogPath", ""),
                "effectiveLogPath": effective_log,
                "hasUrl": url is not None,
                "latestPlayerId": parsed_info["playerId"] if parsed_info else None,
                "players": analysis.get("players", []),
                "activePlayer": analysis.get("activePlayer", None),
                "hasSavedData": analysis.get("hasData", False)
            })
            return

        # API: 获取统计分析数据
        if path == "/api/analysis":
            player_id = query.get("playerId", [None])[0]
            analysis = db_manager.get_analysis_for_player(player_id)
            self.send_json(200, {
                "success": True,
                "data": analysis
            })
            return

        # API: 获取某个卡池全部抽卡明细列表
        if path == "/api/pool_records":
            player_id = query.get("playerId", [None])[0]
            pool_type = query.get("poolType", ["1"])[0]
            
            players = db_manager.data.get("players", {})
            if not player_id and players:
                player_id = list(players.keys())[0]
                
            p_data = players.get(str(player_id), {}) if player_id else {}
            records = p_data.get("pools", {}).get(str(pool_type), [])
            # 倒序返回，最新的在前面
            sorted_records = sorted(records, key=lambda x: x.get("time", ""), reverse=True)
            for r in sorted_records:
                info = get_item_info(r.get("name", ""), r.get("qualityLevel"), r.get("resourceType"), r.get("resourceId"))
                r["avatar"] = info.get("avatar", "")
                r["element"] = info.get("element", "")
            self.send_json(200, {
                "success": True,
                "poolType": int(pool_type),
                "poolName": POOL_NAMES.get(int(pool_type), "未知卡池"),
                "records": sorted_records
            })
            return

        # API: 全量导出备份 (包含鸣潮、原神、自定义立绘配置及坚果云配置)
        if path in ("/api/backup/export", "/api/export_full"):
            payload = build_full_backup_payload()
            now_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="gacha_full_backup_{now_slug}.json"')
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        # API: 导出数据 (鸣潮独立格式)
        if path == "/api/export":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="wuwa_gacha_backup.json"')
            self.end_headers()
            self.wfile.write(json.dumps(db_manager.data, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        # API: 获取全局自定义配置与角色映射
        if path == "/api/config":
            cfg = get_all_config_data()
            latest_url, _ = extract_latest_gacha_url(LOG_PATH)
            cfg["detectedUrl"] = latest_url or ""
            self.send_json(200, {
                "success": True,
                "config": cfg
            })
            return

        # ================= 原神相关 API (GET) =================
        # 原神: 状态检查
        if path == "/api/genshin/status":
            url, err = extract_genshin_gacha_url(GENSHIN_LOG_PATH)
            analysis = genshin_db_manager.get_analysis_for_player()
            self.send_json(200, {
                "success": True,
                "hasLog": os.path.exists(GENSHIN_LOG_PATH),
                "defaultLogPath": GENSHIN_LOG_PATH,
                "hasUrl": url is not None,
                "detectedUrl": url or "",
                "players": analysis.get("players", []),
                "activePlayer": analysis.get("activePlayer", None),
                "hasSavedData": analysis.get("hasData", False)
            })
            return

        # 原神: 获取统计分析数据
        if path == "/api/genshin/analysis":
            player_id = query.get("playerId", [None])[0]
            analysis = genshin_db_manager.get_analysis_for_player(player_id)
            self.send_json(200, {
                "success": True,
                "data": analysis
            })
            return

        # 原神: 获取卡池明细流水
        if path == "/api/genshin/pool_records":
            player_id = query.get("playerId", [None])[0]
            pool_type = query.get("poolType", ["301"])[0]
            players = genshin_db_manager.data.get("players", {})
            if not player_id and players:
                player_id = list(players.keys())[0]
            p_data = players.get(str(player_id), {}) if player_id else {}
            records = list(p_data.get("pools", {}).get(str(pool_type), []))
            if str(pool_type) == "301" and "400" in p_data.get("pools", {}):
                records += list(p_data.get("pools", {}).get("400", []))
            sorted_records = sorted(records, key=lambda x: (x.get("time", ""), str(x.get("id", ""))), reverse=True)
            for r in sorted_records:
                r["qualityLevel"] = int(r.get("qualityLevel", r.get("rank_type", 3)))
                r["resourceType"] = r.get("resourceType") or r.get("item_type") or ("角色" if r["qualityLevel"] >= 4 else "武器")
                r["avatar"] = get_genshin_avatar_url(r.get("name", ""))
            self.send_json(200, {
                "success": True,
                "poolType": int(pool_type),
                "poolName": GENSHIN_POOL_NAMES.get(int(pool_type), "祈愿"),
                "records": sorted_records
            })
            return

        # 原神: 导出标准 UIGF JSON
        if path == "/api/genshin/export":
            player_id = query.get("playerId", [None])[0]
            uigf_data = genshin_db_manager.export_uigf(player_id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="genshin_uigf_backup.json"')
            self.end_headers()
            self.wfile.write(json.dumps(uigf_data, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        # 原神: 获取角色与武器图鉴配置
        if path == "/api/genshin/config":
            cfg = get_all_genshin_config_data()
            url, _ = extract_genshin_gacha_url(GENSHIN_LOG_PATH)
            cfg["detectedUrl"] = url or ""
            self.send_json(200, {
                "success": True,
                "config": cfg
            })
            return

        # API: 获取后台自动同步实时状态
        if path == "/api/auto_sync":
            self.send_json(200, {
                "success": True,
                "status": latest_auto_sync_status
            })
            return

        # API: 获取坚果云 / WebDAV 配置状态
        if path == "/api/webdav/config":
            cfg = load_webdav_config()
            self.send_json(200, {
                "success": True,
                "config": sanitize_config_for_frontend(cfg)
            })
            return

        # Favicon 处理 (绯雪高清图标)
        if path == "/favicon.ico":
            ico_path = os.path.join(STATIC_DIR, "favicon.ico")
            if os.path.exists(ico_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/x-icon")
                self.end_headers()
                with open(ico_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            self.send_response(204)
            self.end_headers()
            return

        # 静态文件服务
        if path == "/" or path == "/index.html":
            file_path = os.path.join(STATIC_DIR, "index.html")
            content_type = "text/html; charset=utf-8"
        else:
            decoded_path = urllib.parse.unquote(path)
            rel_path = decoded_path.lstrip("/")
            if rel_path.startswith("static/"):
                rel_path = rel_path[7:]
            file_path = os.path.join(STATIC_DIR, rel_path)

            # 智能回退：若未直接找到对应图片，尝试在 avatars 或上级 images 目录寻找
            if not os.path.exists(file_path):
                base_name = os.path.basename(rel_path)
                alt1 = os.path.join(STATIC_DIR, "images", "avatars", base_name)
                alt2 = os.path.join(STATIC_DIR, "images", base_name)
                if os.path.exists(alt1):
                    file_path = alt1
                elif os.path.exists(alt2):
                    file_path = alt2

            if file_path.endswith(".css"):
                content_type = "text/css; charset=utf-8"
            elif file_path.endswith(".js"):
                content_type = "application/javascript; charset=utf-8"
            elif file_path.endswith(".png"):
                content_type = "image/png"
            elif file_path.endswith(".webp"):
                content_type = "image/webp"
            elif file_path.endswith(".svg"):
                content_type = "image/svg+xml"
            elif file_path.endswith(".ico"):
                content_type = "image/x-icon"
            elif file_path.endswith(".json") or file_path.endswith(".webmanifest"):
                content_type = "application/manifest+json; charset=utf-8"
            else:
                content_type = "text/plain; charset=utf-8"

        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        
        try:
            req_data = json.loads(post_body.decode("utf-8")) if post_body else {}
        except Exception:
            req_data = {}

        # API: 触发后台全量自动同步 (鸣潮 & 原神)
        if path == "/api/auto_sync":
            if not latest_auto_sync_status["running"]:
                threading.Thread(target=run_auto_sync_all, daemon=True).start()
            self.send_json(200, {
                "success": True,
                "message": "后台全量自动同步已触发运行",
                "status": latest_auto_sync_status
            })
            return

        # API: 检测指定日志文件或目录
        if path == "/api/check_log":
            input_path = req_data.get("path", "").strip()
            log_b64 = req_data.get("logBase64", "")
            
            if log_b64:
                try:
                    raw_bytes = base64.b64decode(log_b64)
                    extracted_url, err = extract_gacha_url_from_bytes(raw_bytes)
                except Exception as e:
                    self.send_json(400, {"success": False, "message": f"文件解码失败: {e}"})
                    return
            else:
                if not input_path:
                    custom_cfg = load_custom_config()
                    input_path = custom_cfg.get("customLogPath") or LOG_PATH
                extracted_url, err = extract_latest_gacha_url(input_path)

            if not extracted_url:
                self.send_json(200, {
                    "success": False,
                    "hasUrl": False,
                    "path": input_path,
                    "message": err or "日志中未找到抽卡链接。请先在游戏内打开一次【唤取记录】页面后再试。"
                })
                return

            parsed_info, p_err = parse_gacha_url(extracted_url)
            self.send_json(200, {
                "success": True,
                "hasUrl": True,
                "path": input_path,
                "url": extracted_url,
                "playerId": parsed_info["playerId"] if parsed_info else None,
                "message": f"成功检测到有效抽卡凭据 (UID: {parsed_info['playerId'] if parsed_info else '未知'})"
            })
            return

        # API: 一键同步抽卡数据 (支持自定义日志目录与文件)
        if path == "/api/sync":
            input_url = req_data.get("url", "").strip()
            custom_log_path = req_data.get("logPath", "").strip()
            log_b64 = req_data.get("logBase64", "")
            remember_path = req_data.get("rememberPath", False)

            # 若用户选择记住该路径，自动存入 custom_config.json
            if custom_log_path and remember_path:
                cfg = load_custom_config()
                cfg["customLogPath"] = custom_log_path
                save_custom_config(cfg)

            # 智能判断：若传入的是原神日志或原神 URL，自动转入原神同步逻辑
            is_genshin_target = False
            genshin_url = None
            if input_url and ("authkey=" in input_url or "e20190909gacha" in input_url or "hk4e" in input_url):
                is_genshin_target = True
                genshin_url = input_url
            elif custom_log_path and ("output_log" in custom_log_path.lower() or "原神" in custom_log_path or "genshin" in custom_log_path.lower()):
                is_genshin_target = True
                genshin_url, _ = extract_genshin_gacha_url(custom_log_path)
            elif log_b64:
                try:
                    raw_b = base64.b64decode(log_b64)
                    g_url, _ = extract_genshin_url_from_bytes(raw_b)
                    if g_url:
                        is_genshin_target = True
                        genshin_url = g_url
                except Exception:
                    pass

            if is_genshin_target:
                if not genshin_url:
                    genshin_url, g_err = extract_genshin_gacha_url(custom_log_path or GENSHIN_LOG_PATH)
                if not genshin_url:
                    self.send_json(400, {
                        "success": False,
                        "message": "未能从原神日志中提取到祈愿链接。请先在原神游戏内打开一次【祈愿 -> 历史记录】页面后再试。"
                    })
                    return
                ok, msg, fetched_pools, uid = query_genshin_official_records(genshin_url)
                if not ok:
                    self.send_json(400, {"success": False, "message": msg})
                    return
                uid = uid or "100000001"
                total_added = 0
                for pt, rlist in fetched_pools.items():
                    total_added += genshin_db_manager.merge_records(uid, pt, rlist)
                analysis = genshin_db_manager.get_analysis_for_player(uid)
                self.send_json(200, {
                    "success": True,
                    "message": f"原神抽卡记录同步完成！UID: {uid}，共新增 {total_added} 条记录。",
                    "playerId": uid,
                    "game": "genshin",
                    "analysis": analysis,
                    "data": analysis
                })
                return

            # 鸣潮提取 URL：优先级 1.手动传入url 2.上传的logBase64 3.传入的logPath 4.自定义customLogPath 5.自定义customUrl 6.默认LOG_PATH
            if not input_url:
                err = None
                if log_b64:
                    try:
                        raw_bytes = base64.b64decode(log_b64)
                        input_url, err = extract_gacha_url_from_bytes(raw_bytes)
                    except Exception as e:
                        self.send_json(400, {"success": False, "message": f"读取上传日志异常: {e}"})
                        return
                elif custom_log_path:
                    input_url, err = extract_latest_gacha_url(custom_log_path)
                else:
                    custom_cfg = load_custom_config()
                    if custom_cfg and custom_cfg.get("customLogPath"):
                        input_url, err = extract_latest_gacha_url(custom_cfg["customLogPath"])
                    elif custom_cfg and custom_cfg.get("customUrl"):
                        input_url = custom_cfg["customUrl"].strip()
                    else:
                        input_url, err = extract_latest_gacha_url(LOG_PATH)

                if not input_url:
                    self.send_json(400, {
                        "success": False,
                        "message": err or "未从指定日志中提取到抽卡链接。请先在游戏内打开一次【唤取记录】页面，然后再尝试同步。"
                    })
                    return
                
            parsed_info, err = parse_gacha_url(input_url)
            if not parsed_info:
                self.send_json(400, {
                    "success": False,
                    "message": f"抽卡链接解析失败: {err}"
                })
                return

            player_id = parsed_info["playerId"]
            sync_results = {}
            total_added = 0
            errors = []

            # 遍历查询所有卡池 (1到7)
            for p_type in range(1, 8):
                records, err = query_official_records(parsed_info, p_type)
                if err:
                    # 如果出错了（比如链接过期）
                    errors.append(f"{POOL_NAMES.get(p_type, p_type)}: {err}")
                else:
                    added, total = db_manager.merge_records(player_id, p_type, records)
                    sync_results[POOL_NAMES.get(p_type, str(p_type))] = {
                        "added": added,
                        "total": total
                    }
                    total_added += added
                # 适度休眠防限频
                time.sleep(0.3)

            # 判断同步状态
            if errors and not sync_results:
                self.send_json(400, {
                    "success": False,
                    "message": "官方接口返回异常（链接可能已过期）。请在游戏内重新打开一次【唤取记录】页面，重新生成有效凭证后再点同步！",
                    "details": errors
                })
                return

            analysis = db_manager.get_analysis_for_player(player_id)
            self.send_json(200, {
                "success": True,
                "message": f"同步完成！共获取到 {total_added} 条全新抽卡记录。",
                "playerId": player_id,
                "totalAdded": total_added,
                "poolDetails": sync_results,
                "errors": errors if errors else None,
                "analysis": analysis
            })
            return

            # API: 全量恢复备份 (支持鸣潮、原神、自定义图鉴配置及坚果云配置)
        if path == "/api/backup/restore":
            content = req_data.get("data") if req_data.get("data") is not None else (req_data.get("jsonContent") or req_data)
            overwrite = bool(req_data.get("overwrite", False))
            ok, msg, detail = restore_from_payload(content, overwrite=overwrite)
            if ok:
                db_manager.load()
                genshin_db_manager.load()
            self.send_json(200 if ok else 400, {
                "success": ok,
                "message": msg,
                "detail": detail,
                "analysis": db_manager.get_analysis_for_player()
            })
            return

        # API: 导入数据 (全面兼容全量备份、原生备份、UIGF 3.0标准、鸣潮工坊等格式)
        if path == "/api/import":
            import_data = req_data.get("data")
            if not import_data:
                self.send_json(400, {"success": False, "message": "导入的数据内容为空"})
                return

            # 若为包含坚果云配置或双端记录的全量备份包，直接走全量恢复
            if isinstance(import_data, dict) and ("wuwa" in import_data or "genshin" in import_data or "webdavConfig" in import_data):
                ok, msg, detail = restore_from_payload(import_data)
                if ok:
                    db_manager.load()
                    genshin_db_manager.load()
                self.send_json(200 if ok else 400, {
                    "success": ok,
                    "message": msg,
                    "detail": detail,
                    "analysis": db_manager.get_analysis_for_player()
                })
                return

            normalized_players = normalize_imported_records(import_data)
            if not normalized_players:
                self.send_json(400, {"success": False, "message": "未能识别该文件中的有效鸣潮抽卡数据，请确认文件格式"})
                return

            imported_players = 0
            imported_records = 0
            last_pid = None
            for pid, pools in normalized_players.items():
                last_pid = pid
                for pt, rlist in pools.items():
                    added, _ = db_manager.merge_records(pid, pt, rlist)
                    imported_records += added
                imported_players += 1

            self.send_json(200, {
                "success": True,
                "message": f"成功兼容导入 {imported_players} 个账号，新增合并 {imported_records} 条历史抽卡记录！",
                "playerId": last_pid,
                "analysis": db_manager.get_analysis_for_player(last_pid)
            })
            return

        # API: 保存自定义配置 (人物角色、头像、ID 映射、别名、抽卡链接)
        if path == "/api/config":
            cfg = {}
            if os.path.exists(CUSTOM_CONFIG_PATH):
                try:
                    with open(CUSTOM_CONFIG_PATH, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                except Exception:
                    pass

            if "customUrl" in req_data:
                cfg["customUrl"] = req_data["customUrl"].strip()
            if "customLogPath" in req_data:
                cfg["customLogPath"] = req_data["customLogPath"].strip()
            if "idMap" in req_data:
                if "idMap" not in cfg:
                    cfg["idMap"] = {}
                cfg["idMap"].update(req_data["idMap"])
            if "aliasMap" in req_data:
                if "aliasMap" not in cfg:
                    cfg["aliasMap"] = {}
                cfg["aliasMap"].update(req_data["aliasMap"])
            if "characters" in req_data:
                if "characters" not in cfg:
                    cfg["characters"] = {}
                cfg["characters"].update(req_data["characters"])
            if "weapons" in req_data:
                if "weapons" not in cfg:
                    cfg["weapons"] = {}
                cfg["weapons"].update(req_data["weapons"])

            save_custom_config(cfg)
            self.send_json(200, {
                "success": True,
                "message": "自定义配置已保存并立即生效！",
                "config": get_all_config_data(),
                "analysis": db_manager.get_analysis_for_player()
            })
            return

        # API: 加载演示数据
        if path == "/api/demo":
            demo_pid = "UID:10086888 (演示)"
            from demo_data import generate_demo_records
            demo_pools = generate_demo_records()
            for pt, rlist in demo_pools.items():
                db_manager.merge_records(demo_pid, pt, rlist)
            self.send_json(200, {
                "success": True,
                "message": "演示数据加载成功！快来看看欧非分析与出金流水吧~",
                "playerId": demo_pid,
                "analysis": db_manager.get_analysis_for_player(demo_pid)
            })
            return

        # API: 清空账号数据
        if path == "/api/clear":
            pid = req_data.get("playerId")
            if pid and pid in db_manager.data.get("players", {}):
                del db_manager.data["players"][pid]
                db_manager.save()
            self.send_json(200, {
                "success": True,
                "message": f"已清除账号 {pid} 的本地数据",
                "analysis": db_manager.get_analysis_for_player()
            })
            return

        # ================= 原神相关 API (POST) =================
        # 原神: 检测指定日志文件
        if path == "/api/genshin/check_log":
            input_path = req_data.get("path", "").strip()
            log_b64 = req_data.get("logBase64", "")
            
            if log_b64:
                try:
                    raw_bytes = base64.b64decode(log_b64)
                    url, err = extract_genshin_url_from_bytes(raw_bytes)
                except Exception as e:
                    self.send_json(400, {"success": False, "message": f"文件解码失败: {e}"})
                    return
            else:
                input_path = input_path or GENSHIN_LOG_PATH
                url, err = extract_genshin_gacha_url(input_path)

            if not url:
                self.send_json(200, {
                    "success": False,
                    "hasUrl": False,
                    "path": input_path,
                    "message": err or "日志中未找到抽卡链接。请先在原神游戏内打开一次【祈愿 -> 历史记录】页面后再试。"
                })
                return
            
            self.send_json(200, {
                "success": True,
                "hasUrl": True,
                "path": input_path,
                "url": url,
                "playerId": "原神玩家",
                "message": "成功检测到有效原神祈愿历史凭据，点击下方按钮即可开始同步！"
            })
            return

        # 原神: 同步抽卡数据
        if path == "/api/genshin/sync":
            input_url = req_data.get("url", "").strip()
            log_path = req_data.get("logPath", "").strip()
            log_b64 = req_data.get("logBase64", "")
            
            if not input_url:
                if log_b64:
                    try:
                        raw_bytes = base64.b64decode(log_b64)
                        input_url, err = extract_genshin_url_from_bytes(raw_bytes)
                    except Exception as e:
                        self.send_json(400, {"success": False, "message": f"读取上传日志异常: {e}"})
                        return
                else:
                    log_path = log_path or GENSHIN_LOG_PATH
                    input_url, err = extract_genshin_gacha_url(log_path)

                if not input_url:
                    self.send_json(400, {"success": False, "message": err or "未找到有效的抽卡链接。请先在原神游戏内打开一次【祈愿 -> 历史记录】"})
                    return
            
            ok, msg, fetched_pools, uid = query_genshin_official_records(input_url)
            if not ok:
                self.send_json(400, {"success": False, "message": msg})
                return
            
            if not uid:
                uid = "100000001"
            
            total_added = 0
            for pt, rlist in fetched_pools.items():
                total_added += genshin_db_manager.merge_records(uid, pt, rlist)
            
            analysis = genshin_db_manager.get_analysis_for_player(uid)
            self.send_json(200, {
                "success": True,
                "message": f"原神抽卡记录同步完成！UID: {uid}，共新增 {total_added} 条记录。",
                "playerId": uid,
                "analysis": analysis,
                "data": analysis
            })
            return

        # 原神: 加载演示数据
        if path == "/api/genshin/demo":
            demo_pid = "UID:10086888 (演示)"
            from demo_data_genshin import generate_genshin_demo_records
            demo_pools = generate_genshin_demo_records()
            for pt, rlist in demo_pools.items():
                genshin_db_manager.merge_records(demo_pid, pt, rlist)
            self.send_json(200, {
                "success": True,
                "message": "原神演示数据加载成功！快来看看欧非分析与出金流水吧~",
                "playerId": demo_pid,
                "analysis": genshin_db_manager.get_analysis_for_player(demo_pid)
            })
            return

        # 原神: 导入标准 UIGF JSON (全面兼容全量备份)
        if path == "/api/genshin/import":
            raw_text = req_data.get("jsonContent", "")
            try:
                uigf_obj = json.loads(raw_text) if isinstance(raw_text, str) else raw_text
            except Exception as e:
                self.send_json(400, {"success": False, "message": f"JSON 解析失败: {e}"})
                return

            # 若为包含坚果云配置或双端记录的全量备份包，直接走全量恢复
            if isinstance(uigf_obj, dict) and ("wuwa" in uigf_obj or "genshin" in uigf_obj or "webdavConfig" in uigf_obj):
                ok, msg, detail = restore_from_payload(uigf_obj)
                if ok:
                    db_manager.load()
                    genshin_db_manager.load()
                self.send_json(200 if ok else 400, {
                    "success": ok,
                    "message": msg,
                    "detail": detail,
                    "analysis": genshin_db_manager.get_analysis_for_player()
                })
                return

            ok, msg, count = genshin_db_manager.import_uigf(uigf_obj)
            if ok:
                self.send_json(200, {
                    "success": True,
                    "message": msg,
                    "analysis": genshin_db_manager.get_analysis_for_player()
                })
            else:
                self.send_json(400, {"success": False, "message": msg})
            return

        # 原神: 清空账号数据
        if path == "/api/genshin/clear":
            pid = req_data.get("playerId")
            if pid and pid in genshin_db_manager.data.get("players", {}):
                del genshin_db_manager.data["players"][pid]
                genshin_db_manager.save()
            self.send_json(200, {
                "success": True,
                "message": f"已清除原神账号 {pid} 的本地数据",
                "analysis": genshin_db_manager.get_analysis_for_player()
            })
            return

        # 原神: 保存图鉴配置
        if path == "/api/genshin/config":
            try:
                save_genshin_custom_config(req_data)
                self.send_json(200, {
                    "success": True,
                    "message": "原神图鉴条目已保存并生效！",
                    "config": get_all_genshin_config_data()
                })
            except Exception as e:
                self.send_json(500, {
                    "success": False,
                    "message": f"保存原神配置失败: {str(e)}"
                })
            return

        # 坚果云: 保存 WebDAV 配置
        if path == "/api/webdav/config":
            try:
                old_cfg = load_webdav_config()
                new_cfg = dict(req_data)
                if not new_cfg.get("password") and old_cfg.get("password"):
                    new_cfg["password"] = old_cfg["password"]
                saved = save_webdav_config(new_cfg)
                self.send_json(200, {
                    "success": True,
                    "message": "坚果云 / WebDAV 配置已保存！",
                    "config": sanitize_config_for_frontend(saved)
                })
            except Exception as e:
                self.send_json(500, {
                    "success": False,
                    "message": f"保存 WebDAV 配置失败: {str(e)}"
                })
            return

        # 坚果云: 测试 WebDAV 连通性
        if path == "/api/webdav/test":
            try:
                target_cfg = dict(req_data)
                old_cfg = load_webdav_config()
                if not target_cfg.get("password") and old_cfg.get("password"):
                    target_cfg["password"] = old_cfg["password"]
                ok, msg = test_webdav_connection(target_cfg)
                self.send_json(200 if ok else 400, {
                    "success": ok,
                    "message": msg
                })
            except Exception as e:
                self.send_json(500, {
                    "success": False,
                    "message": f"测试连接异常: {str(e)}"
                })
            return

        # 坚果云: 立即上传备份
        if path == "/api/webdav/backup":
            try:
                ok, msg, detail = upload_backup_to_webdav()
                self.send_json(200 if ok else 400, {
                    "success": ok,
                    "message": msg,
                    "detail": detail
                })
            except Exception as e:
                self.send_json(500, {
                    "success": False,
                    "message": f"备份异常: {str(e)}"
                })
            return

        # 坚果云: 从云端拉取恢复
        if path == "/api/webdav/restore":
            try:
                overwrite = bool(req_data.get("overwrite", False))
                ok, msg, detail = restore_backup_from_webdav(overwrite=overwrite)
                if ok:
                    db_manager.load()
                    genshin_db_manager.load()
                self.send_json(200 if ok else 400, {
                    "success": ok,
                    "message": msg,
                    "detail": detail
                })
            except Exception as e:
                self.send_json(500, {
                    "success": False,
                    "message": f"恢复异常: {str(e)}"
                })
            return

        self.send_error(404, "API endpoint not found")

def start_server(port=None, auto_open_browser=True):
    if port is None:
        port = find_available_port(8765)
        
    server_address = ("127.0.0.1", port)
    httpd = ServerClass(server_address, GachaRequestHandler)
    url = f"http://127.0.0.1:{port}"
    
    print("=" * 60)
    print("   鸣潮 & 原神 抽卡分析系统 (Gacha Tracker)")
    print(f"   本地服务已成功启动: {url}")
    print(f"   游戏日志路径: {LOG_PATH}")
    print("=" * 60)
    
    # 探测本地 HTTP 服务就绪状态，确保服务端主循环 100% 准备就绪后再唤起默认浏览器
    def open_browser():
        start_time = time.time()
        while time.time() - start_time < 6.0:
            try:
                req = urllib.request.Request(f"{url}/api/status", headers={"User-Agent": "ReadyChecker"})
                with urllib.request.urlopen(req, timeout=0.3) as resp:
                    if resp.status == 200:
                        time.sleep(0.2)
                        break
            except Exception:
                time.sleep(0.1)
        webbrowser.open(url)
        
    # 窗口唤起 3 秒后再执行后台双端自动同步，不抢占首屏资源
    def delayed_auto_sync():
        time.sleep(3.0)
        run_auto_sync_all()
    threading.Thread(target=delayed_auto_sync, daemon=True).start()

    if auto_open_browser:
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已安全退出。")
        httpd.server_close()

if __name__ == "__main__":
    start_server()
