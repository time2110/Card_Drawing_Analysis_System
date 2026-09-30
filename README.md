# 鸣潮 & 原神 双端抽卡分析系统 (Gacha Tracker for WuWa & Genshin)

<p align="center">
  <img src="https://fastly.jsdelivr.net/gh/ryanbenson/wuthering-waves-assets@master/images/Hiyuki.png" width="90" height="90" alt="WuWa Logo" style="border-radius: 18px; box-shadow: 0 4px 20px rgba(245, 158, 11, 0.3); margin-right: 12px;" />
  <img src="https://enka.network/ui/UI_AvatarIcon_Furina.png" width="90" height="90" alt="Genshin Logo" style="border-radius: 18px; box-shadow: 0 4px 20px rgba(56, 189, 248, 0.3);" />
</p>

<p align="center">
  <b>一款轻量、极速、零外部依赖的《鸣潮》与《原神》双端本地抽卡分析与保底水位可视化系统</b><br>
  鸣潮工坊风格流式看板 · 启动静默后台自动同步 · 永久本地只增不减保存 · 原神捕获明光算法 · UIGF 多格式导入导出 · 离线立绘与新角色扩展
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Standard%20Lib)-success?style=flat-square" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/Games-WuWa%20%7C%20Genshin%20Impact-blueviolet?style=flat-square" alt="Supported Games" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/Format-UIGF%20v3.0%20Compatible-orange?style=flat-square" alt="UIGF" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
</p>

---

## 💡 为什么选择本项目？

1. **🎮 鸣潮 & 原神 双端一键秒级切换**
   - 顶栏无缝切换游戏，系统自动记住上次选中的游戏状态（刷新或重启不重置）。
   - 鸣潮 6 大卡池（角色/武器活动唤取、常驻、新手唤取等）与原神 5 大卡池（角色祈愿 301/400、武器 302、常驻 200、集录 500、新手 100）全适配，多 UID 自由切换。
2. **⚡ 真正的纯原生零依赖（Zero Dependencies）**
   - 全套后端基于 Python 标准库原生开发（`http.server`, `urllib`, `ssl`, `json`），**无需 `pip install` 任何第三方包**！下载解压双击即可秒开。
3. **🔄 打开即同步：双端静默后台自动同步引擎**
   - 应用启动时，后台守护线程会自动嗅探鸣潮与原神的本地日志（`Client.log` 与 `output_log.txt`），若链接有效则自动静默增量拉取入库。
   - 页面顶部提供动态状态胶囊指示器，拉取到新记录后**自动无感刷新图表**。
4. **🛡️ 本地永久保留与高精度防重（突破官方 180 天与 1 年清除限制）**
   - 官方服务器会物理清理过往抽卡历史。本系统采用`时间戳 + 单抽位次 + 物品ID`复合指纹严格去重，**本地数据只增不减、永久留存**，即便回坑一年，垫刀水位依然无缝衔接。
5. **🎯 精准的各游戏专属保底机制**
   - **《鸣潮》**：80 抽保底基准、小保底 50/50 判定、专武 100% 不歪标记、专属红色“歪”印记。
   - **《原神》**：90 抽保底基准、74 抽软保底曲线、5.0+ **捕获明光（Captured Light）** 综合胜率模型、武器 80 抽定轨保底。
6. **🖼️ 全量高清立绘 + 杜绝破图 + 零门槛扔图识别**
   - 原神全面接入 Enka Network 全版本解包 CDN（1.0 至 5.x 枫丹/纳塔新角色 100% 真实高清立绘，彻底解决米游社假 200 黑史莱姆问题）。
   - 内置**动态 SVG 黄金流光印章徽章**：遇到未来尚未收录的新角色时，自动生成精致 5★ 印章，绝不出现死黑或破图。
   - **极简文件夹扔图法**：新角色推出时，只需将图片命名为 `角色名.png`（如 `火神.png`）丢进 `static/images/avatars/` 文件夹，系统自动秒级点亮！
7. **☁️ 坚果云 / WebDAV 云端自动备份与跨端恢复**
   - 原生支持坚果云（Jianguoyun）或任意标准 WebDAV 服务器，账号密码加密存储于本地，不泄露至代码仓库。
   - 每次后台或手动抽卡同步产生新记录后，**自动静默增量备份到云端**，再也不怕重装系统或换电脑丢失数据！
   - 支持多设备之间一键从云端拉取历史备份，增量智能合并，严格保证“只增不减”。
