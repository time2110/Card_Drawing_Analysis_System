# -*- coding: utf-8 -*-
"""
鸣潮抽卡核心处理模块
负责日志解密、链接提取、接口抓取、数据持久化与统计指标计算
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime
from characters_db import get_item_info, STANDARD_FIVE_STARS

# 卡池类型定义
POOL_NAMES = {
    1: "角色活动唤取",
    2: "武器活动唤取",
    3: "角色常驻唤取",
    4: "武器常驻唤取",
    5: "新手唤取",
    6: "新手自选唤取",
    7: "感恩自选唤取"
}

# 卡池所属分类
POOL_CATEGORIES = {
    1: "character_event",
    2: "weapon_event",
    3: "character_standard",
    4: "weapon_standard",
    5: "novice",
    6: "novice_target",
    7: "gift_target"
}

def decrypt_log_bytes(raw_bytes):
    """
    解密鸣潮 Client.log 字节流
    规则：跳过前3字节，对后续每个字节判断：若最后一位为1异或0xA5，否则异或0xEF
    """
    if len(raw_bytes) < 3:
        return ""
    
    # 检查是否已经是明文
    try:
        sample = raw_bytes[:500].decode('utf-8', errors='ignore')
        if "LogInit" in sample or "Puerts" in sample or "aki-gm-resources" in sample:
            return raw_bytes.decode('utf-8', errors='ignore')
    except Exception:
        pass

    result = bytearray(len(raw_bytes) - 3)
    for i in range(3, len(raw_bytes)):
        b = raw_bytes[i]
        if (b & 1) == 1:
            result[i - 3] = b ^ 0xA5
        else:
            result[i - 3] = b ^ 0xEF
            
    return result.decode('utf-8', errors='ignore')

def extract_gacha_url_from_bytes(raw):
    """从字节流中提取抽卡 URL（自动兼容明文与异或解密，并容错处理 Unicode/HTML 转义）"""
    url_pattern = re.compile(r'https?://[^\s"\'<>]*aki-gm-resources[^\s"\'<>]*')
    text = raw.decode('utf-8', errors='ignore')
    matches = url_pattern.findall(text)
    if not matches:
        text = decrypt_log_bytes(raw)
        matches = url_pattern.findall(text)
    if matches:
        raw_url = matches[-1]
        # 容错处理：虚幻引擎日志或转义文本中可能出现的 \u0026 及 &amp; 统一转为 &
        raw_url = raw_url.replace(r"\u0026", "&").replace("&amp;", "&")
        return raw_url, None
    return None, "日志中未找到抽卡链接。请先在游戏内打开一次【唤取记录】页面后再试。"

def extract_latest_gacha_url(log_file_path):
    """
    从 Client.log 或目录中提取最新的唤取记录 URL，自动支持目录路径及文件路径
    """
    if not log_file_path:
        return None, "日志路径未指定"
    
    target_file = os.path.normpath(log_file_path.strip().strip('"').strip("'"))
    if not os.path.exists(target_file):
        return None, f"未找到指定的文件或目录: {target_file}"

    # 若为目录，自动在其下方寻找 Client.log 或 Client_decoded.log
    if os.path.isdir(target_file):
        candidates = [
            os.path.join(target_file, "Client.log"),
            os.path.join(target_file, "Client_decoded.log")
        ]
        found = None
        for c in candidates:
            if os.path.exists(c):
                found = c
                break
        if not found:
            return None, f"在目录 [{target_file}] 下未找到 Client.log 文件，请确认路径是否正确"
        target_file = found

    try:
        with open(target_file, "rb") as f:
            raw = f.read()
        return extract_gacha_url_from_bytes(raw)
    except Exception as e:
        return None, f"读取日志出错: {str(e)}"

def parse_gacha_url(url_str):
    """
    解析唤取 URL，提取关键鉴权参数及 API 请求地址
    """
    url_str = url_str.strip().replace(r"\u0026", "&").replace("&amp;", "&")
    # 处理 hash 路由中的查询参数
    query_str = ""
    if "?" in url_str:
        query_str = url_str.split("?", 1)[1]
    
    params = urllib.parse.parse_qs(query_str)
    
    # 提取关键字段
    player_id = params.get("player_id", [None])[0]
    svr_id = params.get("svr_id", [None])[0]
    record_id = params.get("record_id", [None])[0]
    resources_id = params.get("resources_id", [None])[0]
    lang = params.get("lang", ["zh-Hans"])[0]
    svr_area = params.get("svr_area", ["global"])[0]
    
    if not player_id or not svr_id:
        return None, "抽卡链接无效：缺少 player_id 或 svr_id 参数"
    
    # 区分国服与国际服
    is_cn = (svr_area == "cn") or ("aki-game.com" in url_str and "-oversea" not in url_str)
    api_base = "https://gmserver-api.aki-game2.com/gacha" if is_cn else "https://gmserver-api.aki-game2.net/gacha"
    api_url = f"{api_base}/record/query"
    
    parsed_info = {
        "apiUrl": api_url,
        "playerId": str(player_id),
        "serverId": str(svr_id),
        "recordId": str(record_id or ""),
        "cardPoolId": str(resources_id or ""),
        "languageCode": lang,
        "svrArea": svr_area,
        "isCn": is_cn,
        "rawUrl": url_str
    }
    return parsed_info, None

def query_official_records(api_info, pool_type):
    """
    向官方接口发起 POST 请求获取指定卡池的抽卡记录
    """
    payload = {
        "playerId": api_info["playerId"],
        "cardPoolId": api_info["cardPoolId"],
        "cardPoolType": int(pool_type),
        "serverId": api_info["serverId"],
        "languageCode": api_info["languageCode"],
        "recordId": api_info["recordId"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept-Language": api_info["languageCode"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    req = urllib.request.Request(
        api_info["apiUrl"],
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    import ssl
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            code = res_data.get("code")
            msg = res_data.get("message", "")
            
            if code == 0 or code == 200 or msg == "成功":
                return res_data.get("data", []) or [], None
            return [], f"接口返回错误 (Code {code}): {msg}"
    except urllib.error.HTTPError as e:
        return [], f"HTTP请求错误: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        # 兼容处理：用户开启网络加速器(如UU/雷神)或系统代理时，自签名证书可能触发 CERTIFICATE_VERIFY_FAILED，自动回退放行
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            try:
                unverified_ctx = ssl.create_default_context()
                unverified_ctx.check_hostname = False
                unverified_ctx.verify_mode = ssl.CERT_NONE
                with urllib.request.urlopen(req, timeout=12, context=unverified_ctx) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    code = res_data.get("code")
                    msg = res_data.get("message", "")
                    if code == 0 or code == 200 or msg == "成功":
                        return res_data.get("data", []) or [], None
                    return [], f"接口返回错误 (Code {code}): {msg}"
            except Exception as retry_err:
                return [], f"网络连接失败 (代理/证书异常): {str(retry_err)}"
        return [], f"网络连接失败: {str(e)}"
    except Exception as e:
        return [], f"网络连接失败: {str(e)}"

class GachaDataManager:
    """
    抽卡数据持久化与统计管理类
    """
    def __init__(self, data_file_path):
        self.data_file = data_file_path
        os.makedirs(os.path.dirname(data_file_path), exist_ok=True)
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"players": {}}

    def load(self):
        """重新从磁盘加载最新数据至内存"""
        self.data = self._load()
        return self.data

    def save(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def merge_records(self, player_id, pool_type, new_records):
        """
        合并抽卡记录，保持完整抽取序列，支持精确去重与追加
        new_records 可为官方接口返回（倒序：最新在前），亦可为全量备份/导出（正序：最旧在前）
        """
        if "players" not in self.data:
            self.data["players"] = {}
            
        pid = str(player_id)
        if pid not in self.data["players"]:
            self.data["players"][pid] = {
                "playerId": pid,
                "lastSyncTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pools": {}
            }
            
        player_pools = self.data["players"][pid]["pools"]
        pt = str(pool_type)
        if pt not in player_pools:
            player_pools[pt] = []
            
        existing = player_pools[pt]
        
        # 智能判定时序：若官方接口返回倒序（最新在前），转为从旧到新的正序；若已是正序（备份文件/数据库导出），保持原样
        chrono_new = list(new_records) if new_records else []
        is_descending = False
        for i in range(len(chrono_new) - 1):
            t_curr = chrono_new[i].get("time", "")
            t_next = chrono_new[i + 1].get("time", "")
            if t_curr and t_next and t_curr != t_next:
                if t_curr > t_next:
                    is_descending = True
                break
        if is_descending:
            chrono_new.reverse()
        
        if not existing:
            player_pools[pt] = chrono_new
            self.data["players"][pid]["lastSyncTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save()
            return len(chrono_new), len(chrono_new)
            
        # 多重集频次差分精确去重算法：
        # 彻底摆脱对同秒内抽取相对顺序的依赖。针对同一时间戳 (如单次十连抽)，统计各物品 (time, name, quality) 的已有频次
        # 无论新记录是正序、倒序或乱序，新记录中某物品的出现次数只有在超过本地已有频次时，才算真正的新增抽卡！
        def get_record_key(r):
            t = str(r.get("time", "")).strip()
            name = str(r.get("name") or r.get("item_name") or "").strip()
            quality = str(r.get("qualityLevel") or r.get("rank_type") or "3").strip()
            return (t, name, quality)

        existing_counts = {}
        for r in existing:
            k = get_record_key(r)
            existing_counts[k] = existing_counts.get(k, 0) + 1

        added = []
        new_seen_counts = {}
        for r in chrono_new:
            k = get_record_key(r)
            new_seen_counts[k] = new_seen_counts.get(k, 0) + 1
            if new_seen_counts[k] > existing_counts.get(k, 0):
                added.append(r)
                
        if added:
            existing.extend(added)
            existing.sort(key=lambda x: x.get("time", ""))
            
        self.data["players"][pid]["lastSyncTime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save()
        return len(added), len(existing)

    def get_analysis_for_player(self, player_id=None):
        """
        计算指定账号（或默认第一个账号）的完整抽卡统计指标
        """
        players = self.data.get("players", {})
        if not players:
            return {
                "hasData": False,
                "players": [],
                "activePlayer": "",
                "lastSyncTime": "未同步",
                "totalPullsAll": 0,
                "total5StarAll": 0,
                "total4StarAll": 0,
                "totalAstrite": 0,
                "pools": {
                    str(p): {
                        "poolType": p,
                        "name": POOL_NAMES.get(p, ""),
                        "totalPulls": 0,
                        "currentPity": 0,
                        "maxPity": 50 if p == 5 else 80,
                        "remainingPity": 50 if p == 5 else 80,
                        "isGuaranteedNext": False,
                        "fiveStarsCount": 0,
                        "fourStarsCount": 0,
                        "avg5Star": 0.0,
                        "avg4Star": 0.0,
                        "luckScore": 50,
                        "luckTitle": "暂无数据",
                        "fiveStars": [],
                        "recordsCount": 0
                    } for p in POOL_NAMES.keys()
                }
            }
            
        if not player_id or str(player_id) not in players:
            player_id = list(players.keys())[0]
            
        p_data = players[str(player_id)]
        pools_data = p_data.get("pools", {})
        
        result_pools = {}
        total_pulls_all = 0
        total_5star_all = 0
        total_4star_all = 0
        
        all_five_stars_list = []
        up_char_pulls = 0
        up_char_count = 0
        up_weapon_pulls = 0
        up_weapon_count = 0
        win_5050_count = 0
        total_5050_count = 0

        for p_type_int, pool_name in POOL_NAMES.items():
            pt_str = str(p_type_int)
            records = pools_data.get(pt_str, [])
            
            # 记录在持久化存储时已是严格正序（从旧到新）
            sorted_records = list(records)
            
            total_pulls = len(sorted_records)
            total_pulls_all += total_pulls
            
            # 遍历计算保底垫刀数与出金列表
            five_stars = []
            four_stars = []
            current_pity = 0
            accumulated_pity = 0
            current_4star_pity = 0
            
            # 用于记录上一个五星是否为常驻
            last_was_standard = False
            
            for item in sorted_records:
                current_pity += 1
                accumulated_pity += 1
                current_4star_pity += 1
                star = int(item.get("qualityLevel", 3))
                raw_name = item.get("name", "")
                item_meta = get_item_info(raw_name, star, item.get("resourceType"), item.get("resourceId"))
                real_name = item_meta["name"]
                
                if star == 5:
                    is_standard = item_meta["isStandard"]
                    is_lost_5050 = False
                    is_guaranteed = False
                    item_cumulative_pity = current_pity
                    
                    if p_type_int == 1: # 限定角色池
                        if is_standard:
                            is_lost_5050 = True
                            last_was_standard = True
                            total_5050_count += 1
                            item_cumulative_pity = current_pity
                            # 歪常驻不重置 accumulated_pity，抽数继续累加到下一个 UP
                        else:
                            is_guaranteed = last_was_standard
                            if not last_was_standard:
                                win_5050_count += 1
                                total_5050_count += 1
                            last_was_standard = False
                            up_char_count += 1
                            item_cumulative_pity = accumulated_pity
                            accumulated_pity = 0 # 获得 UP 角色后重置累计花费抽数
                            
                    elif p_type_int == 2: # 限定武器池
                        if not is_standard:
                            up_weapon_count += 1
                        accumulated_pity = 0
                    else:
                        accumulated_pity = 0
                            
                    f_info = {
                        "name": real_name,
                        "star": 5,
                        "element": item_meta.get("element", "常规"),
                        "elementColor": item_meta.get("elementColor", "#facc15"),
                        "elementBg": item_meta.get("elementBg", ""),
                        "avatar": item_meta.get("avatar", ""),
                        "category": item_meta.get("category", "角色"),
                        "weapon": item_meta.get("weapon", ""),
                        "time": item.get("time", ""),
                        "pity": current_pity,
                        "cumulativePity": item_cumulative_pity,
                        "isStandard": is_standard,
                        "isLost5050": is_lost_5050,
                        "isGuaranteed": is_guaranteed,
                        "isUp": item_meta.get("isUp", False),
                        "poolType": p_type_int
                    }
                    five_stars.append(f_info)
                    all_five_stars_list.append(f_info)
                    total_5star_all += 1
                    current_pity = 0 # 重置单次出金水位
                    
                elif star == 4:
                    four_stars.append({
                        "name": real_name,
                        "star": 4,
                        "element": item_meta.get("element", "常规"),
                        "elementColor": item_meta.get("elementColor", "#c084fc"),
                        "avatar": item_meta.get("avatar", ""),
                        "time": item.get("time", ""),
                        "pity": current_4star_pity
                    })
                    total_4star_all += 1
                    current_4star_pity = 0
            
            # 计算平均抽数：歪的不计入金，角色活动池只按获得的 UP 限定角色计算均抽与金数
            if p_type_int == 1:
                up_fives = [f for f in five_stars if f.get("isUp")]
                lost_fives = [f for f in five_stars if f.get("isLost5050")]
                effective_pulls = total_pulls - current_pity
                avg_5star = round(effective_pulls / len(up_fives), 1) if up_fives else 0.0
                pool_five_count = len(up_fives) # 歪的不计入金，只算 UP 金数
                pool_lost_count = len(lost_fives)
            else:
                avg_5star = round(sum(f["pity"] for f in five_stars) / len(five_stars), 1) if five_stars else 0.0
                pool_five_count = len(five_stars)
                pool_lost_count = 0
                
            avg_4star = round(sum(f["pity"] for f in four_stars) / len(four_stars), 1) if four_stars else 0.0
            
            # 计算单池欧气指数 (0-100)
            luck_score, luck_title = calculate_luck_score(five_stars, avg_5star, p_type_int)
            
            # 保底上限（常规为80，新手池为50）
            max_pity = 50 if p_type_int == 5 else 80
            
            # 格式化出金历史展示列表（倒序显示最新出金在前）
            five_stars_display = list(reversed(five_stars))
            
            result_pools[pt_str] = {
                "poolType": p_type_int,
                "name": pool_name,
                "totalPulls": total_pulls,
                "currentPity": current_pity,
                "maxPity": max_pity,
                "remainingPity": max(0, max_pity - current_pity),
                "isGuaranteedNext": last_was_standard if p_type_int == 1 else False,
                "fiveStarsCount": pool_five_count,
                "lostCount": pool_lost_count,
                "rawFiveStarsCount": len(five_stars),
                "fourStarsCount": len(four_stars),
                "avg5Star": avg_5star,
                "avg4Star": avg_4star,
                "luckScore": luck_score,
                "luckTitle": luck_title,
                "fiveStars": five_stars_display,
                "recordsCount": len(sorted_records)
            }

        # 汇总全局五星与展示图鉴列表
        limited_5star_count = sum(1 for f in all_five_stars_list if not f["isStandard"])
        standard_5star_count = sum(1 for f in all_five_stars_list if f["isStandard"])
        
        # 统计每个五星的数量与头像（用于顶栏头像网格）
        summary_dict = {}
        for f in all_five_stars_list:
            nm = f["name"]
            if nm not in summary_dict:
                summary_dict[nm] = {
                    "name": nm,
                    "avatar": f["avatar"],
                    "isStandard": f["isStandard"],
                    "category": f["category"],
                    "count": 0
                }
            summary_dict[nm]["count"] += 1
            
        # 限定排前面，常驻排后面
        summary_grid = sorted(summary_dict.values(), key=lambda x: (x["isStandard"], -x["count"]))
        
        # 小保底不歪率
        win_rate = round((win_5050_count / total_5050_count) * 100, 1) if total_5050_count > 0 else 50.0
        
        # 计算每UP角色所需抽数 (限定角色池有效消耗抽数 / UP角色数量)
        up_char_avg_pity = round((result_pools.get("1", {}).get("totalPulls", 0) - result_pools.get("1", {}).get("currentPity", 0)) / up_char_count, 1) if up_char_count > 0 else 0.0
        # 计算每UP武器所需抽数 (限定武器池有效消耗抽数 / UP武器数量)
        up_weapon_avg_pity = round((result_pools.get("2", {}).get("totalPulls", 0) - result_pools.get("2", {}).get("currentPity", 0)) / up_weapon_count, 1) if up_weapon_count > 0 else 0.0

        # 综合欧皇指数：只计算角色活动池抽取，且歪的不计入金
        char_pool = result_pools.get("1", {})
        char_pool_pulls = char_pool.get("totalPulls", 0)
        char_up_count = char_pool.get("fiveStarsCount", 0)
        char_avg_pity = char_pool.get("avg5Star", 0.0)
        
        if char_up_count > 0:
            if char_avg_pity <= 55 and win_rate >= 50:
                rank_title = "终极无敌至尊欧皇"
                tags = ["天选之子", "一发入魂", "极速出金", "从未歪过"]
            elif char_avg_pity <= 75:
                rank_title = "大吉大利·欧气充沛"
                tags = ["抽卡锦鲤", "运势亨通", "平稳出金", "极少歪卡"]
            elif char_avg_pity <= 95:
                rank_title = "平平淡淡·凡骨真仙"
                tags = ["修仙得道", "理性抽卡", "概率正常", "常规保底"]
            elif char_avg_pity <= 115:
                rank_title = "稍显波折·常驻之友"
                tags = ["常驻喜加一", "稍显坎坷", "越挫越勇", "蓄力待发"]
            else:
                rank_title = "逆风翻盘·大保底战士"
                tags = ["保底战神", "硬核吃保底", "必出大保底", "底力深厚"]
        else:
            if char_pool_pulls > 0:
                rank_title = "蓄力待发·等待首金"
                tags = ["潜龙在渊", "厚积薄发", "静待花开", "下次必出"]
            else:
                rank_title = "暂无角色活动数据"
                tags = ["暂未抽卡", "备战新池", "积攒星声", "蓄势待发"]
            
        featured_avatar = summary_grid[0]["avatar"] if summary_grid else ""

        return {
            "hasData": True,
            "players": list(players.keys()),
            "activePlayer": str(player_id),
            "lastSyncTime": p_data.get("lastSyncTime", ""),
            "totalPullsAll": total_pulls_all,
            "total5StarAll": total_5star_all,
            "total4StarAll": total_4star_all,
            "totalAstrite": total_pulls_all * 160,
            "limited5StarCount": limited_5star_count,
            "standard5StarCount": standard_5star_count,
            "charPoolPulls": char_pool_pulls,
            "charPoolUpCount": char_up_count,
            "summaryGrid": summary_grid,
            "winRate": win_rate,
            "upCharAvgPity": up_char_avg_pity,
            "upWeaponAvgPity": up_weapon_avg_pity,
            "globalAvgPity": char_avg_pity if char_up_count > 0 else 0.0,
            "rankTitle": rank_title,
            "tags": tags,
            "featuredAvatar": featured_avatar,
            "pools": result_pools
        }

def calculate_luck_score(five_stars, avg_pity, pool_type):
    """
    根据出金平均抽数与歪卡情况计算运气评分
    """
    if not five_stars:
        return 50, "暂无出金数据"
        
    if pool_type == 1:
        # 限定角色池：歪的不计入金，基于每 UP 抽数 (数学期望 93 抽) 与小保底不歪率进行评定
        up_fives = [f for f in five_stars if f.get("isUp")]
        lost_fives = [f for f in five_stars if f.get("isLost5050")]
        
        if not up_fives:
            return 30, "未出UP角色"
            
        win_ratio = len(up_fives) / (len(up_fives) + len(lost_fives)) if (up_fives or lost_fives) else 0.5
        
        # 数学期望 93 抽/UP。若平均 60 抽对应 ~80 分，50 抽对应 ~90 分，120 抽对应 ~30 分
        base = 100 - (avg_pity / 140.0) * 70
        base += (win_ratio - 0.5) * 30
        score = int(max(5, min(99, base)))
        
        if score >= 85:
            title = "欧皇转世 (顶尖欧气)"
        elif score >= 70:
            title = "大吉大利 (欧气充沛)"
        elif score >= 50:
            title = "平平淡淡 (正常概率)"
        elif score >= 35:
            title = "稍显波折 (有点偏非)"
        else:
            title = "非酋体质 (大保底战士)"
            
        return score, title
    else:
        # 其他卡池按常规 62 抽期望评估
        base = 100 - (avg_pity / 80.0) * 80
        score = int(max(5, min(99, base)))
        if score >= 85:
            title = "欧气爆棚"
        elif score >= 70:
            title = "运势良好"
        elif score >= 50:
            title = "正常概率"
        elif score >= 35:
            title = "偏非体质"
        else:
            title = "保底吃满"
        return score, title

def normalize_imported_records(raw_data, default_uid="802084356"):
    """
    智能解析并规范化来自各类第三方工具（鸣潮工坊、UIGF、Astrionyx、原生备份等）的抽卡记录
    返回: { uid: { pool_type_str: [ standard_record, ... ] } }
    """
    from characters_db import ID_MAP, ALIAS_MAP
    
    result = {}

    def clean_record(r, default_pool="1"):
        p_type = str(r.get("cardPoolType") or r.get("card_pool_type") or r.get("gacha_type") or r.get("poolType") or default_pool)
        raw_name = str(r.get("name") or r.get("item_name") or "").strip()
        res_id = r.get("resourceId") or r.get("resource_id") or r.get("item_id")
        
        # 依据 ID 校正角色/武器名
        if res_id:
            try:
                res_id_int = int(res_id)
                if res_id_int in ID_MAP:
                    raw_name = ID_MAP[res_id_int]
            except (ValueError, TypeError):
                pass
        
        name = ALIAS_MAP.get(raw_name, raw_name)
        
        quality = r.get("qualityLevel") or r.get("quality_level") or r.get("rank_type") or 3
        try:
            quality = int(quality)
        except (ValueError, TypeError):
            quality = 3
            
        res_type = r.get("resourceType") or r.get("resource_type") or r.get("item_type") or ("角色" if quality >= 4 else "武器")
        time_str = str(r.get("time") or r.get("timestamp") or "").strip()
        
        return p_type, {
            "cardPoolType": int(p_type) if p_type.isdigit() else 1,
            "resourceId": res_id or "",
            "name": name,
            "resourceType": res_type,
            "qualityLevel": quality,
            "time": time_str
        }

    # 情况 1: 本地原生格式
    if isinstance(raw_data, dict) and "players" in raw_data:
        for pid, pdata in raw_data["players"].items():
            result[str(pid)] = {}
            for pt, rlist in pdata.get("pools", {}).items():
                result[str(pid)][str(pt)] = [clean_record(r, pt)[1] for r in rlist if isinstance(r, dict)]
        return result

    # 情况 2: UIGF 格式 (含 info 与 list)
    if isinstance(raw_data, dict) and ("info" in raw_data or "list" in raw_data or "records" in raw_data):
        info = raw_data.get("info", {})
        uid = str(info.get("uid") or raw_data.get("uid") or default_uid)
        items = raw_data.get("list") or raw_data.get("records") or raw_data.get("data") or []
        result[uid] = {}
        for item in items:
            if isinstance(item, dict):
                pt, rec = clean_record(item)
                if pt not in result[uid]:
                    result[uid][pt] = []
                result[uid][pt].append(rec)
        return result

    # 情况 3: 纯列表
    if isinstance(raw_data, list):
        uid = default_uid
        result[uid] = {}
        for item in raw_data:
            if isinstance(item, dict):
                pt, rec = clean_record(item)
                if pt not in result[uid]:
                    result[uid][pt] = []
                result[uid][pt].append(rec)
        return result

    # 情况 4: 以卡池 ID 为 key 的字典 { "1": [...], "2": [...] }
    if isinstance(raw_data, dict):
        uid = str(raw_data.get("uid") or default_uid)
        result[uid] = {}
        for k, v in raw_data.items():
            if str(k).isdigit() and isinstance(v, list):
                result[uid][str(k)] = [clean_record(r, k)[1] for r in v if isinstance(r, dict)]
        if result[uid]:
            return result

    return result

