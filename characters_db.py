# -*- coding: utf-8 -*-
"""
鸣潮角色与武器数据库
包含共鸣者属性、星级、卡池归属、高清头像与武器 CDN
支持国服、国际服（港澳台/日韩/欧美）全角色与专武映射
"""

import os
import json

IMG_BASE = "https://fastly.jsdelivr.net/gh/ryanbenson/wuthering-waves-assets@master/images/"
WEAPON_BASE = "https://fastly.jsdelivr.net/gh/ryanbenson/wuthering-waves-assets@master/images/weapons/"

# 资源 ID 映射表（官方内部 ID 到标准显示名称）
ID_MAP = {
    # 角色 (基于官方日志实际 resourceId 修正与补齐)
    1102: "散华",
    1103: "白芷",
    1106: "釉瑚",
    1108: "绯雪",
    1203: "安可",
    1204: "莫特斐",
    1205: "吟霖",
    1206: "折枝",
    1301: "卡卡罗",
    1302: "忌炎",
    1303: "渊武",
    1305: "相里要",
    1307: "卜灵",
    1401: "炽霞",
    1402: "秧秧",
    1403: "秋水",
    1404: "长离",
    1405: "鉴心",
    1406: "椿",
    1411: "仇远",
    1501: "白芷",
    1503: "维里奈",
    1504: "灯灯",
    1505: "守岸人",
    1601: "桃祈",
    1602: "丹瑾",
    # 五星武器
    21020086: "霜天灼刃",
    # 四星武器 (基于用户日志实际抽到 ID 补齐)
    21020044: "不归孤军",
    21010044: "永夜长明",
    21010064: "东落",
    21050024: "奇幻变奏",
    21050064: "异度",
    21040044: "袍泽之固",
    21050044: "今州守望",
    21020024: "行进序曲",
    21020064: "西升",
    21010024: "异响空灵",
    21030064: "飞逝",
    21020084: "永续坍缩",
    21040064: "骇行",
    21030044: "无眠烈火",
    21040084: "尘云旋臂",
    21040024: "呼啸重音",
    21010084: "凋亡频移",
    21030024: "华彩乐段",
    21050084: "核熔星盘",
    21030084: "悖论喷流",
    21020015: "千古汧流",
}

# 别名/内部代号映射
ALIAS_MAP = {
    "绯雪": "绯雪",
    "緋雪": "绯雪",
    "Hiyuki": "绯雪",
    "仇远": "仇远",
    "Qiuyuan": "仇远",
    "Qiu Yuan": "仇远",
    "卜灵": "卜灵",
    "Buling": "卜灵",
    "Bu Ling": "卜灵",
    "菲比": "菲比",
    "Phoebe": "菲比",
    "布兰特": "布兰特",
    "Brant": "布兰特",
    "坎特蕾拉": "坎特蕾拉",
    "Cantarella": "坎特蕾拉",
    "赞妮": "赞妮",
    "Zani": "赞妮",
    "弗洛洛": "弗洛洛",
    "Phrolova": "弗洛洛",
    "奥古斯塔": "奥古斯塔",
    "Augusta": "奥古斯塔",
    "尤诺": "尤诺",
    "Iuno": "尤诺",
    "Yuno": "尤诺",
    "嘉贝莉娜": "嘉贝莉娜",
    "Galbrena": "嘉贝莉娜",
    "清宵": "清宵",
    "Qingxiao": "清宵",
    "景燃": "景燃",
    "Jingran": "景燃",
    "达妮娅": "达妮娅",
    "Denia": "达妮娅",
    "Dania": "达妮娅",
    "莫宁": "莫宁",
    "Mornye": "莫宁",
    "Morning": "莫宁",
    "霜天灼刃": "霜天灼刃",
    "霜天银刃": "霜天灼刃",
    "Frostburn": "霜天灼刃",
    "裁竹": "裁竹",
    "Emerald Sentence": "裁竹",
    "EmeraldSentence": "裁竹",
    "死与舞": "死与舞",
    "The Last Dance": "死与舞",
    "TheLastDance": "死与舞",
    "悲喜剧": "悲喜剧",
    "Tragicomedy": "悲喜剧",
    "千古汧流": "千古汧流",
    "千古洐流": "千古汧流",
    "Emerald of Genesis": "千古汧流",
    "EmeraldOfGenesis": "千古汧流",
    "核熔星盘": "核熔星盘",
    "悖论喷流": "悖论喷流",
}