8. **📂 灵活支持自定义路径与手动链接输入**
   - 支持自动嗅探默认路径，也支持点击【📂 浏览选择】指定任意磁盘位置的日志文件，更支持手动粘贴抽卡 URL 进行增量同步。
9. **🔄 广泛的数据兼容性（UIGF 3.0 标准互通）**
   - 支持主流工具（**UIGF v3.0**、**鸣潮工坊**、**提瓦特小助手**、**Astrionyx**）的备份文件导入与导出，数据自由流转，无厂商绑定。

---

## 🖥️ 界面核心模块

* **综合欧非总览看板**：小保底不歪率、总抽数、原石/唤取原核折算、UP角色平均抽数、UP武器平均抽数、出金图鉴矩阵（带命座/同名数量徽章）。
* **横向水流出金流水**：顶部固定当前已垫抽数条，历史出金记录自适应各卡池保底深度（80 抽 / 90 抽 / 20 抽），按新到旧清晰排列。
* **ECharts 出金分布与概率直方图**：自适应软保底区间（原神 74 抽软保底 / 鸣潮 65 抽区间）。
* **全量日志独立表格视图**：支持 5★ / 4★ 星级筛选、名称即时搜索与分页导航。
* **双端【⚙️ 图鉴与配置】控制弹窗**：支持可视化编辑角色、武器、头像链接与专属抽卡链接，点击保存立即热重载。

---

## 🚀 快速开始

