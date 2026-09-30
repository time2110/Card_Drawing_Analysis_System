# -*- coding: utf-8 -*-
"""
原神抽卡分析核心逻辑与数据管理器 (Genshin Impact Gacha Core)
实现原神日志解析、官方 API 抓取、UIGF 导入导出与数学期望统计分析
"""

import os
import re
import json
import time
import ssl
import urllib.parse
import urllib.request
from typing import Dict, List, Tuple, Any, Optional

from genshin_db import (
    GENSHIN_POOL_NAMES,
    GENSHIN_CHARACTERS_5STAR,
    GENSHIN_WEAPONS_5STAR,
    is_genshin_standard_5star,
    get_genshin_avatar_url
)

# 默认官方 API 端点
GENSHIN_API_CN = "https://public-operation-hk4e.mihoyo.com/gacha_info/api/getGachaLog"
GENSHIN_API_OS = "https://public-operation-hk4e-sg.hoyoverse.com/gacha_info/api/getGachaLog"

def get_default_genshin_log_path() -> str:
    """获取原神客户端默认日志路径"""
    user_profile = os.environ.get("USERPROFILE", "")
    locallow = os.path.join(user_profile, "AppData", "LocalLow")
    
    candidates = [
        # 国服
        os.path.join(locallow, "miHoYo", "原神", "output_log.txt"),
        os.path.join(locallow, "miHoYo", "原神", "output_log_last.txt"),
        # 国际服
        os.path.join(locallow, "Cognosphere", "Genshin Impact", "output_log.txt"),
        os.path.join(locallow, "Cognosphere", "Genshin Impact", "output_log_last.txt"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.normpath(c)
    return os.path.normpath(candidates[0])

def extract_genshin_url_from_bytes(content_bytes: bytes) -> Tuple[Optional[str], Optional[str]]:
    """从二进制字节流中提取原神抽卡链接（支持直接上传的文件内容）"""
    try:
        content = content_bytes.decode("utf-8", errors="ignore")
        # 匹配日志中的 Webview 祈愿历史记录 URL
        # 格式示例：https://webstatic.mihoyo.com/hk4e/event/e20190909gacha-df01aea2/index.html?...authkey=...
        pattern = r"https?://[^\s\x22\x27\x3c\x3e]+(?:e20190909gacha|getGachaLog)[^\s\x22\x27\x3c\x3e]*"
        matches = re.findall(pattern, content)
        if not matches:
            return None, "未在日志中发现有效的抽卡记录链接，请确保在游戏内打开过一次【祈愿 -> 历史记录】"
            
        latest_url = matches[-1]
        # 去除 HTML/日志转义符
        clean_url = latest_url.replace(r"\u0026", "&").replace("&amp;", "&").rstrip(",").rstrip(";").rstrip(" ")
        # 移除 URL 结尾的 hash 锚点
        if "#/log" in clean_url:
            clean_url = clean_url.split("#/log")[0]
        return clean_url, None
    except Exception as e:
        return None, f"解析原神日志异常: {str(e)}"

def extract_genshin_gacha_url(log_path: str) -> Tuple[Optional[str], Optional[str]]:
    """从原神 output_log.txt 日志中提取最新的抽卡链接"""
    if not os.path.exists(log_path):
        return None, f"日志文件不存在: {log_path}"
    
    try:
        with open(log_path, "rb") as f:
            return extract_genshin_url_from_bytes(f.read())
    except Exception as e:
        return None, f"读取原神日志出错: {str(e)}"

def parse_genshin_url_params(url: str) -> Dict[str, str]:
    """解析原神抽卡 URL 中的查询参数"""
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    params = {}
    for k, v in qs.items():
        if v:
            params[k] = v[0]
    return params

def query_genshin_official_records(
    auth_url: str,
    target_pool_type: Optional[int] = None,
    progress_callback: Optional[Any] = None
) -> Tuple[bool, str, Dict[str, List[Dict[str, Any]]], Optional[str]]:
    """
    通过原神官方 API 批量抓取抽卡记录
    返回: (成功状态, 消息提示, 卡池字典, 玩家UID)
    """
    params = parse_genshin_url_params(auth_url)
    authkey = params.get("authkey")
    if not authkey:
        return False, "链接缺少核心鉴权参数 authkey", {}, None
        
    game_biz = params.get("game_biz", "hk4e_cn")
    is_os = "hk4e_global" in game_biz or "hk4e_os" in game_biz
    api_endpoint = GENSHIN_API_OS if is_os else GENSHIN_API_CN
    
    # 待拉取的卡池列表：角色(301)、武器(302)、常驻(200)、集录(500)、新手(100)
    pool_types = [target_pool_type] if target_pool_type else [301, 302, 200, 500, 100]
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    fetched_data: Dict[str, List[Dict[str, Any]]] = {}
    detected_uid = None
    
    for pt in pool_types:
        pool_records: List[Dict[str, Any]] = []
        page = 1
        end_id = "0"
        
        while True:
            query_args = {
                "authkey_ver": params.get("authkey_ver", "1"),
                "sign_type": params.get("sign_type", "2"),
                "auth_appid": params.get("auth_appid", "webview_gacha"),
                "lang": params.get("lang", "zh-cn"),
                "game_biz": game_biz,
                "authkey": authkey,
                "gacha_type": str(pt),
                "page": str(page),
                "size": "20",
                "end_id": end_id
            }
            req_url = f"{api_endpoint}?{urllib.parse.urlencode(query_args)}"
            req = urllib.request.Request(req_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            try:
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                return False, f"请求官方 API 失败: {str(e)}", fetched_data, detected_uid
                
            retcode = res.get("retcode", -1)
            if retcode != 0:
                msg = res.get("message", "未知错误")
                if "visit too frequently" in msg.lower():
                    # 遇到米哈游频控，自动休眠 1.5 秒后重试（最多重试 3 次）
                    retried = False
                    for _ in range(3):
                        time.sleep(1.5)
                        try:
                            with urllib.request.urlopen(req, context=ctx, timeout=10) as r_resp:
                                r_res = json.loads(r_resp.read().decode("utf-8"))
                            if r_res.get("retcode") == 0:
                                res = r_res
                                retried = True
                                break
                        except Exception:
                            pass
                    if not retried:
                        return False, f"官方访问过于频繁: {msg} (请稍后重试)", fetched_data, detected_uid
                elif "authkey valid" in msg.lower() or "authkey timeout" in msg.lower():
                    return False, f"官方鉴权失效或超时: {msg} (请重新在原神游戏内打开一次历史记录)", fetched_data, detected_uid
                else:
                    return False, f"API 报错 (代码 {retcode}): {msg}", fetched_data, detected_uid
                
            items = res.get("data", {}).get("list", [])
            if not items:
                break
                
            for item in items:
                uid = item.get("uid")
                if uid and not detected_uid:
                    detected_uid = str(uid)
                    
                # 规范化记录字段
                pool_records.append({
                    "id": str(item.get("id")),
                    "uid": str(item.get("uid", "")),
                    "gacha_type": str(item.get("gacha_type")),
                    "name": item.get("name", ""),
                    "time": item.get("time", ""),
                    "item_type": item.get("item_type", "角色" if int(item.get("rank_type", 3)) >= 4 else "武器"),
                    "rank_type": int(item.get("rank_type", 3)),
                    "qualityLevel": int(item.get("rank_type", 3)),
                    "resourceType": item.get("item_type", "")
                })
                
            end_id = str(items[-1].get("id"))
            page += 1
            if progress_callback:
                progress_callback(pt, len(pool_records))
            time.sleep(0.35)  # 稳健间隔，避免频繁请求触发米哈游限流
            
        fetched_data[str(pt)] = pool_records
        time.sleep(0.3)  # 每个卡池之间稍作停顿
        
    return True, "数据同步成功", fetched_data, detected_uid

class GenshinDataManager:
    """原神抽卡数据持久化管理器"""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data: Dict[str, Any] = {"players": {}}
        self.load()
        
    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {"players": {}}
        else:
            self.data = {"players": {}}
            self.save()
            
    def save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
            
    def merge_records(self, player_id: str, pool_type: str, records: List[Dict[str, Any]]) -> int:
        """合并抽卡记录，根据 record id 去重，返回新增记录数"""
        player_id = str(player_id)
        pool_type = str(pool_type)
        if "players" not in self.data:
            self.data["players"] = {}
        if player_id not in self.data["players"]:
            self.data["players"][player_id] = {"uid": player_id, "pools": {}}
            
        player_pools = self.data["players"][player_id].setdefault("pools", {})
        existing = player_pools.setdefault(pool_type, [])
        
        exist_ids = {str(r.get("id")) for r in existing if "id" in r}
        added_count = 0
        for r in records:
            rid = str(r.get("id"))
            if rid not in exist_ids:
                existing.append(r)
                exist_ids.add(rid)
                added_count += 1
                
        # 始终按时间正序排列（最旧的在前面，方便计算保底垫抽）
        existing.sort(key=lambda x: (x.get("time", ""), str(x.get("id", ""))))
        self.save()
        return added_count

    def export_uigf(self, player_id: Optional[str] = None) -> Dict[str, Any]:
        """导出为标准的 UIGF v3.0 格式 JSON"""
        players = self.data.get("players", {})
        if not players:
            return {"info": {}, "list": []}
            
        if not player_id or player_id not in players:
            player_id = list(players.keys())[0]
            
        p_data = players[player_id]
        uigf_list = []
        for ptype, rlist in p_data.get("pools", {}).items():
            for r in rlist:
                uigf_list.append({
                    "gacha_type": str(r.get("gacha_type", ptype)),
                    "time": r.get("time", ""),
                    "name": r.get("name", ""),
                    "item_type": r.get("item_type", "角色" if r.get("qualityLevel", 3) >= 4 else "武器"),
                    "rank_type": str(r.get("qualityLevel", r.get("rank_type", 3))),
                    "id": str(r.get("id", "")),
                    "uigf_gacha_type": str(ptype),
                    "count": "1"
                })
                
        uigf_list.sort(key=lambda x: (x.get("time", ""), x.get("id", "")))
        return {
            "info": {
                "uid": str(player_id),
                "lang": "zh-cn",
                "export_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "export_app": "WutheringWaves_Genshin_Tracker",
                "export_app_version": "2.0.0",
                "uigf_version": "v3.0"
            },
            "list": uigf_list
        }

    def import_uigf(self, uigf_json: Dict[str, Any]) -> Tuple[bool, str, int]:
        """从标准 UIGF JSON 导入数据"""
        info = uigf_json.get("info", {})
        record_list = uigf_json.get("list", [])
        if not record_list:
            return False, "导入的文件中没有找到抽卡记录", 0
            
        uid = str(info.get("uid") or record_list[0].get("uid", "100000001"))
        total_added = 0
        
        # 按卡池分类
        pools_map: Dict[str, List[Dict[str, Any]]] = {}
        for r in record_list:
            ptype = str(r.get("uigf_gacha_type") or r.get("gacha_type", "301"))
            # 角色池 400 合并到 301
            if ptype == "400":
                ptype = "301"
            star = int(r.get("rank_type", 3))
            pools_map.setdefault(ptype, []).append({
                "id": str(r.get("id")),
                "uid": uid,
                "gacha_type": ptype,
                "name": r.get("name", ""),
                "time": r.get("time", ""),
                "item_type": r.get("item_type", "角色" if star >= 4 else "武器"),
                "rank_type": star,
                "qualityLevel": star,
                "resourceType": r.get("item_type", "")
            })
            
        for pt, rlist in pools_map.items():
            total_added += self.merge_records(uid, pt, rlist)
            
        return True, f"成功导入 UID {uid} 的 {total_added} 条新记录！", total_added

    def get_analysis_for_player(self, player_id: Optional[str] = None) -> Dict[str, Any]:
        """获取指定玩家的原神抽卡全面分析报告"""
        players = self.data.get("players", {})
        if not players:
            return {
                "hasData": False,
                "players": [],
                "activePlayer": None,
                "totalPullsAll": 0,
                "totalPrimogems": 0,
                "total5StarAll": 0,
                "globalAvgPity": 0.0,
                "upCharAvgPity": 0.0,
                "upWeaponAvgPity": 0.0,
                "winRate": 55.0,
                "limited5StarCount": 0,
                "standard5StarCount": 0,
                "luckScore": 60,
                "rankTitle": "暂无数据",
                "summaryGrid": [],
                "charactersMatrix": [],
                "pools": {
                    "301": self._analyze_pool("301", [], max_pity=90, soft_pity=74),
                    "302": self._analyze_pool("302", [], max_pity=80, soft_pity=63),
                    "200": self._analyze_pool("200", [], max_pity=90, soft_pity=74),
                    "500": self._analyze_pool("500", [], max_pity=90, soft_pity=74),
                    "100": self._analyze_pool("100", [], max_pity=90, soft_pity=74),
                }
            }
            
        if not player_id or player_id not in players:
            player_id = list(players.keys())[0]
            
        p_data = players[player_id]
        pools = p_data.get("pools", {})
        
        # 角色池 301 与 400 合并统计（双池共享保底）
        char_records = list(pools.get("301", [])) + list(pools.get("400", []))
        char_records.sort(key=lambda x: (x.get("time", ""), str(x.get("id", ""))))
        
        pool_analyses = {}
        # 1. 角色活动祈愿
        pool_analyses["301"] = self._analyze_pool("301", char_records, max_pity=90, soft_pity=74)
        # 2. 武器活动祈愿
        pool_analyses["302"] = self._analyze_pool("302", pools.get("302", []), max_pity=80, soft_pity=63)
        # 3. 常驻祈愿
        pool_analyses["200"] = self._analyze_pool("200", pools.get("200", []), max_pity=90, soft_pity=74)
        # 4. 集录祈愿
        if "500" in pools:
            pool_analyses["500"] = self._analyze_pool("500", pools.get("500", []), max_pity=90, soft_pity=74)
        # 5. 新手祈愿
        if "100" in pools:
            pool_analyses["100"] = self._analyze_pool("100", pools.get("100", []), max_pity=90, soft_pity=74)
            
        # 汇总看板指标（完全按照角色活动池为核心评定）
        char_pool = pool_analyses["301"]
        total_pulls_all = sum(pa.get("totalPulls", 0) for pa in pool_analyses.values())
        total_5star_all = sum(pa.get("fiveStarsCount", 0) for pa in pool_analyses.values())
        
        # 五星图鉴矩阵（角色+武器）
        item_counter = {}
        for pa in pool_analyses.values():
            for g in pa.get("fiveStars", []):
                name = g["name"]
                if name not in item_counter:
                    item_counter[name] = {
                        "name": name,
                        "count": 0,
                        "avatar": g.get("avatar", ""),
                        "isStandard": not g.get("isUp", True),
                        "category": g.get("item_type", "角色")
                    }
                item_counter[name]["count"] += 1
                
        summary_grid = list(item_counter.values())
        summary_grid.sort(key=lambda x: (x["isStandard"], -x["count"]))
                
        # 欧皇评定（原神理论期望 ~93 抽/UP，小保底期望 55%）
        luck_score, rank_title = self._calculate_genshin_luck(char_pool)
        
        all_limited_5star = sum(pa.get("limited5StarCount", 0) for pa in pool_analyses.values())
        all_standard_5star = sum(pa.get("lostCount", 0) for pa in pool_analyses.values())

        return {
            "hasData": True,
            "players": list(players.keys()),
            "activePlayer": player_id,
            "totalPullsAll": total_pulls_all,
            "totalPrimogems": total_pulls_all * 160,
            "total5StarAll": total_5star_all,
            "globalAvgPity": char_pool.get("upCharAvgPity", 0.0),
            "upCharAvgPity": char_pool.get("upCharAvgPity", 0.0),
            "upWeaponAvgPity": pool_analyses.get("302", {}).get("avg5Star", 0.0),
            "winRate": char_pool.get("winRate", 55.0),
            "limited5StarCount": all_limited_5star,
            "standard5StarCount": all_standard_5star,
            "luckScore": luck_score,
            "rankTitle": rank_title,
            "summaryGrid": summary_grid,
            "charactersMatrix": summary_grid,
            "pools": pool_analyses
        }

    def _analyze_pool(self, pool_type: str, records: List[Dict[str, Any]], max_pity: int = 90, soft_pity: int = 74) -> Dict[str, Any]:
        """单卡池分析算法（按时间递增模拟抽卡队列）"""
        total = len(records)
        if total == 0:
            p_name = GENSHIN_POOL_NAMES.get(int(pool_type), "祈愿")
            return {
                "poolType": pool_type,
                "name": p_name,
                "poolName": p_name,
                "totalPulls": 0,
                "currentPity": 0,
                "maxPity": max_pity,
                "remainingPity": max_pity,
                "isGuaranteedNext": False,
                "fiveStarsCount": 0,
                "limited5StarCount": 0,
                "standard5StarCount": 0,
                "lostCount": 0,
                "fourStarsCount": 0,
                "pityCount": 0,
                "pityRemain": max_pity,
                "avg5Star": 0.0,
                "avg4Star": 0.0,
                "avgPity": 0.0,
                "upCharAvgPity": 0.0,
                "winRate": 55.0,
                "luckScore": 60,
                "luckTitle": "平平淡淡才是真",
                "fiveStars": [],
                "goldRecords": [],
                "ranges": ["1-10", "11-50", "51-73", "74-85", "86+"],
                "rangeCounts": [0, 0, 0, 0, 0]
            }
            
        current_pity = 0
        cumulative_pity = 0
        gold_records = []
        count_4star = 0
        
        # 统计小保底胜率
        is_guaranteed = False
        fifty_fifty_total = 0
        fifty_fifty_wins = 0
        
        limited_up_cost_list = []
        limited_up_count = 0
        standard_count = 0
        range_counts = [0, 0, 0, 0, 0]  # 1-10, 11-50, 51-73, 74-85, 86+
        
        for r in records:
            current_pity += 1
            cumulative_pity += 1
            star = int(r.get("qualityLevel", r.get("rank_type", 3)))
            name = r.get("name", "")
            item_type = r.get("item_type", "")
            
            if star == 4:
                count_4star += 1
            elif star == 5:
                is_std = is_genshin_standard_5star(name, item_type)
                if pool_type == "200":  # 常驻池
                    is_std = True
                    
                # 记录区间分布
                if current_pity <= 10:
                    range_counts[0] += 1
                elif current_pity <= 50:
                    range_counts[1] += 1
                elif current_pity <= 73:
                    range_counts[2] += 1
                elif current_pity <= 85:
                    range_counts[3] += 1
                else:
                    range_counts[4] += 1
                    
                lost_5050 = False
                if pool_type == "301":
                    if not is_guaranteed:
                        fifty_fifty_total += 1
                        if not is_std:
                            fifty_fifty_wins += 1
                        else:
                            lost_5050 = True
                    else:
                        is_guaranteed = False
                        
                    if is_std:
                        is_guaranteed = True
                        standard_count += 1
                    else:
                        limited_up_cost_list.append(cumulative_pity)
                        limited_up_count += 1
                        cumulative_pity = 0
                else:
                    if is_std:
                        standard_count += 1
                    else:
                        limited_up_count += 1
                        
                gold_records.append({
                    "name": name,
                    "time": r.get("time", ""),
                    "pity": current_pity,
                    "cumulativePity": cumulative_pity,
                    "standard": is_std,
                    "lost5050": lost_5050,
                    "item_type": item_type,
                    "avatar": get_genshin_avatar_url(name)
                })
                current_pity = 0
                
        # 逆序排列出金流水（最新的在最前）
        gold_records.reverse()
        
        five_count = len(gold_records)
        all_pities = [g["pity"] for g in gold_records]
        avg_pity = round(sum(all_pities) / five_count, 1) if five_count > 0 else 0.0
        up_avg = round(sum(limited_up_cost_list) / len(limited_up_cost_list), 1) if limited_up_cost_list else 0.0
        avg_4star = round(total / count_4star, 1) if count_4star > 0 else 0.0
        
        win_rate = round(fifty_fifty_wins / fifty_fifty_total * 100, 1) if fifty_fifty_total > 0 else 55.0
        
        # 角色活动池只按 UP 算金数，歪的不计入金
        pool_5star_count = limited_up_count if pool_type == "301" else five_count
        pool_avg_5star = up_avg if pool_type == "301" else avg_pity
        
        # 计算单池欧气
        pool_luck_score, pool_luck_title = self._calculate_genshin_luck({
            "limited5StarCount": limited_up_count,
            "upCharAvgPity": pool_avg_5star,
            "winRate": win_rate
        })
        
        # 兼容两种命名方式，保障前端无缝渲染
        five_stars_formatted = []
        for g in gold_records:
            g_name = g["name"]
            is_char = "角色" in g.get("item_type", "角色")
            if is_char:
                c_info = GENSHIN_CHARACTERS_5STAR.get(g_name, {})
                elem = c_info.get("element", "风")
                wpn = c_info.get("weapon", "单手剑")
                cat = "角色"
            else:
                w_info = GENSHIN_WEAPONS_5STAR.get(g_name, {})
                elem = "武器"
                wpn = w_info.get("type", "单手剑")
                cat = "武器"

            five_stars_formatted.append({
                "name": g_name,
                "pity": g["pity"],
                "cumulativePity": g["cumulativePity"],
                "isLost5050": g["lost5050"],
                "isUp": not g["standard"],
                "isStandard": g["standard"],
                "avatar": g["avatar"],
                "time": g["time"],
                "qualityLevel": 5,
                "category": cat,
                "item_type": cat,
                "element": elem,
                "weapon": wpn
            })

        return {
            "poolType": pool_type,
            "name": GENSHIN_POOL_NAMES.get(int(pool_type), "祈愿"),
            "poolName": GENSHIN_POOL_NAMES.get(int(pool_type), "祈愿"),
            "totalPulls": total,
            "currentPity": current_pity,
            "maxPity": max_pity,
            "remainingPity": max(0, max_pity - current_pity),
            "isGuaranteedNext": is_guaranteed if pool_type == "301" else False,
            "fiveStarsCount": pool_5star_count,
            "limited5StarCount": limited_up_count,
            "standard5StarCount": standard_count,
            "lostCount": standard_count,
            "fourStarsCount": count_4star,
            "avg5Star": pool_avg_5star,
            "avg4Star": avg_4star,
            "upCharAvgPity": up_avg,
            "winRate": win_rate,
            "luckScore": pool_luck_score,
            "luckTitle": pool_luck_title,
            "fiveStars": five_stars_formatted,
            "goldRecords": gold_records,
            "ranges": ["1-10", "11-50", "51-73", "74-85", "86+"],
            "rangeCounts": range_counts
        }

    def _calculate_genshin_luck(self, char_pool: Dict[str, Any]) -> Tuple[int, str]:
        """计算原神欧皇指数与评级称号"""
        up_count = char_pool.get("limited5StarCount", 0)
        up_avg = char_pool.get("upCharAvgPity", 0.0)
        win_rate = char_pool.get("winRate", 55.0)
        
        if up_count == 0:
            return 60, "平平淡淡才是真"
            
        # 原神理论期望：不歪率约 55%，单次出金期望约 62.5 抽，每 UP 期望约 93 抽
        diff = 93.0 - up_avg
        base_score = int(55 + (diff * 0.9) + (win_rate - 55.0) * 0.4)
        luck_score = max(5, min(99, base_score))
        
        if luck_score >= 95:
            rank = "终极提瓦特天选欧皇"
        elif luck_score >= 85:
            rank = "十连多金气运之子"
        elif luck_score >= 75:
            rank = "捕获明光常胜将军"
        elif luck_score >= 60:
            rank = "平平淡淡才是真"
        elif luck_score >= 45:
            rank = "小歪怡情略显非酋"
        elif luck_score >= 30:
            rank = "大保底专业户"
        else:
            rank = "地心深渊非酋战神"
            
        return luck_score, rank