# 属性定义与色彩
ELEMENTS = {
    "衍射": {"name": "衍射", "en": "Spectro", "color": "#facc15", "bg": "rgba(250, 204, 21, 0.15)"},
    "湮灭": {"name": "湮灭", "en": "Havoc", "color": "#c084fc", "bg": "rgba(192, 132, 252, 0.15)"},
    "热熔": {"name": "热熔", "en": "Fusion", "color": "#f87171", "bg": "rgba(248, 113, 113, 0.15)"},
    "冷凝": {"name": "冷凝", "en": "Glacio", "color": "#38bdf8", "bg": "rgba(56, 189, 248, 0.15)"},
    "气动": {"name": "气动", "en": "Aero", "color": "#34d399", "bg": "rgba(52, 211, 153, 0.15)"},
    "导电": {"name": "导电", "en": "Electro", "color": "#a78bfa", "bg": "rgba(167, 139, 250, 0.15)"},
}

# 常驻五星角色列表（用于判断限定角色池是否“歪卡”）
STANDARD_FIVE_STARS = {
    "维里奈",
    "安可",
    "鉴心",
    "卡卡罗",
    "凌阳"
}

# 角色资料表
CHARACTERS = {
    # 5星限定角色
    "仇远": {"star": 5, "element": "气动", "weapon": "迅刀", "type": "UP", "avatar": IMG_BASE + "Qiuyuan.png"},
    "绯雪": {"star": 5, "element": "冷凝", "weapon": "迅刀", "type": "UP", "avatar": IMG_BASE + "Hiyuki.png"},
    "今汐": {"star": 5, "element": "衍射", "weapon": "重刃", "type": "UP", "avatar": IMG_BASE + "Jinhsi.png"},
    "长离": {"star": 5, "element": "热熔", "weapon": "迅刀", "type": "UP", "avatar": IMG_BASE + "Changli.png"},
    "椿": {"star": 5, "element": "湮灭", "weapon": "迅刀", "type": "UP", "avatar": IMG_BASE + "Camellya.png"},
    "忌炎": {"star": 5, "element": "气动", "weapon": "重刃", "type": "UP", "avatar": IMG_BASE + "Jiyan.png"},
    "吟霖": {"star": 5, "element": "导电", "weapon": "音感仪", "type": "UP", "avatar": IMG_BASE + "Yinlin.png"},
    "折枝": {"star": 5, "element": "冷凝", "weapon": "音感仪", "type": "UP", "avatar": IMG_BASE + "Zhezhi.png"},
    "相里要": {"star": 5, "element": "导电", "weapon": "臂铠", "type": "UP", "avatar": IMG_BASE + "XiangliYao.png"},
    "守岸人": {"star": 5, "element": "衍射", "weapon": "音感仪", "type": "UP", "avatar": IMG_BASE + "Shorekeeper.png"},
    "珂莱塔": {"star": 5, "element": "冷凝", "weapon": "佩枪", "type": "UP", "avatar": IMG_BASE + "Carlotta.png"},
    "洛可可": {"star": 5, "element": "湮灭", "weapon": "臂铠", "type": "UP", "avatar": IMG_BASE + "Roccia.png"},
    "菲比": {"star": 5, "element": "衍射", "weapon": "音感仪", "type": "UP", "avatar": IMG_BASE + "Phoebe.png"},
    "布兰特": {"star": 5, "element": "热熔", "weapon": "迅刀", "type": "UP", "avatar": IMG_BASE + "Brant.png"},
    "坎特蕾拉": {"star": 5, "element": "湮灭", "weapon": "音感仪", "type": "UP", "avatar": IMG_BASE + "Cantarella.png"},
    "赞妮": {"star": 5, "element": "衍射", "weapon": "臂铠", "type": "UP", "avatar": IMG_BASE + "Zani.png"},
    "弗洛洛": {"star": 5, "element": "湮灭", "weapon": "音感仪", "type": "UP", "avatar": IMG_BASE + "Phrolova.png"},
    "奥古斯塔": {"star": 5, "element": "导电", "weapon": "重刃", "type": "UP", "avatar": IMG_BASE + "Augusta.png"},
    "尤诺": {"star": 5, "element": "气动", "weapon": "臂铠", "type": "UP", "avatar": IMG_BASE + "Iuno.png"},
    "嘉贝莉娜": {"star": 5, "element": "热熔", "weapon": "佩枪", "type": "UP", "avatar": IMG_BASE + "Galbrena.png"},
    "清宵": {"star": 5, "element": "气动", "weapon": "迅刀", "type": "UP", "avatar": IMG_BASE + "Qingxiao.png"},
    "景燃": {"star": 5, "element": "热熔", "weapon": "重刃", "type": "UP", "avatar": IMG_BASE + "Jingran.png"},
    "达妮娅": {"star": 5, "element": "热熔", "weapon": "音感仪", "type": "UP", "avatar": IMG_BASE + "Denia.png"},
    "莫宁": {"star": 5, "element": "热熔", "weapon": "重刃", "type": "UP", "avatar": IMG_BASE + "Mornye.png"},

    # 5星常驻角色
    "维里奈": {"star": 5, "element": "衍射", "weapon": "音感仪", "type": "常驻", "avatar": IMG_BASE + "Verina.png"},
    "安可": {"star": 5, "element": "热熔", "weapon": "音感仪", "type": "常驻", "avatar": IMG_BASE + "Encore.png"},
    "鉴心": {"star": 5, "element": "气动", "weapon": "臂铠", "type": "常驻", "avatar": IMG_BASE + "Jianxin.png"},
    "卡卡罗": {"star": 5, "element": "导电", "weapon": "重刃", "type": "常驻", "avatar": IMG_BASE + "Calcharo.png"},
    "凌阳": {"star": 5, "element": "冷凝", "weapon": "臂铠", "type": "常驻", "avatar": IMG_BASE + "Lingyang.png"},
    "漂泊者": {"star": 5, "element": "衍射", "weapon": "迅刀", "type": "主角", "avatar": IMG_BASE + "RoverFemale.png"},

    # 4星角色
    "卜灵": {"star": 4, "element": "导电", "weapon": "音感仪", "type": "4星", "avatar": IMG_BASE + "Buling.png"},
    "散华": {"star": 4, "element": "冷凝", "weapon": "迅刀", "type": "4星", "avatar": IMG_BASE + "Sanhua.png"},
    "白芷": {"star": 4, "element": "冷凝", "weapon": "音感仪", "type": "4星", "avatar": IMG_BASE + "Baizhi.png"},
    "丹瑾": {"star": 4, "element": "湮灭", "weapon": "迅刀", "type": "4星", "avatar": IMG_BASE + "Danjin.png"},
    "炽霞": {"star": 4, "element": "热熔", "weapon": "佩枪", "type": "4星", "avatar": IMG_BASE + "Chixia.png"},
    "秧秧": {"star": 4, "element": "气动", "weapon": "迅刀", "type": "4星", "avatar": IMG_BASE + "Yangyang.png"},
    "莫特斐": {"star": 4, "element": "热熔", "weapon": "佩枪", "type": "4星", "avatar": IMG_BASE + "Mortefi.png"},
    "渊武": {"star": 4, "element": "导电", "weapon": "臂铠", "type": "4星", "avatar": IMG_BASE + "Yuanwu.png"},
    "桃祈": {"star": 4, "element": "湮灭", "weapon": "重刃", "type": "4星", "avatar": IMG_BASE + "Taoqi.png"},
    "秋水": {"star": 4, "element": "气动", "weapon": "佩枪", "type": "4星", "avatar": IMG_BASE + "Aalto.png"},
    "釉瑚": {"star": 4, "element": "冷凝", "weapon": "臂铠", "type": "4星", "avatar": IMG_BASE + "Youhu.png"},
    "灯灯": {"star": 4, "element": "导电", "weapon": "重刃", "type": "4星", "avatar": IMG_BASE + "Lumi.png"},
}

