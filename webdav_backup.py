# -*- coding: utf-8 -*-
"""
坚果云 / WebDAV 自动备份与跨设备同步模块
支持坚果云官方 WebDAV (https://dav.jianguoyun.com/dav/) 及任意标准 WebDAV 服务器
纯 Python 标准库原生实现，零第三方依赖
"""

import os
import sys
import json
import base64
import ssl
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_PATH = os.path.join(DATA_DIR, "webdav_config.json")

JIANGUOYUN_DEFAULT_URL = "https://dav.jianguoyun.com/dav/"
DEFAULT_REMOTE_FOLDER = "GachaTracker"

def _get_ssl_context():
    """获取忽略证书严格校验的 SSL 上下文（防代理或加速器断流）"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def _get_auth_header(username: str, password: str) -> str:
    """生成 HTTP Basic Auth 请求头"""
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"

def load_webdav_config() -> Dict[str, Any]:
    """读取保存的 WebDAV 配置"""
    default_cfg = {
        "enabled": False,
        "provider": "jianguoyun",
        "url": JIANGUOYUN_DEFAULT_URL,
        "username": "",
        "password": "",
        "remoteFolder": DEFAULT_REMOTE_FOLDER,
        "autoBackupOnSync": True,
        "lastBackupTime": "",
        "lastBackupStatus": ""
    }
    if not os.path.exists(CONFIG_PATH):
        return default_cfg
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            default_cfg.update(cfg)
            return default_cfg
    except Exception:
        return default_cfg

def save_webdav_config(new_cfg: Dict[str, Any]) -> Dict[str, Any]:
    """持久化保存 WebDAV 配置"""
    os.makedirs(DATA_DIR, exist_ok=True)
    cfg = load_webdav_config()
    cfg.update(new_cfg)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    return cfg

def sanitize_config_for_frontend(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """返回给前端的脱敏配置（密码掩码）"""
    safe = dict(cfg)
    if safe.get("password"):
        safe["hasPassword"] = True
        safe["passwordMasked"] = "•" * min(8, len(safe["password"]))
    else:
        safe["hasPassword"] = False
        safe["passwordMasked"] = ""
    return safe

def _build_url(base_url: str, folder: str, filename: str = "") -> str:
    """拼装规范的 WebDAV 资源 URL"""
    clean_base = base_url.strip().rstrip("/")
    clean_folder = folder.strip().strip("/")
    if filename:
        return f"{clean_base}/{clean_folder}/{filename}"
    return f"{clean_base}/{clean_folder}/"

def _send_webdav_request(url: str, method: str, username: str, password: str, data: Optional[bytes] = None) -> Tuple[int, bytes, Dict[str, str]]:
    """底层通用 WebDAV 请求封装"""
    ctx = _get_ssl_context()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", _get_auth_header(username, password))
    req.add_header("User-Agent", "GachaTracker-Client/1.0")
    if data:
        req.add_header("Content-Type", "application/json; charset=utf-8")

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            body = resp.read()
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, body, headers
    except urllib.error.HTTPError as e:
        body = e.read()
        headers = {k.lower(): v for k, v in e.headers.items()}
        return e.code, body, headers
    except Exception as e:
        raise RuntimeError(f"WebDAV 网络请求异常: {str(e)}")

def ensure_remote_folder(cfg: Dict[str, Any]) -> Tuple[bool, str]:
    """确保坚果云端目标文件夹存在（MKCOL）"""
    url = _build_url(cfg["url"], cfg["remoteFolder"])
    status, _, _ = _send_webdav_request(url, "PROPFIND", cfg["username"], cfg["password"])
    if status in (200, 207):
        return True, "远程目录已存在"
    if status == 404:
        # 创建目录
        mk_status, _, _ = _send_webdav_request(url, "MKCOL", cfg["username"], cfg["password"])
        if mk_status in (200, 201, 204):
            return True, "已成功创建远程备份目录"
        return False, f"创建远程目录失败: HTTP {mk_status}"
    if status in (401, 403):
        return False, "坚果云账号或应用密码错误，请检查认证信息"
    return False, f"检查远程目录返回 HTTP {status}"

def test_webdav_connection(cfg: Dict[str, Any]) -> Tuple[bool, str]:
    """测试坚果云 / WebDAV 连通性"""
    username = cfg.get("username", "").strip()
    password = cfg.get("password", "").strip()
    url = cfg.get("url", "").strip() or JIANGUOYUN_DEFAULT_URL
    folder = cfg.get("remoteFolder", "").strip() or DEFAULT_REMOTE_FOLDER

    if not username:
        return False, "请输入坚果云账号 (通常为登录邮箱)"
    if not password:
        return False, "请输入坚果云应用密码 (非登录密码)"

    try:
        # 探测根目录
        root_status, _, _ = _send_webdav_request(url, "PROPFIND", username, password)
        if root_status in (401, 403):
            return False, "认证失败！请确保使用的是坚果云【应用密码】而非登录密码"
        if root_status not in (200, 207, 404):
            return False, f"连接服务器响应异常: HTTP {root_status}"

        # 确保创建目录
        ok, msg = ensure_remote_folder({"url": url, "remoteFolder": folder, "username": username, "password": password})
        if not ok:
            return False, msg

        return True, "坚果云 WebDAV 连接成功！已就绪远程备份目录"
    except Exception as e:
        return False, f"连接测试失败: {str(e)}"

def build_full_backup_payload() -> Dict[str, Any]:
    """构建全量双端抽卡数据与配置的完整备份包"""
    wuwa_data = {}
    genshin_data = {}
    wuwa_cfg = {}
    genshin_cfg = {}

    wuwa_path = os.path.join(DATA_DIR, "gacha_records.json")
    if os.path.exists(wuwa_path):
        try:
            with open(wuwa_path, "r", encoding="utf-8") as f:
                wuwa_data = json.load(f)
        except Exception:
            pass

    genshin_path = os.path.join(DATA_DIR, "genshin_records.json")
    if os.path.exists(genshin_path):
        try:
            with open(genshin_path, "r", encoding="utf-8") as f:
                genshin_data = json.load(f)
        except Exception:
            pass

    custom_wuwa_path = os.path.join(DATA_DIR, "custom_config.json")
    if os.path.exists(custom_wuwa_path):
        try:
            with open(custom_wuwa_path, "r", encoding="utf-8") as f:
                wuwa_cfg = json.load(f)
        except Exception:
            pass

    custom_genshin_path = os.path.join(DATA_DIR, "genshin_custom_config.json")
    if os.path.exists(custom_genshin_path):
        try:
            with open(custom_genshin_path, "r", encoding="utf-8") as f:
                genshin_cfg = json.load(f)
        except Exception:
            pass

    webdav_cfg = load_webdav_config()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "version": "1.1",
        "app": "GachaTracker",
        "backupTime": now_str,
        "wuwa": wuwa_data,
        "genshin": genshin_data,
        "customConfig": {
            "wuwa": wuwa_cfg,
            "genshin": genshin_cfg
        },
        "webdavConfig": webdav_cfg
    }

def restore_from_payload(data: Dict[str, Any], overwrite: bool = False) -> Tuple[bool, str, Dict[str, Any]]:
    """
    从备份数据字典中恢复鸣潮数据、原神数据、自定义配置及坚果云配置
    :param overwrite: 若为 True，则执行全量镜像覆盖替换（彻底清空本地现有，完全以备份为准）；
                      若为 False，则执行多重集增量去重合并（保留本地已有新记录，零重复叠加）。
    """
    if not isinstance(data, dict):
        return False, "备份数据格式无效，应为 JSON 对象", {}

    added_wuwa = 0
    added_genshin = 0
    webdav_restored = False
    custom_restored = False

    from gacha_core import GachaDataManager, normalize_imported_records
    db_wuwa = GachaDataManager(os.path.join(DATA_DIR, "gacha_records.json"))
    from genshin_core import GenshinDataManager
    db_genshin = GenshinDataManager(os.path.join(DATA_DIR, "genshin_records.json"))

    if overwrite:
        # 全量覆盖模式：以备份文件为绝对基准镜像替换
        if "wuwa" in data and isinstance(data["wuwa"], dict):
            db_wuwa.data = dict(data["wuwa"])
            db_wuwa.save()
        elif "players" in data and not ("info" in data and "uigf_version" in data.get("info", {})):
            normalized = normalize_imported_records(data)
            db_wuwa.data = {"players": {pid: {"playerId": pid, "lastSyncTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "pools": pools} for pid, pools in normalized.items()}}
            db_wuwa.save()

        if "genshin" in data and isinstance(data["genshin"], dict):
            db_genshin.data = dict(data["genshin"])
            db_genshin.save()
        elif "info" in data or "list" in data:
            db_genshin.data = {"players": {}}
            db_genshin.import_uigf(data)
    else:
        # 1. 增量合并鸣潮抽卡数据 (采用多重集差分精确去重)
        if "wuwa" in data and isinstance(data["wuwa"], dict):
            wuwa_records = data["wuwa"].get("players", {})
            for pid, pdata in wuwa_records.items():
                pools = pdata.get("pools", {})
                for pt, rlist in pools.items():
                    c, _ = db_wuwa.merge_records(pid, pt, rlist)
                    added_wuwa += c
        elif "players" in data and not ("info" in data and "uigf_version" in data.get("info", {})):
            # 兼容纯鸣潮数据库格式
            normalized = normalize_imported_records(data)
            for pid, pools in normalized.items():
                for pt, rlist in pools.items():
                    c, _ = db_wuwa.merge_records(pid, pt, rlist)
                    added_wuwa += c

        # 2. 增量合并原神抽卡数据
        if "genshin" in data and isinstance(data["genshin"], dict):
            genshin_records = data["genshin"].get("players", {})
            for pid, pdata in genshin_records.items():
                pools = pdata.get("pools", {})
                for pt, rlist in pools.items():
                    c = db_genshin.merge_records(pid, pt, rlist)
                    added_genshin += c
        elif "info" in data or "list" in data:
            # 兼容原神标准 UIGF 格式
            ok, _, c = db_genshin.import_uigf(data)
            if ok:
                added_genshin += c

    # 3. 恢复自定义配置（立绘/别名等）
    custom_cfg = data.get("customConfig", {})
    if isinstance(custom_cfg, dict):
        if custom_cfg.get("wuwa"):
            from characters_db import save_custom_config
            save_custom_config(custom_cfg["wuwa"])
            custom_restored = True
        if custom_cfg.get("genshin"):
            from genshin_db import save_genshin_custom_config
            save_genshin_custom_config(custom_cfg["genshin"])
            custom_restored = True

    # 4. 恢复坚果云 / WebDAV 配置
    webdav_cfg = data.get("webdavConfig")
    if isinstance(webdav_cfg, dict):
        if webdav_cfg.get("username") or webdav_cfg.get("password") or webdav_cfg.get("url"):
            save_webdav_config(webdav_cfg)
            webdav_restored = True

    # 统计最终双端数据体量与账号列表
    wuwa_players = list(db_wuwa.data.get("players", {}).keys())
    total_wuwa_records = sum(
        len(rlist) 
        for p in db_wuwa.data.get("players", {}).values() 
        for rlist in p.get("pools", {}).values()
    )

    genshin_players = list(db_genshin.data.get("players", {}).keys())
    total_genshin_records = sum(
        len(rlist) 
        for p in db_genshin.data.get("players", {}).values() 
        for rlist in p.get("pools", {}).values()
    )

    # 构建详尽透明的提示信息
    parts = []
    if wuwa_players:
        wuwa_summary = f"鸣潮 {len(wuwa_players)} 个账号已就绪 (共 {total_wuwa_records} 条" + (f"，本次新增 {added_wuwa} 条" if added_wuwa > 0 else "，数据已完整") + ")"
        parts.append(wuwa_summary)
    if genshin_players:
        genshin_summary = f"原神 {len(genshin_players)} 个账号已就绪 (共 {total_genshin_records} 条" + (f"，本次新增 {added_genshin} 条" if added_genshin > 0 else "，数据已完整") + ")"
        parts.append(genshin_summary)
    if webdav_restored:
        parts.append("坚果云配置已恢复")
    if custom_restored:
        parts.append("自定义图鉴配置已恢复")

    prefix = "全量镜像覆盖恢复成功！" if overwrite else "恢复成功！"
    if not parts:
        msg = "备份恢复完成，当前数据已是最新"
    else:
        msg = prefix + "；".join(parts)

    return True, msg, {
        "mode": "overwrite" if overwrite else "merge",
        "addedWuwa": added_wuwa,
        "addedGenshin": added_genshin,
        "totalWuwaRecords": total_wuwa_records,
        "totalGenshinRecords": total_genshin_records,
        "wuwaPlayers": wuwa_players,
        "genshinPlayers": genshin_players,
        "webdavRestored": webdav_restored,
        "customRestored": custom_restored,
        "backupTime": data.get("backupTime", "未知")
    }

def upload_backup_to_webdav(cfg: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Dict[str, Any]]:
    """将本地最新抽卡数据及配置打包上传至坚果云 / WebDAV"""
    if cfg is None:
        cfg = load_webdav_config()

    username = cfg.get("username", "").strip()
    password = cfg.get("password", "").strip()
    url = cfg.get("url", "").strip() or JIANGUOYUN_DEFAULT_URL
    folder = cfg.get("remoteFolder", "").strip() or DEFAULT_REMOTE_FOLDER

    if not username or not password:
        return False, "未配置坚果云账号或应用密码，请先在设置中填写", {}

    try:
        # 1. 确保远端文件夹存在
        ok, msg = ensure_remote_folder(cfg)
        if not ok:
            return False, f"初始化坚果云目录失败: {msg}", {}

        # 2. 构建备份文件
        payload = build_full_backup_payload()
        payload_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        size_kb = round(len(payload_bytes) / 1024, 1)

        # 3. 仅上传单一全量备份文件: full_backup.json (鸣潮+原神+角色配置+坚果云配置)
        full_url = _build_url(url, folder, "full_backup.json")
        status, _, _ = _send_webdav_request(full_url, "PUT", username, password, payload_bytes)
        if status not in (200, 201, 204):
            return False, f"上传备份文件失败: HTTP {status}", {}

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_webdav_config({
            "lastBackupTime": now_str,
            "lastBackupStatus": f"成功 ({size_kb} KB)"
        })

        return True, f"已成功备份至坚果云！共上传 {size_kb} KB 数据 (full_backup.json)", {
            "backupTime": now_str,
            "sizeKb": size_kb
        }
    except Exception as e:
        save_webdav_config({
            "lastBackupStatus": f"失败: {str(e)}"
        })
        return False, f"备份至坚果云异常: {str(e)}", {}

def restore_backup_from_webdav(cfg: Optional[Dict[str, Any]] = None, overwrite: bool = False) -> Tuple[bool, str, Dict[str, Any]]:
    """从坚果云拉取远端备份并恢复到本地（支持增量合并或全量覆盖）"""
    if cfg is None:
        cfg = load_webdav_config()

    username = cfg.get("username", "").strip()
    password = cfg.get("password", "").strip()
    url = cfg.get("url", "").strip() or JIANGUOYUN_DEFAULT_URL
    folder = cfg.get("remoteFolder", "").strip() or DEFAULT_REMOTE_FOLDER

    if not username or not password:
        return False, "未配置坚果云账号或应用密码", {}

    try:
        full_url = _build_url(url, folder, "full_backup.json")
        status, body, _ = _send_webdav_request(full_url, "GET", username, password)
        if status == 404:
            return False, "坚果云中暂无备份文件 (full_backup.json)，请先进行一次备份", {}
        if status != 200:
            return False, f"拉取备份失败: HTTP {status}", {}

        data = json.loads(body.decode("utf-8"))
        return restore_from_payload(data, overwrite=overwrite)
    except Exception as e:
        return False, f"从坚果云恢复异常: {str(e)}", {}
