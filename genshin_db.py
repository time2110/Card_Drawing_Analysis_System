# -*- coding: utf-8 -*-
"""
原神角色与武器数据库 (Genshin Impact Database)
包含全 5★ 角色、5★ 武器、4★ 角色/武器的详细信息、常驻标记与头像资源
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
GENSHIN_CONFIG_PATH = os.path.join(BASE_DIR, "data", "genshin_custom_config.json")

# 原神卡池类型映射 (官方 gacha_type)
GENSHIN_POOL_NAMES = {
    301: "角色活动祈愿",
    400: "角色活动祈愿-2",
    302: "武器活动祈愿",
    200: "常驻祈愿",
    500: "集录祈愿",
    100: "新手祈愿"
}

# 原神常驻五星角色 (在角色限定池中抽到代表“歪”)
GENSHIN_STANDARD_5STAR_CHARS = {
    "琴", "迪卢克", "莫娜", "七七", "刻晴", "提纳里", "迪希雅"
}

# 原神常驻五星武器 (在限定武器池中抽到代表“歪”)
GENSHIN_STANDARD_5STAR_WEAPONS = {
    "天空之刃", "风鹰剑",
    "天空之傲", "狼的末路",
    "天空之脊", "和璞鸢",
    "天空之卷", "四风原典",
    "天空之翼", "阿莫斯之弓"
}

# 头像与武器 CDN (首选 Enka Network 全版本解包 CDN，支持 1.0 ~ 5.x 全角色/武器)
CHAR_AVATAR_BASE = "https://enka.network/ui"
WEAPON_AVATAR_BASE = "https://enka.network/ui"
BBS_CHAR_AVATAR_BASE = "https://upload-bbs.mihoyo.com/game_record/genshin/character_icon"
BBS_WEAPON_AVATAR_BASE = "https://upload-bbs.mihoyo.com/game_record/genshin/equip"

# 五星角色数据库
# 包含：元素、武器类型、是否常驻、英文Icon名称
GENSHIN_CHARACTERS_5STAR = {
    # 常驻 7 虎
    "琴": {"element": "风", "weapon": "单手剑", "standard": True, "icon": "UI_AvatarIcon_Qin.png"},
    "迪卢克": {"element": "火", "weapon": "双手剑", "standard": True, "icon": "UI_AvatarIcon_Diluc.png"},
    "莫娜": {"element": "水", "weapon": "法器", "standard": True, "icon": "UI_AvatarIcon_Mona.png"},
    "七七": {"element": "冰", "weapon": "单手剑", "standard": True, "icon": "UI_AvatarIcon_Qiqi.png"},
    "刻晴": {"element": "雷", "weapon": "单手剑", "standard": True, "icon": "UI_AvatarIcon_Keqing.png"},
    "提纳里": {"element": "草", "weapon": "弓", "standard": True, "icon": "UI_AvatarIcon_Tighnari.png"},
    "迪希雅": {"element": "火", "weapon": "双手剑", "standard": True, "icon": "UI_AvatarIcon_Dehya.png"},

    # 1.x 时代
    "温迪": {"element": "风", "weapon": "弓", "standard": False, "icon": "UI_AvatarIcon_Venti.png"},
    "可莉": {"element": "火", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Klee.png"},
    "达达利亚": {"element": "水", "weapon": "弓", "standard": False, "icon": "UI_AvatarIcon_Tartaglia.png"},
    "钟离": {"element": "岩", "weapon": "长柄武器", "standard": False, "icon": "UI_AvatarIcon_Zhongli.png"},
    "阿贝多": {"element": "岩", "weapon": "单手剑", "standard": False, "icon": "UI_AvatarIcon_Albedo.png"},
    "甘雨": {"element": "冰", "weapon": "弓", "standard": False, "icon": "UI_AvatarIcon_Ganyu.png"},
    "魈": {"element": "风", "weapon": "长柄武器", "standard": False, "icon": "UI_AvatarIcon_Xiao.png"},
    "胡桃": {"element": "火", "weapon": "长柄武器", "standard": False, "icon": "UI_AvatarIcon_Hutao.png"},
    "优菈": {"element": "冰", "weapon": "双手剑", "standard": False, "icon": "UI_AvatarIcon_Eula.png"},

    # 2.x 时代 (稻妻)
    "枫原万叶": {"element": "风", "weapon": "单手剑", "standard": False, "icon": "UI_AvatarIcon_Kazuha.png"},
    "神里绫华": {"element": "冰", "weapon": "单手剑", "standard": False, "icon": "UI_AvatarIcon_Ayaka.png"},
    "宵宫": {"element": "火", "weapon": "弓", "standard": False, "icon": "UI_AvatarIcon_Yoimiya.png"},
    "雷电将军": {"element": "雷", "weapon": "长柄武器", "standard": False, "icon": "UI_AvatarIcon_Shougun.png"},
    "珊瑚宫心海": {"element": "水", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Kokomi.png"},
    "荒泷一斗": {"element": "岩", "weapon": "双手剑", "standard": False, "icon": "UI_AvatarIcon_Itto.png"},
    "申鹤": {"element": "冰", "weapon": "长柄武器", "standard": False, "icon": "UI_AvatarIcon_Shenhe.png"},
    "八重神子": {"element": "雷", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Yae.png"},
    "神里绫人": {"element": "水", "weapon": "单手剑", "standard": False, "icon": "UI_AvatarIcon_Ayato.png"},
    "夜兰": {"element": "水", "weapon": "弓", "standard": False, "icon": "UI_AvatarIcon_Yelan.png"},

    # 3.x 时代 (须弥)
    "赛诺": {"element": "雷", "weapon": "长柄武器", "standard": False, "icon": "UI_AvatarIcon_Cyno.png"},
    "妮露": {"element": "水", "weapon": "单手剑", "standard": False, "icon": "UI_AvatarIcon_Nilou.png"},
    "纳西妲": {"element": "草", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Nahida.png"},
    "流浪者": {"element": "风", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Wanderer.png"},
    "艾尔海森": {"element": "草", "weapon": "单手剑", "standard": False, "icon": "UI_AvatarIcon_Alhatham.png"},
    "白术": {"element": "草", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Baizhuer.png"},

    # 4.x 时代 (枫丹)
    "林尼": {"element": "火", "weapon": "弓", "standard": False, "icon": "UI_AvatarIcon_Liney.png"},
    "那维莱特": {"element": "水", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Neuvillette.png"},
    "莱欧斯利": {"element": "冰", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Wriothesley.png"},
    "芙宁娜": {"element": "水", "weapon": "单手剑", "standard": False, "icon": "UI_AvatarIcon_Furina.png"},
    "娜维娅": {"element": "岩", "weapon": "双手剑", "standard": False, "icon": "UI_AvatarIcon_Navia.png"},
    "闲云": {"element": "风", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Liuyun.png"},
    "千织": {"element": "岩", "weapon": "单手剑", "standard": False, "icon": "UI_AvatarIcon_Chiori.png"},
    "阿蕾奇诺": {"element": "火", "weapon": "长柄武器", "standard": False, "icon": "UI_AvatarIcon_Arlecchino.png"},
    "克洛琳德": {"element": "雷", "weapon": "单手剑", "standard": False, "icon": "UI_AvatarIcon_Clorinde.png"},
    "希格雯": {"element": "水", "weapon": "弓", "standard": False, "icon": "UI_AvatarIcon_Sigewinne.png"},
    "艾梅莉埃": {"element": "草", "weapon": "长柄武器", "standard": False, "icon": "UI_AvatarIcon_Emilie.png"},

    # 5.x ~ 7.x 时代
    "玛拉妮": {"element": "水", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Mualani.png"},
    "基尼奇": {"element": "草", "weapon": "双手剑", "standard": False, "icon": "UI_AvatarIcon_Kinich.png"},
    "希诺宁": {"element": "岩", "weapon": "单手剑", "standard": False, "icon": "UI_AvatarIcon_Xilonen.png"},
    "恰斯卡": {"element": "风", "weapon": "弓", "standard": False, "icon": "UI_AvatarIcon_Chasca.png"},
    "茜特菈莉": {"element": "冰", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Citlali.png"},
    "玛薇卡": {"element": "火", "weapon": "双手剑", "standard": False, "icon": "UI_AvatarIcon_Mavuika.png"},
    "沃雅妮莎": {"element": "水", "weapon": "法器", "standard": False, "icon": "UI_AvatarIcon_Vodyanitsa.png", "avatar": "/images/avatars/UI_AvatarIcon_Vodyanitsa.png"},

    # 联动/特殊
    "埃洛伊": {"element": "冰", "weapon": "弓", "standard": True, "icon": "UI_AvatarIcon_Aloy.png"}
}

# 五星武器数据库
GENSHIN_WEAPONS_5STAR = {
    # 单手剑
    "风鹰剑": {"type": "单手剑", "standard": True, "icon": "UI_EquipIcon_Sword_Falcon.png"},
    "天空之刃": {"type": "单手剑", "standard": True, "icon": "UI_EquipIcon_Sword_Dvalin.png"},
    "斫峰之刃": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Kunwu.png"},
    "磐岩结绿": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Morax.png"},
    "苍古自由之誓": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Widsith.png"},
    "雾切之回光": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Narukami.png"},
    "波乱月白经津": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Amenoma.png"},
    "圣显之钥": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Deshret.png"},
    "裁叶萃光": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Ayus.png"},
    "静水流涌之辉": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Regalis.png"},
    "有乐御簾切": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Urakusai.png"},
    "赦罪": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Estoc.png"},
    "岩峰巡歌": {"type": "单手剑", "standard": False, "icon": "UI_EquipIcon_Sword_Pact.png"},

    # 双手剑
    "天空之傲": {"type": "双手剑", "standard": True, "icon": "UI_EquipIcon_Claymore_Dvalin.png"},
    "狼的末路": {"type": "双手剑", "standard": True, "icon": "UI_EquipIcon_Claymore_Wolfmound.png"},
    "无工之剑": {"type": "双手剑", "standard": False, "icon": "UI_EquipIcon_Claymore_Kunwu.png"},
    "松籁响起之时": {"type": "双手剑", "standard": False, "icon": "UI_EquipIcon_Claymore_Widsith.png"},
    "赤角石溃杵": {"type": "双手剑", "standard": False, "icon": "UI_EquipIcon_Claymore_Itto.png"},
    "苇海信标": {"type": "双手剑", "standard": False, "icon": "UI_EquipIcon_Claymore_Deshret.png"},
    "裁断": {"type": "双手剑", "standard": False, "icon": "UI_EquipIcon_Claymore_GoldenHornet.png"},
    "山王长牙": {"type": "双手剑", "standard": False, "icon": "UI_EquipIcon_Claymore_Mountain.png"},

    # 长柄武器
    "天空之脊": {"type": "长柄武器", "standard": True, "icon": "UI_EquipIcon_Pole_Dvalin.png"},
    "和璞鸢": {"type": "长柄武器", "standard": True, "icon": "UI_EquipIcon_Pole_Morax.png"},
    "贯虹之槊": {"type": "长柄武器", "standard": False, "icon": "UI_EquipIcon_Pole_Kunwu.png"},
    "护摩之杖": {"type": "长柄武器", "standard": False, "icon": "UI_EquipIcon_Pole_Homa.png"},
    "薙草之稻光": {"type": "长柄武器", "standard": False, "icon": "UI_EquipIcon_Pole_Narukami.png"},
    "息灾": {"type": "长柄武器", "standard": False, "icon": "UI_EquipIcon_Pole_Santika.png"},
    "赤沙之杖": {"type": "长柄武器", "standard": False, "icon": "UI_EquipIcon_Pole_Deshret.png"},
    "赤月之形": {"type": "长柄武器", "standard": False, "icon": "UI_EquipIcon_Pole_BloodMoon.png"},

    # 法器
    "天空之卷": {"type": "法器", "standard": True, "icon": "UI_EquipIcon_Catalyst_Dvalin.png"},
    "四风原典": {"type": "法器", "standard": True, "icon": "UI_EquipIcon_Catalyst_FourWinds.png"},
    "尘世之锁": {"type": "法器", "standard": False, "icon": "UI_EquipIcon_Catalyst_Kunwu.png"},
    "不灭月华": {"type": "法器", "standard": False, "icon": "UI_EquipIcon_Catalyst_Kaleido.png"},
    "神乐之真意": {"type": "法器", "standard": False, "icon": "UI_EquipIcon_Catalyst_Narukami.png"},
    "千夜浮梦": {"type": "法器", "standard": False, "icon": "UI_EquipIcon_Catalyst_Ayus.png"},
    "碧落之珑": {"type": "法器", "standard": False, "icon": "UI_EquipIcon_Catalyst_Baizhuer.png"},
    "金流监督": {"type": "法器", "standard": False, "icon": "UI_EquipIcon_Catalyst_Wheatley.png"},
    "万世流涌大典": {"type": "法器", "standard": False, "icon": "UI_EquipIcon_Catalyst_Iudex.png"},
    "鹤鸣余音": {"type": "法器", "standard": False, "icon": "UI_EquipIcon_Catalyst_Crane.png"},
    "冲浪时光": {"type": "法器", "standard": False, "icon": "UI_EquipIcon_Catalyst_Mualani.png"},

    # 弓
    "天空之翼": {"type": "弓", "standard": True, "icon": "UI_EquipIcon_Bow_Dvalin.png"},
    "阿莫斯之弓": {"type": "弓", "standard": True, "icon": "UI_EquipIcon_Bow_Amos.png"},
    "终末嗟叹之诗": {"type": "弓", "standard": False, "icon": "UI_EquipIcon_Bow_Widsith.png"},
    "飞雷之弦振": {"type": "弓", "standard": False, "icon": "UI_EquipIcon_Bow_Narukami.png"},
    "冬极白星": {"type": "弓", "standard": False, "icon": "UI_EquipIcon_Bow_Worldbane.png"},
    "若水": {"type": "弓", "standard": False, "icon": "UI_EquipIcon_Bow_Kirin.png"},
    "猎人之径": {"type": "弓", "standard": False, "icon": "UI_EquipIcon_Bow_Ayus.png"},
    "最初的大魔术": {"type": "弓", "standard": False, "icon": "UI_EquipIcon_Bow_Pledge.png"},
    "白雨心弦": {"type": "弓", "standard": False, "icon": "UI_EquipIcon_Bow_Heartstring.png"},
    "星鹫赤羽": {"type": "弓", "standard": False, "icon": "UI_EquipIcon_Bow_Chasca.png"}
}

# 常用四星角色表
GENSHIN_CHARACTERS_4STAR = {
    "香菱": {"element": "火", "weapon": "长柄武器", "icon": "UI_AvatarIcon_Xiangling.png"},
    "行秋": {"element": "水", "weapon": "单手剑", "icon": "UI_AvatarIcon_Xingqiu.png"},
    "班尼特": {"element": "火", "weapon": "单手剑", "icon": "UI_AvatarIcon_Bennett.png"},
    "久岐忍": {"element": "雷", "weapon": "单手剑", "icon": "UI_AvatarIcon_Shinobu.png"},
    "菲谢尔": {"element": "雷", "weapon": "弓", "icon": "UI_AvatarIcon_Fischl.png"},
    "砂糖": {"element": "风", "weapon": "法器", "icon": "UI_AvatarIcon_Sucrose.png"},
    "北斗": {"element": "雷", "weapon": "双手剑", "icon": "UI_AvatarIcon_Beidou.png"},
    "凝光": {"element": "岩", "weapon": "法器", "icon": "UI_AvatarIcon_Ningguang.png"},
    "迪奥娜": {"element": "冰", "weapon": "弓", "icon": "UI_AvatarIcon_Diona.png"},
    "重云": {"element": "冰", "weapon": "双手剑", "icon": "UI_AvatarIcon_Chongyun.png"},
    "芭芭拉": {"element": "水", "weapon": "法器", "icon": "UI_AvatarIcon_Barbara.png"},
    "雷泽": {"element": "雷", "weapon": "双手剑", "icon": "UI_AvatarIcon_Razor.png"},
    "诺艾尔": {"element": "岩", "weapon": "双手剑", "icon": "UI_AvatarIcon_Noel.png"},
    "罗莎莉亚": {"element": "冰", "weapon": "长柄武器", "icon": "UI_AvatarIcon_Rosaria.png"},
    "烟绯": {"element": "火", "weapon": "法器", "icon": "UI_AvatarIcon_Feiyan.png"},
    "早柚": {"element": "风", "weapon": "双手剑", "icon": "UI_AvatarIcon_Sayu.png"},
    "九条裟罗": {"element": "雷", "weapon": "弓", "icon": "UI_AvatarIcon_Sara.png"},
    "托马": {"element": "火", "weapon": "长柄武器", "icon": "UI_AvatarIcon_Tohma.png"},
    "五郎": {"element": "岩", "weapon": "弓", "icon": "UI_AvatarIcon_Gorou.png"},
    "云堇": {"element": "岩", "weapon": "长柄武器", "icon": "UI_AvatarIcon_Yunjin.png"},
    "鹿野院平藏": {"element": "风", "weapon": "法器", "icon": "UI_AvatarIcon_Heizo.png"},
    "柯莱": {"element": "草", "weapon": "弓", "icon": "UI_AvatarIcon_Collei.png"},
    "多莉": {"element": "雷", "weapon": "双手剑", "icon": "UI_AvatarIcon_Dori.png"},
    "坎蒂丝": {"element": "水", "weapon": "长柄武器", "icon": "UI_AvatarIcon_Candace.png"},
    "莱依拉": {"element": "冰", "weapon": "单手剑", "icon": "UI_AvatarIcon_Layla.png"},
    "珐露珊": {"element": "风", "weapon": "弓", "icon": "UI_AvatarIcon_Faruzan.png"},
    "瑶瑶": {"element": "草", "weapon": "长柄武器", "icon": "UI_AvatarIcon_Yaoyao.png"},
    "米卡": {"element": "冰", "weapon": "长柄武器", "icon": "UI_AvatarIcon_Mika.png"},
    "卡维": {"element": "草", "weapon": "双手剑", "icon": "UI_AvatarIcon_Kaveh.png"},
    "绮良良": {"element": "草", "weapon": "单手剑", "icon": "UI_AvatarIcon_Momoka.png"},
    "琳妮特": {"element": "风", "weapon": "单手剑", "icon": "UI_AvatarIcon_Linette.png"},
    "菲米尼": {"element": "冰", "weapon": "双手剑", "icon": "UI_AvatarIcon_Freminet.png"},
    "夏洛蒂": {"element": "冰", "weapon": "法器", "icon": "UI_AvatarIcon_Charlotte.png"},
    "嘉明": {"element": "火", "weapon": "双手剑", "icon": "UI_AvatarIcon_Gaming.png"},
    "赛索斯": {"element": "雷", "weapon": "弓", "icon": "UI_AvatarIcon_Sethos.png"},
    "卡齐娜": {"element": "岩", "weapon": "长柄武器", "icon": "UI_AvatarIcon_Kachina.png"},
    "欧洛伦": {"element": "雷", "weapon": "弓", "icon": "UI_AvatarIcon_Olorun.png"},
    "安柏": {"element": "火", "weapon": "弓", "icon": "UI_AvatarIcon_Ambor.png"},
    "凯亚": {"element": "冰", "weapon": "单手剑", "icon": "UI_AvatarIcon_Kaeya.png"},
    "丽莎": {"element": "雷", "weapon": "法器", "icon": "UI_AvatarIcon_Lisa.png"},
    "辛焱": {"element": "火", "weapon": "双手剑", "icon": "UI_AvatarIcon_Xinyan.png"},
    "蓝砚": {"element": "风", "weapon": "法器", "icon": "UI_AvatarIcon_Lanyan.png"},
}

# 常用四星武器表
GENSHIN_WEAPONS_4STAR = {
    "西风剑": {"type": "单手剑", "icon": "UI_EquipIcon_Sword_Zephyrus.png"},
    "祭礼剑": {"type": "单手剑", "icon": "UI_EquipIcon_Sword_Fossil.png"},
    "匣里龙吟": {"type": "单手剑", "icon": "UI_EquipIcon_Sword_Rockkiller.png"},
    "笛剑": {"type": "单手剑", "icon": "UI_EquipIcon_Sword_Troupe.png"},
    "黑剑": {"type": "单手剑", "icon": "UI_EquipIcon_Sword_Kannazuki.png"},
    "天目影打刀": {"type": "单手剑", "icon": "UI_EquipIcon_Sword_Bakufu.png"},
    "西风大剑": {"type": "双手剑", "icon": "UI_EquipIcon_Claymore_Zephyrus.png"},
    "祭礼大剑": {"type": "双手剑", "icon": "UI_EquipIcon_Claymore_Fossil.png"},
    "雨裁": {"type": "双手剑", "icon": "UI_EquipIcon_Claymore_Perdue.png"},
    "钟剑": {"type": "双手剑", "icon": "UI_EquipIcon_Claymore_Troupe.png"},
    "螭骨剑": {"type": "双手剑", "icon": "UI_EquipIcon_Claymore_Kione.png"},
    "白影剑": {"type": "双手剑", "icon": "UI_EquipIcon_Claymore_Proto.png"},
    "西风长枪": {"type": "长柄武器", "icon": "UI_EquipIcon_Pole_Zephyrus.png"},
    "匣里灭辰": {"type": "长柄武器", "icon": "UI_EquipIcon_Pole_Stardust.png"},
    "决斗之枪": {"type": "长柄武器", "icon": "UI_EquipIcon_Pole_Gladiator.png"},
    "渔获": {"type": "长柄武器", "icon": "UI_EquipIcon_Pole_Mori.png"},
    "昭心": {"type": "法器", "icon": "UI_EquipIcon_Catalyst_Troupe.png"},
    "流浪乐章": {"type": "法器", "icon": "UI_EquipIcon_Catalyst_Troupe.png"},
    "西风秘典": {"type": "法器", "icon": "UI_EquipIcon_Catalyst_Zephyrus.png"},
    "祭礼残章": {"type": "法器", "icon": "UI_EquipIcon_Catalyst_Fossil.png"},
    "匣里日月": {"type": "法器", "icon": "UI_EquipIcon_Catalyst_Resonance.png"},
    "西风猎弓": {"type": "弓", "icon": "UI_EquipIcon_Bow_Zephyrus.png"},
    "祭礼弓": {"type": "弓", "icon": "UI_EquipIcon_Bow_Fossil.png"},
    "绝弦": {"type": "弓", "icon": "UI_EquipIcon_Bow_Troupe.png"},
    "弓藏": {"type": "弓", "icon": "UI_EquipIcon_Bow_Recluse.png"},
}

# 祈愿三星武器全集（支持 100% 覆盖原神抽卡 3 星掉落与白缨枪）
GENSHIN_WEAPONS_3STAR = {
    # 单手剑
    "冷刃": {"type": "单手剑", "icon": "UI_EquipIcon_Sword_Darker.png"},
    "黎明神剑": {"type": "单手剑", "icon": "UI_EquipIcon_Sword_Dawn.png"},
    "飞天御剑": {"type": "单手剑", "icon": "UI_EquipIcon_Sword_Mitsurugi.png"},
    # 双手剑
    "以理服人": {"type": "双手剑", "icon": "UI_EquipIcon_Claymore_Reasoning.png"},
    "沐浴龙血的剑": {"type": "双手剑", "icon": "UI_EquipIcon_Claymore_Glaive.png"},
    "铁影阔剑": {"type": "双手剑", "icon": "UI_EquipIcon_Claymore_Glaive.png"},
    # 长柄武器
    "白缨枪": {"type": "长柄武器", "icon": "UI_EquipIcon_Pole_Ruby.png"},
    "黑缨枪": {"type": "长柄武器", "icon": "UI_EquipIcon_Pole_Noire.png"},
    # 法器
    "魔导绪论": {"type": "法器", "icon": "UI_EquipIcon_Catalyst_Intro.png"},
    "讨龙英杰谭": {"type": "法器", "icon": "UI_EquipIcon_Catalyst_Pulpfic.png"},
    "翡玉法球": {"type": "法器", "icon": "UI_EquipIcon_Catalyst_Jade.png"},
    # 弓
    "弹弓": {"type": "弓", "icon": "UI_EquipIcon_Bow_Sling.png"},
    "神射手之誓": {"type": "弓", "icon": "UI_EquipIcon_Bow_Arjuna.png"},
    "鸦羽弓": {"type": "弓", "icon": "UI_EquipIcon_Bow_Crowfeather.png"},
}

LOCAL_AVATAR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images", "avatars")

def get_genshin_avatar_url(name: str, item_type: str = "") -> str:
    """获取原神角色或武器的高清图标链接（优先检测本地名称同名立绘）"""
    # 0. 优先自动探测本地以名称命名的立绘图片 (如 static/images/avatars/沃雅妮莎.png)
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        local_path = os.path.join(LOCAL_AVATAR_DIR, f"{name}{ext}")
        if os.path.exists(local_path):
            return f"/images/avatars/{name}{ext}"

    # 优先查 5 星角色
    if name in GENSHIN_CHARACTERS_5STAR:
        c = GENSHIN_CHARACTERS_5STAR[name]
        if "avatar" in c and c["avatar"]:
            return c["avatar"]
        icon = c.get("icon", "")
        return f"{CHAR_AVATAR_BASE}/{icon}"
    # 查 4 星角色
    if name in GENSHIN_CHARACTERS_4STAR:
        c = GENSHIN_CHARACTERS_4STAR[name]
        if "avatar" in c:
            return c["avatar"]
        icon = c.get("icon", "")
        return f"{CHAR_AVATAR_BASE}/{icon}"
    # 查 5 星武器
    if name in GENSHIN_WEAPONS_5STAR:
        w = GENSHIN_WEAPONS_5STAR[name]
        if "avatar" in w:
            return w["avatar"]
        icon = w.get("icon", "")
        return f"{WEAPON_AVATAR_BASE}/{icon}"
    # 查 4 星武器
    if name in GENSHIN_WEAPONS_4STAR:
        w = GENSHIN_WEAPONS_4STAR[name]
        if "avatar" in w:
            return w["avatar"]
        icon = w.get("icon", "")
        return f"{WEAPON_AVATAR_BASE}/{icon}"
    # 查 3 星武器
    if name in GENSHIN_WEAPONS_3STAR:
        w = GENSHIN_WEAPONS_3STAR[name]
        if "avatar" in w:
            return w["avatar"]
        icon = w.get("icon", "")
        return f"{WEAPON_AVATAR_BASE}/{icon}"
        
    return ""

def is_genshin_standard_5star(name: str, item_type: str = "角色") -> bool:
    """判断是否为原神常驻五星（即小保底歪卡）"""
    if "角色" in item_type or name in GENSHIN_CHARACTERS_5STAR:
        return name in GENSHIN_STANDARD_5STAR_CHARS
    if "武器" in item_type or name in GENSHIN_WEAPONS_5STAR:
        return name in GENSHIN_STANDARD_5STAR_WEAPONS
    return False

def get_all_genshin_config_data():
    """获取原神完整的图鉴清单（供前端界面查看和编辑）"""
    chars_list = []
    
    # 5星角色
    for name, c in GENSHIN_CHARACTERS_5STAR.items():
        avatar_src = c.get("avatar") or f"{CHAR_AVATAR_BASE}/{c.get('icon', '')}"
        chars_list.append({
            "name": name,
            "category": "角色",
            "star": 5,
            "element": c.get("element", "风"),
            "weapon": c.get("weapon", "单手剑"),
            "type": "常驻" if c.get("standard") else "UP",
            "avatar": avatar_src,
            "id": ""
        })
        
    # 4星角色
    for name, c in GENSHIN_CHARACTERS_4STAR.items():
        chars_list.append({
            "name": name,
            "category": "角色",
            "star": 4,
            "element": c.get("element", "火"),
            "weapon": c.get("weapon", "单手剑"),
            "type": "4星",
            "avatar": f"{CHAR_AVATAR_BASE}/{c.get('icon', '')}",
            "id": ""
        })

    # 5星武器
    for name, w in GENSHIN_WEAPONS_5STAR.items():
        chars_list.append({
            "name": name,
            "category": "武器",
            "star": 5,
            "element": "武器",
            "weapon": w.get("type", "单手剑"),
            "type": "常驻" if w.get("standard") else "UP",
            "avatar": f"{WEAPON_AVATAR_BASE}/{w.get('icon', '')}",
            "id": ""
        })

    # 4星武器
    for name, w in GENSHIN_WEAPONS_4STAR.items():
        chars_list.append({
            "name": name,
            "category": "武器",
            "star": 4,
            "element": "武器",
            "weapon": w.get("type", "单手剑"),
            "type": "4星",
            "avatar": f"{WEAPON_AVATAR_BASE}/{w.get('icon', '')}",
            "id": ""
        })

    # 3星武器（原神抽卡全量 3 星掉落）
    for name, w in GENSHIN_WEAPONS_3STAR.items():
        chars_list.append({
            "name": name,
            "category": "武器",
            "star": 3,
            "element": "武器",
            "weapon": w.get("type", "单手剑"),
            "type": "3星",
            "avatar": f"{WEAPON_AVATAR_BASE}/{w.get('icon', '')}",
            "id": ""
        })

    custom_cfg = {}
    if os.path.exists(GENSHIN_CONFIG_PATH):
        try:
            with open(GENSHIN_CONFIG_PATH, "r", encoding="utf-8") as f:
                custom_cfg = json.load(f)
        except Exception:
            pass

    return {
        "customUrl": custom_cfg.get("customUrl", ""),
        "customLogPath": custom_cfg.get("customLogPath", ""),
        "idMap": {},
        "aliasMap": {},
        "charactersList": chars_list,
        "elements": ["风", "岩", "雷", "草", "水", "火", "冰"]
    }

# ================= 原神自定义配置管理与持久化 =================
GENSHIN_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "genshin_custom_config.json")

def load_genshin_custom_config():
    """加载并应用用户自定义的原神角色、头像及链接"""
    global GENSHIN_CHARACTERS_5STAR, GENSHIN_CHARACTERS_4STAR, GENSHIN_WEAPONS_5STAR, GENSHIN_WEAPONS_4STAR
    if not os.path.exists(GENSHIN_CONFIG_PATH):
        return {}
    try:
        with open(GENSHIN_CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            
        for name, info in cfg.get("characters", {}).items():
            if info.get("star") == 5:
                GENSHIN_CHARACTERS_5STAR[name] = info
            else:
                GENSHIN_CHARACTERS_4STAR[name] = info
                
        for name, info in cfg.get("weapons", {}).items():
            if info.get("star") == 5:
                GENSHIN_WEAPONS_5STAR[name] = info
            else:
                GENSHIN_WEAPONS_4STAR[name] = info
                
        return cfg
    except Exception as e:
        print(f"加载原神自定义配置失败: {e}")
        return {}

def save_genshin_custom_config(new_config):
    """持久化用户自定义配置并即时热重载（增量合并）"""
    os.makedirs(os.path.dirname(GENSHIN_CONFIG_PATH), exist_ok=True)
    cfg = {}
    if os.path.exists(GENSHIN_CONFIG_PATH):
        try:
            with open(GENSHIN_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
    if not isinstance(cfg, dict):
        cfg = {}

    if "characters" not in cfg:
        cfg["characters"] = {}
    if "weapons" not in cfg:
        cfg["weapons"] = {}

    if "characters" in new_config:
        cfg["characters"].update(new_config["characters"])
    if "weapons" in new_config:
        cfg["weapons"].update(new_config["weapons"])
    if "customUrl" in new_config:
        cfg["customUrl"] = new_config["customUrl"].strip()
    if "customLogPath" in new_config:
        cfg["customLogPath"] = new_config["customLogPath"].strip()

    with open(GENSHIN_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    load_genshin_custom_config()

# 模块导入时默认加载自定义配置
load_genshin_custom_config()