# 五星武器表
WEAPONS_5STAR = {
    # 限定五星武器
    "死与舞": {"star": 5, "weapon": "佩枪", "type": "UP", "avatar": WEAPON_BASE + "TheLastDance.png"},
    "悲喜剧": {"star": 5, "weapon": "臂铠", "type": "UP", "avatar": WEAPON_BASE + "Tragicomedy.png"},
    "裁竹": {"star": 5, "weapon": "迅刀", "type": "UP", "avatar": WEAPON_BASE + "EmeraldSentence.png"},
    "霜天灼刃": {"star": 5, "weapon": "迅刀", "type": "UP", "avatar": WEAPON_BASE + "Frostburn.png"},
    "苍鳞千嶂": {"star": 5, "weapon": "重刃", "type": "UP", "avatar": WEAPON_BASE + "VerdantSummit.png"},
    "掣傀之手": {"star": 5, "weapon": "音感仪", "type": "UP", "avatar": WEAPON_BASE + "Stringmaster.png"},
    "时斯如梭": {"star": 5, "weapon": "重刃", "type": "UP", "avatar": WEAPON_BASE + "AgesOfHarvest.png"},
    "赫奕流明": {"star": 5, "weapon": "迅刀", "type": "UP", "avatar": WEAPON_BASE + "BlazingBrilliance.png"},
    "琼枝冰绡": {"star": 5, "weapon": "音感仪", "type": "UP", "avatar": WEAPON_BASE + "RimeDrapedSprouts.png"},
    "诸方玄枢": {"star": 5, "weapon": "臂铠", "type": "UP", "avatar": WEAPON_BASE + "VeritysHandle.png"},
    "序奇微芒": {"star": 5, "weapon": "音感仪", "type": "UP", "avatar": WEAPON_BASE + "StellarSymphony.png"},
    "裁春": {"star": 5, "weapon": "迅刀", "type": "UP", "avatar": WEAPON_BASE + "RedSpring.png"},
    
    # 常驻五星武器
    "浩境粼光": {"star": 5, "weapon": "重刃", "type": "常驻", "avatar": WEAPON_BASE + "LustrousRazor.png"},
    "停驻之烟": {"star": 5, "weapon": "佩枪", "type": "常驻", "avatar": WEAPON_BASE + "StaticMist.png"},
    "擎渊怒涛": {"star": 5, "weapon": "臂铠", "type": "常驻", "avatar": WEAPON_BASE + "AbyssSurges.png"},
    "漪澜浮录": {"star": 5, "weapon": "音感仪", "type": "常驻", "avatar": WEAPON_BASE + "CosmicRipples.png"},
    "千古汧流": {"star": 5, "weapon": "迅刀", "type": "常驻", "avatar": WEAPON_BASE + "EmeraldOfGenesis.png"},
}

