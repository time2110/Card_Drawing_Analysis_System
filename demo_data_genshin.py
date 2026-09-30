# -*- coding: utf-8 -*-
"""
原神抽卡演示数据生成器 (Demo Data for Genshin Impact)
"""

def generate_genshin_demo_records():
    """生成真实的演示抽卡数据（包含欧皇提前出金、歪常驻、大保底等典型场景）"""
    records_301 = []
    
    # 模拟角色活动池
    # 1. 钟离 (第 76 抽，小保底不歪)
    for i in range(75):
        records_301.append({
            "id": f"100010001000{i:03d}",
            "uid": "10086888 (演示)",
            "gacha_type": "301",
            "name": "弹弓" if i % 10 != 0 else "行秋",
            "time": f"2024-01-01 12:{i%60:02d}:00",
            "item_type": "武器" if i % 10 != 0 else "角色",
            "rank_type": 3 if i % 10 != 0 else 4,
            "qualityLevel": 3 if i % 10 != 0 else 4
        })
    records_301.append({
        "id": "100010001000076",
        "uid": "10086888 (演示)",
        "gacha_type": "301",
        "name": "钟离",
        "time": "2024-01-01 12:59:00",
        "item_type": "角色",
        "rank_type": 5,
        "qualityLevel": 5
    })
    
    # 2. 琴 (第 35 抽，小保底歪常驻)
    for i in range(34):
        records_301.append({
            "id": f"100010002000{i:03d}",
            "uid": "10086888 (演示)",
            "gacha_type": "301",
            "name": "黎明神剑" if i % 10 != 0 else "香菱",
            "time": f"2024-02-01 14:{i%60:02d}:00",
            "item_type": "武器" if i % 10 != 0 else "角色",
            "rank_type": 3 if i % 10 != 0 else 4,
            "qualityLevel": 3 if i % 10 != 0 else 4
        })
    records_301.append({
        "id": "100010002000035",
        "uid": "10086888 (演示)",
        "gacha_type": "301",
        "name": "琴",
        "time": "2024-02-01 14:40:00",
        "item_type": "角色",
        "rank_type": 5,
        "qualityLevel": 5
    })
    
    # 3. 芙宁娜 (第 78 抽，大保底拿下)
    for i in range(77):
        records_301.append({
            "id": f"100010003000{i:03d}",
            "uid": "10086888 (演示)",
            "gacha_type": "301",
            "name": "神射手之誓" if i % 10 != 0 else "夏洛蒂",
            "time": f"2024-03-01 18:{i%60:02d}:00",
            "item_type": "武器" if i % 10 != 0 else "角色",
            "rank_type": 3 if i % 10 != 0 else 4,
            "qualityLevel": 3 if i % 10 != 0 else 4
        })
    records_301.append({
        "id": "100010003000078",
        "uid": "10086888 (演示)",
        "gacha_type": "301",
        "name": "芙宁娜",
        "time": "2024-03-01 19:20:00",
        "item_type": "角色",
        "rank_type": 5,
        "qualityLevel": 5
    })
    
    # 4. 希诺宁 (第 12 抽，极速双黄单抽欧皇)
    for i in range(11):
        records_301.append({
            "id": f"100010004000{i:03d}",
            "uid": "10086888 (演示)",
            "gacha_type": "301",
            "name": "黑缨枪",
            "time": f"2024-10-10 10:{i%60:02d}:00",
            "item_type": "武器",
            "rank_type": 3,
            "qualityLevel": 3
        })
    records_301.append({
        "id": "100010004000012",
        "uid": "10086888 (演示)",
        "gacha_type": "301",
        "name": "希诺宁",
        "time": "2024-10-10 10:15:00",
        "item_type": "角色",
        "rank_type": 5,
        "qualityLevel": 5
    })
    
    # 垫抽 28 抽
    for i in range(28):
        records_301.append({
            "id": f"100010005000{i:03d}",
            "uid": "10086888 (演示)",
            "gacha_type": "301",
            "name": "白缨枪" if i % 10 != 0 else "班尼特",
            "time": f"2024-10-20 20:{i%60:02d}:00",
            "item_type": "武器" if i % 10 != 0 else "角色",
            "rank_type": 3 if i % 10 != 0 else 4,
            "qualityLevel": 3 if i % 10 != 0 else 4
        })

    # 武器池 302
    records_302 = []
    # 静水流涌之辉 (第 66 抽拿下)
    for i in range(65):
        records_302.append({
            "id": f"200010001000{i:03d}",
            "uid": "10086888 (演示)",
            "gacha_type": "302",
            "name": "以理服人" if i % 10 != 0 else "西风剑",
            "time": f"2024-03-02 12:{i%60:02d}:00",
            "item_type": "武器",
            "rank_type": 3 if i % 10 != 0 else 4,
            "qualityLevel": 3 if i % 10 != 0 else 4
        })
    records_302.append({
        "id": "200010001000066",
        "uid": "10086888 (演示)",
        "gacha_type": "302",
        "name": "静水流涌之辉",
        "time": "2024-03-02 12:45:00",
        "item_type": "武器",
        "rank_type": 5,
        "qualityLevel": 5
    })

    # 常驻池 200
    records_200 = []
    for i in range(78):
        records_200.append({
            "id": f"300010001000{i:03d}",
            "uid": "10086888 (演示)",
            "gacha_type": "200",
            "name": "翡玉法球",
            "time": f"2023-12-01 10:{i%60:02d}:00",
            "item_type": "武器",
            "rank_type": 3,
            "qualityLevel": 3
        })
    records_200.append({
        "id": "300010001000079",
        "uid": "10086888 (演示)",
        "gacha_type": "200",
        "name": "莫娜",
        "time": "2023-12-01 10:55:00",
        "item_type": "角色",
        "rank_type": 5,
        "qualityLevel": 5
    })

    return {
        "301": records_301,
        "302": records_302,
        "200": records_200
    }