### 0. 环境准备 (Prerequisites)
* **Python 环境**：需要安装 **Python 3.8 及以上版本**（推荐 Python 3.10 ~ 3.12）。
  * 官方下载地址：[Python 官方下载](https://www.python.org/downloads/)。
  * ⚠️ **重要提示**：在 Windows 安装 Python 时，**务必勾选底部的 `Add python.exe to PATH`**（将 Python 添加到系统环境变量）。
* **零依赖**：本项目完全使用 Python 内置库，**无需执行任何 `pip install`**。

### 方式 A：Windows 双击一键启动（推荐）
1. 下载或克隆本项目仓库到本地。
2. 双击运行根目录下的 **`启动鸣潮抽卡分析.bat`**。
3. 程序会自动启动本地服务并调起默认浏览器访问：
   ```text
   http://127.0.0.1:8765
   ```

### 方式 B：跨平台命令行运行（Windows / macOS / Linux）
```bash
git clone https://github.com/time2110/Mingchao_Card_Drawing_Analysis_System.git
cd Mingchao_Card_Drawing_Analysis_System
python app.py
```
终端输出运行日志后，打开浏览器访问 `http://127.0.0.1:8765` 即可。

---

## 📖 如何同步游戏数据？

### 1. 《鸣潮》数据同步
1. 启动《鸣潮》客户端，进入游戏内按 `F3` 打开 **【唤取】** 页面；
2. 点击任意卡池下方的 **【唤取记录】** 按钮进入历史记录界面（游戏此时会在本地日志中写入凭据）；
3. 切换到本软件网页（如果后台自动同步已检测到，将直接自动入库；若未自动同步，点击顶栏 **【一键从日志同步】** 即可）。

### 2. 《原神》数据同步
1. 启动《原神》客户端，按 `F5` 进入 **【祈愿】** 页面；
2. 点击卡池下方的 **【历史记录】** 按钮打开抽卡历史一览；
3. 切换到本软件网页，顶栏切换为【原神】，点击 **【一键从日志同步】**（或等待后台自动同步）。

> 💡 **小贴士**：
> * 游戏内的抽卡链接时效约为 30~60 分钟。若提示“链接已过期”，只需在游戏里重新点开一次抽卡记录即可刷新时效。
> * 如果不想每次打开游戏，也可以在【⚙️ 图鉴与配置】中粘贴专属链接长期保存。

---

## 🎨 新角色立绘如何补齐？（3 种极简方式）

当游戏推出全新角色、而代码库尚未更新时，你可以任选以下方式之一秒级配置：

1. **文件夹直接扔图（最推荐 ⭐⭐⭐⭐⭐）**：
   - 保存一张新角色头像，重命名为角色的中文名称（例如 `玛拉妮.png` 或 `椿.png`）；
   - 丢进项目的 `static/images/avatars/` 文件夹；
   - 刷新页面，立绘立刻自动识别显示！
2. **网页表单即时添加（⭐⭐⭐⭐）**：
   - 点击网页右上角【⚙️ 图鉴与配置】，填入名称、星级、属性及任意图片链接，点击【保存此条目】即可热生效。
3. **配置文件修改（⭐⭐⭐）**：
   - 打开 `data/genshin_custom_config.json`（原神）或 `data/custom_config.json`（鸣潮）直接添加。

---

## ☁️ 坚果云 / WebDAV 云端备份与跨设备同步

为了彻底免除换电脑、重装系统或浏览器清空缓存导致数据丢失的顾虑，本项目提供了**基于 WebDAV 协议的原生云端自动备份体系**（深度兼容坚果云）。

### 1. 配置步骤 (只需 1 分钟)
1. 点击顶栏右侧的 **【☁️ 坚果云备份】** 按钮打开设置弹窗；
2. 服务商选择默认的 **【🥜 坚果云】**（服务器地址为 `https://dav.jianguoyun.com/dav/`）；
3. **输入坚果云账号**：通常为你注册坚果云时使用的登录邮箱；
4. **获取并输入应用密码**（⚠️ **注意：不是坚果云网页登录密码！**）：
   - 打开并登录 [坚果云官网](https://www.jianguoyun.com/)；
   - 点击右上角头像 ➔ **【账户信息】** ➔ 选择 **【安全选项】**；
   - 找到 **【第三方应用管理】**，点击 **【添加应用密码】**，输入应用名称（如 `GachaTracker`）并生成密码；
   - 复制生成的 16 位密码，粘贴至本软件的【应用密码】输入框中；
5. 点击 **【🔍 测试连接】**，提示“连接成功”即代表云端授权通过；
6. 勾选 **【启用坚果云同步】** 与 **【抽卡同步完成后自动备份到云端】**，点击 **【💾 保存设置】**。

### 2. 核心工作机制
* **静默自动推送**：开启后，每次系统在后台或手动完成鸣潮/原神抽卡记录拉取并产生新数据时，会自动将全量加密数据静默打包并推送到坚果云网盘的 `GachaTracker/` 目录下。
* **双向智能增量合并**：在新设备上只需输入相同的坚果云凭据，点击 **【⬇️ 从云端恢复】**，系统将从坚果云拉取远端历史，采用**只增不减原则**与本地数据合并，绝不会冲刷覆盖已有记录。
* **本地凭证安全隔离**：坚果云配置保存在本地 `data/webdav_config.json` 中，已被 `.gitignore` 全面排除，绝不会被意外提交至远程代码仓库。

---

## 🗂️ 项目文件结构

```text
wuwa_tracker/
├── app.py                         # Web 服务核心 (双端路由、后台自动同步调度)
├── webdav_backup.py               # 坚果云 / WebDAV 云端备份引擎 (纯原生实现)
├── gacha_core.py                  # 鸣潮抽卡核心 (XOR 解密、API 批量拉取、数据合并)
├── characters_db.py               # 鸣潮角色/武器元数据库与自定义持久化
├── genshin_core.py                # 原神抽卡核心 (官方 API 解析、捕获明光胜率分析)
├── genshin_db.py                  # 原神全量角色/武器元数据库 (1.0 ~ 5.x 全图鉴)
├── demo_data.py                   # 鸣潮仿真演示数据生成器
├── demo_data_genshin.py           # 原神仿真演示数据生成器
├── 启动鸣潮抽卡分析.bat            # Windows 一键自启脚本
├── data/
│   ├── gacha_records.json         # 鸣潮本地永久抽卡数据库 (只增不减)
│   ├── genshin_records.json       # 原神本地永久抽卡数据库 (只增不减)
│   ├── custom_config.json         # 鸣潮用户自定义配置 (角色/立绘/链接)
│   ├── genshin_custom_config.json # 原神用户自定义配置
│   └── webdav_config.json         # 坚果云配置 (已加 gitignore，杜绝泄露)
├── static/
│   ├── index.html                 # 现代化响应式流式看板 (Tailwind CSS + ECharts)
│   └── images/
│       └── avatars/               # 本地高清离线立绘托管目录 (支持自定义扔图)
├── .gitignore                     # Git 忽略配置 (保护个人 UID 抽卡数据与云盘凭据)
├── LICENSE                        # MIT 开源许可证
└── README.md                      # 项目双端开发与使用说明文档
```

---

## 🧩 数据兼容与备份迁移 (全量双端 + 坚果云配置)

* **📤 全量导出备份**：点击顶栏【📤 导出备份】，一键下载包含**《鸣潮》全量抽卡记录 + 《原神》全量抽卡记录 + 自定义图鉴立绘配置 + 坚果云连接配置**的统一 JSON 备份包（`gacha_full_backup_*.json`）。
* **📥 一键恢复备份**：点击顶栏【📥 恢复备份】，选择任意历史备份文件，系统将智能识别并**同时恢复抽卡数据与坚果云配置**（连同坚果云账号与应用密码一并无缝还原，换设备无需重新输入）。
* **🔄 多工具兼容**：除全量备份外，恢复入口同时向下兼容 **UIGF v3.0**、**鸣潮工坊 (Wuwa Tracker)**、**提瓦特小助手**、**Astrionyx** 单项历史文件，自动增量识别合并。
* **☁️ 坚果云一键云恢复**：点击顶栏【☁️ 坚果云备份】➔【⬇️ 从云端恢复】，免去手动传输文件的繁琐，全自动恢复双端记录与网盘状态。

---

## ❓ 常见问题 (FAQ)

<details>
<summary><b>Q1: 会不会有封号风险？</b></summary>
A: <b>绝无封号风险</b>。本工具为纯本地辅助程序，仅以只读方式读取客户端运行时产生的文本日志（<code>Client.log</code> 与 <code>output_log.txt</code>）以获取官方查询凭据，并调用官方查询 API。不注入进程、不修改游戏内存或游戏资源文件。
</details>

<details>
<summary><b>Q2: 为什么提示“未在日志中检测到抽卡链接”？</b></summary>
A: 游戏客户端只有在玩家点击卡池的【抽卡记录 / 祈愿历史】时，才会将带有临时密钥的 URL 写入本地日志。请先在游戏内点开一次抽卡记录，然后再执行同步即可。
</details>

<details>
<summary><b>Q3: 我的游戏安装在其他盘符，找不到日志怎么办？</b></summary>
A: 点击【一键从日志同步】弹出的窗口中，提供【📂 浏览选择】按钮，可以直接手动指定你的 <code>Client.log</code> 或 <code>output_log.txt</code> 路径，并勾选“记住此路径”，以后将永久自动读取。
</details>

<details>
<summary><b>Q4: 为什么我的新角色头像显示的是金色字样的印章？</b></summary>
A: 当游戏推出全新角色、且本地和外部网络未匹配到图片时，系统会启动动态艺术徽章引擎，自动生成高质感的专属 5★ 黄金流光印章，抽卡统计和保底水位依然 100% 精准计算。若需真立绘，只需将角色的图片命名为 <code>角色名.png</code> 扔到 <code>static/images/avatars/</code> 目录下即可！
</details>

<details>
<summary><b>Q5: 换浏览器或重装系统后，我的抽卡数据会丢失吗？</b></summary>
A: <b>绝不会</b>！数据不是存储在浏览器的 LocalStorage 或 Cookie 中，而是永久固化在程序服务端的 <code>data/gacha_records.json</code> 与 <code>data/genshin_records.json</code> 文件中。只要服务端目录未被删除，换任意浏览器、隐身窗口或清除浏览器缓存均无影响。<br>
若更换了新电脑或重装了操作系统，只需在新设备上打开【☁️ 坚果云备份】，输入账号与应用密码，点击【⬇️ 从云端恢复】，即可在 1 秒内完整无损地还原所有鸣潮与原神的抽卡记录！
</details>

---

## 📄 开源许可证 (License)

本项目基于 [MIT License](LICENSE) 开源。

* **免责声明**：本项目为玩家自制开源分析工具。与广州库洛科技有限公司（Kuro Games）及上海米哈游网络科技股份有限公司（miHoYo）官方无关。《鸣潮》与《原神》游戏及其相关角色立绘、图标、音频与名称等知识产权分别归各自所属公司所有。
