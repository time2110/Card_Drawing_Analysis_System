# -*- coding: utf-8 -*-
"""
鸣潮抽卡分析系统 - 真实模拟演示数据集
"""
from datetime import datetime, timedelta

def generate_demo_records():
    """
    生成一套生动、符合鸣潮概率分布的演示抽卡记录
    """
    base_time = datetime(2024, 7, 1, 12, 0, 0)
    
    # 1. 角色活动唤取（限定角色）
    # 模拟流程：
    # 今汐 (68抽 UP) -> 维里奈 (74抽 歪常驻) -> 长离 (28抽 大保底大欧!) -> 椿 (63抽 UP) -> 当前垫了 38 抽
    char_event_records = []
    
    four_stars = ["散华", "白芷", "炽霞", "秧秧", "丹瑾", "莫特斐", "渊武", "桃祈", "秋水"]
    three_stars = ["穿击枪·改", "源能迅刀·改", "重力佩枪·改", "鸣动音感仪·改", "聚能重刃·改"]

    def add_pull_chain(target_5star, pity_count):
        nonlocal base_time
        for i in range(1, pity_count):
            base_time += timedelta(minutes=2)
            # 每大约 8-10 抽出一个 4 星
            if i % 9 == 0:
                char_event_records.append({
                    "cardPoolType": 1,
                    "resourceId": f"400_{len(char_event_records)}",
                    "resourceType": "角色",
                    "name": four_stars[(len(char_event_records)) % len(four_stars)],
                    "count": 1,
                    "time": base_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "qualityLevel": 4
                })
            else:
                char_event_records.append({
                    "cardPoolType": 1,
                    "resourceId": f"300_{len(char_event_records)}",
                    "resourceType": "武器",
                    "name": three_stars[(len(char_event_records)) % len(three_stars)],
                    "count": 1,
                    "time": base_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "qualityLevel": 3
                })
        
        # 出金
        base_time += timedelta(minutes=5)
        char_event_records.append({
            "cardPoolType": 1,
            "resourceId": f"500_{len(char_event_records)}",
            "resourceType": "角色",
            "name": target_5star,
            "count": 1,
            "time": base_time.strftime("%Y-%m-%d %H:%M:%S"),
            "qualityLevel": 5
        })

    # 添加四次出金过程
    add_pull_chain("今汐", 68)
    base_time += timedelta(days=15)
    add_pull_chain("维里奈", 74)
    base_time += timedelta(days=5)
    add_pull_chain("长离", 28)
    base_time += timedelta(days=40)
    add_pull_chain("椿", 63)
    
    # 之后当前池子垫了 38 抽
    for i in range(1, 39):
        base_time += timedelta(minutes=2)
        if i % 9 == 0:
            char_event_records.append({
                "cardPoolType": 1,
                "resourceId": f"400_pad_{i}",
                "resourceType": "角色",
                "name": four_stars[i % len(four_stars)],
                "count": 1,
                "time": base_time.strftime("%Y-%m-%d %H:%M:%S"),
                "qualityLevel": 4
            })
        else:
            char_event_records.append({
                "cardPoolType": 1,
                "resourceId": f"300_pad_{i}",
                "resourceType": "武器",
                "name": three_stars[i % len(three_stars)],
                "count": 1,
                "time": base_time.strftime("%Y-%m-%d %H:%M:%S"),
                "qualityLevel": 3
            })

    # 2. 武器活动唤取（限定武器）
    # 鸣潮武器池 100% 专武永不歪
    # 时斯如梭 (65抽) -> 裁春 (56抽) -> 当前垫了 22 抽
    weapon_event_records = []
    w_base_time = datetime(2024, 7, 2, 10, 0, 0)
    
    def add_weapon_chain(w_name, pity):
        nonlocal w_base_time
        for i in range(1, pity):
            w_base_time += timedelta(minutes=2)
            star = 4 if i % 8 == 0 else 3
            weapon_event_records.append({
                "cardPoolType": 2,
                "resourceId": f"w_{len(weapon_event_records)}",
                "resourceType": "武器",
                "name": "西升" if star == 4 else "源能佩枪",
                "count": 1,
                "time": w_base_time.strftime("%Y-%m-%d %H:%M:%S"),
                "qualityLevel": star
            })
        w_base_time += timedelta(minutes=5)
        weapon_event_records.append({
            "cardPoolType": 2,
            "resourceId": f"w_5_{len(weapon_event_records)}",
            "resourceType": "武器",
            "name": w_name,
            "count": 1,
            "time": w_base_time.strftime("%Y-%m-%d %H:%M:%S"),
            "qualityLevel": 5
        })
        
    add_weapon_chain("时斯如梭", 65)
    w_base_time += timedelta(days=60)
    add_weapon_chain("裁春", 56)
    
    for i in range(1, 23):
        w_base_time += timedelta(minutes=2)
        weapon_event_records.append({
            "cardPoolType": 2,
            "resourceId": f"w_pad_{i}",
            "resourceType": "武器",
            "name": "西升" if i % 8 == 0 else "源能佩枪",
            "count": 1,
            "time": w_base_time.strftime("%Y-%m-%d %H:%M:%S"),
            "qualityLevel": 4 if i % 8 == 0 else 3
        })

    # 3. 角色常驻唤取
    standard_records = []
    s_base_time = datetime(2024, 6, 15, 8, 0, 0)
    for i in range(1, 76):
        s_base_time += timedelta(minutes=3)
        star = 4 if i % 10 == 0 else 3
        standard_records.append({
            "cardPoolType": 3,
            "resourceId": f"std_{i}",
            "resourceType": "角色" if star == 4 else "武器",
            "name": "散华" if star == 4 else "源能迅刀",
            "count": 1,
            "time": s_base_time.strftime("%Y-%m-%d %H:%M:%S"),
            "qualityLevel": star
        })
    standard_records.append({
        "cardPoolType": 3,
        "resourceId": "std_5_1",
        "resourceType": "角色",
        "name": "安可",
        "count": 1,
        "time": (s_base_time + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "qualityLevel": 5
    })
    # 垫 15 抽
    for i in range(1, 16):
        s_base_time += timedelta(minutes=3)
        standard_records.append({
            "cardPoolType": 3,
            "resourceId": f"std_pad_{i}",
            "resourceType": "武器",
            "name": "源能佩枪",
            "count": 1,
            "time": s_base_time.strftime("%Y-%m-%d %H:%M:%S"),
            "qualityLevel": 3
        })

    return {
        "1": char_event_records,
        "2": weapon_event_records,
        "3": standard_records,
        "4": [],
        "5": []
    }