# 四星武器表
WEAPONS_4STAR = {
    "不归孤军": {"weapon": "重刃", "avatar": WEAPON_BASE + "DauntlessEvernight.png"},
    "永夜长明": {"weapon": "迅刀", "avatar": WEAPON_BASE + "CommandoOfConviction.png"},
    "东落": {"weapon": "重刃", "avatar": WEAPON_BASE + "WaningRedshift.png"},
    "奇幻变奏": {"weapon": "音感仪", "avatar": WEAPON_BASE + "Variation.png"},
    "异度": {"weapon": "佩枪", "avatar": WEAPON_BASE + "Novaburst.png"},
    "袍泽之固": {"weapon": "重刃", "avatar": WEAPON_BASE + "AmityAccord.png"},
    "今州守望": {"weapon": "音感仪", "avatar": WEAPON_BASE + "JinzhouKeeper.png"},
    "行进序曲": {"weapon": "迅刀", "avatar": WEAPON_BASE + "Overture.png"},
    "西升": {"weapon": "迅刀", "avatar": WEAPON_BASE + "LunarCutter.png"},
    "异响空灵": {"weapon": "佩枪", "avatar": WEAPON_BASE + "Cadenza.png"},
    "飞逝": {"weapon": "佩枪", "avatar": WEAPON_BASE + "Thunderbolt.png"},
    "永续坍缩": {"weapon": "重刃", "avatar": WEAPON_BASE + "EndlessCollapse.png"},
    "骇行": {"weapon": "臂铠", "avatar": WEAPON_BASE + "Marcato.png"},
    "无眠烈火": {"weapon": "佩枪", "avatar": WEAPON_BASE + "UndyingFlame.png"},
    "尘云旋臂": {"weapon": "臂铠", "avatar": WEAPON_BASE + "CelestialSpiral.png"},
    "呼啸重音": {"weapon": "臂铠", "avatar": WEAPON_BASE + "HollowMirage.png"},
    "凋亡频移": {"weapon": "佩枪", "avatar": WEAPON_BASE + "RelativisticJet.png"},
    "华彩乐段": {"weapon": "音感仪", "avatar": WEAPON_BASE + "Augment.png"},
    "核熔星盘": {"weapon": "音感仪", "avatar": WEAPON_BASE + "FusionAccretion.png"},
    "悖论喷流": {"weapon": "佩枪", "avatar": WEAPON_BASE + "RelativisticJet.png"},
    "秋罡": {"weapon": "重刃", "avatar": WEAPON_BASE + "Autumntrace.png"},
    "飞景": {"weapon": "迅刀", "avatar": WEAPON_BASE + "Lumingloss.png"},
    "金掌": {"weapon": "臂铠", "avatar": WEAPON_BASE + "Stonard.png"},
    "清音": {"weapon": "音感仪", "avatar": WEAPON_BASE + "Augment.png"},
    "奔雷": {"weapon": "佩枪", "avatar": WEAPON_BASE + "SolarFlame.png"},
}

def get_item_info(name, quality_level=None, resource_type=None, resource_id=None):
    """
    获取物品详细信息（星级、属性、类型、图片）
    优先使用准确的原名，或通过 resource_id / 别名修正名称
    """
    orig_name = (name or "").strip()
    
    # 如果原始名称已经是已知角色/武器，直接使用
    if orig_name in CHARACTERS or orig_name in WEAPONS_5STAR or orig_name in WEAPONS_4STAR or orig_name in ALIAS_MAP:
        name = ALIAS_MAP.get(orig_name, orig_name)
    elif resource_id:
        try:
            rid_int = int(resource_id)
            if rid_int in ID_MAP:
                name = ID_MAP[rid_int]
        except Exception:
            pass

    if name in ALIAS_MAP:
        name = ALIAS_MAP[name]

    if name in CHARACTERS:
        c = CHARACTERS[name]
        elem_info = ELEMENTS.get(c["element"], {})
        return {
            "name": name,
            "category": "角色",
            "star": c["star"],
            "element": c["element"],
            "elementColor": elem_info.get("color", "#e2e8f0"),
            "elementBg": elem_info.get("bg", "rgba(250, 204, 21, 0.15)"),
            "weapon": c["weapon"],
            "isUp": c["type"] == "UP",
            "isStandard": name in STANDARD_FIVE_STARS,
            "avatar": c.get("avatar", "")
        }
    
    if name in WEAPONS_5STAR:
        w = WEAPONS_5STAR[name]
        return {
            "name": name,
            "category": "武器",
            "star": 5,
            "element": "武器",
            "elementColor": "#eab308",
            "elementBg": "rgba(234, 179, 8, 0.15)",
            "weapon": w["weapon"],
            "isUp": w["type"] == "UP",
            "isStandard": w["type"] == "常驻",
            "avatar": w.get("avatar", "")
        }

    if name in WEAPONS_4STAR:
        w = WEAPONS_4STAR[name]
        return {
            "name": name,
            "category": "武器",
            "star": 4,
            "element": "武器",
            "elementColor": "#c084fc",
            "elementBg": "rgba(192, 132, 252, 0.15)",
            "weapon": w["weapon"],
            "isUp": False,
            "isStandard": True,
            "avatar": w.get("avatar", "")
        }
    
    star = quality_level or 3
    cat = resource_type or ("角色" if star >= 4 else "武器")
    return {
        "name": name,
        "category": cat,
        "star": star,
        "element": "常规",
        "elementColor": "#94a3b8" if star == 3 else "#c084fc",
        "elementBg": "rgba(148, 163, 184, 0.1)",
        "weapon": "",
        "isUp": False,
        "isStandard": True,
        "avatar": ""
    }

# ================= 自定义配置管理与持久化 =================
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "custom_config.json")

def load_custom_config():
    """
    加载并应用用户自定义的角色、头像、ID 映射及抽卡链接
    """
    global CHARACTERS, WEAPONS_5STAR, ID_MAP, ALIAS_MAP
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            
        # 覆盖 ID 映射
        for k, v in cfg.get("idMap", {}).items():
            try:
                ID_MAP[int(k)] = str(v)
            except ValueError:
                ID_MAP[str(k)] = str(v)
                
        # 覆盖别名映射
        for k, v in cfg.get("aliasMap", {}).items():
            ALIAS_MAP[str(k)] = str(v)
            
        # 覆盖/新增角色
        for name, info in cfg.get("characters", {}).items():
            CHARACTERS[name] = info
            
        # 覆盖/新增武器
        for name, info in cfg.get("weapons", {}).items():
            WEAPONS_5STAR[name] = info
            
        return cfg
    except Exception as e:
        print(f"加载自定义配置失败: {e}")
        return {}

def save_custom_config(new_config):
    """
    持久化用户自定义配置并即时热重载
    """
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(new_config, f, ensure_ascii=False, indent=2)
    load_custom_config()

def get_all_config_data():
    """
    返回完整的配置清单（供前端界面查看和编辑）
    """
    custom_cfg = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                custom_cfg = json.load(f)
        except Exception:
            pass

    # 构建 name -> id 映射
    name_to_id = {}
    for rid, name in ID_MAP.items():
        name_to_id[name] = str(rid)

    chars_list = []
    # 角色
    for name, c in CHARACTERS.items():
        chars_list.append({
            "name": name,
            "category": "角色",
            "star": c.get("star", 5),
            "element": c.get("element", "冷凝"),
            "weapon": c.get("weapon", "迅刀"),
            "type": c.get("type", "UP"),
            "avatar": c.get("avatar", ""),
            "id": name_to_id.get(name, "")
        })

    # 武器
    for name, w in WEAPONS_5STAR.items():
        chars_list.append({
            "name": name,
            "category": "武器",
            "star": w.get("star", 5),
            "element": "武器",
            "weapon": w.get("weapon", "迅刀"),
            "type": w.get("type", "UP"),
            "avatar": w.get("avatar", ""),
            "id": name_to_id.get(name, "")
        })

    return {
        "customUrl": custom_cfg.get("customUrl", ""),
        "customLogPath": custom_cfg.get("customLogPath", ""),
        "idMap": {str(k): str(v) for k, v in ID_MAP.items()},
        "aliasMap": ALIAS_MAP,
        "charactersList": chars_list,
        "elements": list(ELEMENTS.keys())
    }

# 模块导入时默认加载用户自定义配置
load_custom_config()

