# 鸣潮抽卡分析系统 (Wuthering Waves Convene Tracker)

<p align="center">
  <img src="https://fastly.jsdelivr.net/gh/ryanbenson/wuthering-waves-assets@master/images/Hiyuki.png" width="100" height="100" alt="Logo" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(245, 158, 11, 0.3);" />
</p>

<p align="center">
  <b>一款轻量、极速、零外部依赖的《鸣潮》本地抽卡分析与保底水位可视化系统</b><br>
  鸣潮工坊风格流式看板 · 180天数据兼容与永久保存 · UIGF多格式导入 · 自定义角色与头像配置中心
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Standard%20Lib)-success?style=flat-square" alt="Zero Dependencies" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/Format-UIGF%20v3.0%20Compatible-orange?style=flat-square" alt="UIGF" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
</p>

---

## 💡 为什么选择本项目？

1. **⚡ 真正的零依赖（Zero Dependencies）**
   - 全套后端基于 Python 标准库原生实现（`http.server`, `urllib`, `json`），**无需 `pip install` 任何第三方包**！下载解压后双击即可秒开。
2. **🛡️ 180天数据兼容与本地永久保留（只增不减原则）**
   - 库洛官方服务器会在 180 天（6 个月）后物理清除抽卡历史记录。
   - 本工具使用高精度复合指纹（`时间戳 + 单抽位次 + 物品ID`）进行增量比对，**本地数据库永久留存，绝不随官方服务器清理而丢失**。即使半年或一年回坑，历史保底状态与垫抽水位依然无缝衔接。
3. **📂 灵活支持任意日志目录（弹窗自选与文件浏览）**
   - 鸣潮的安装盘符与路径因人而异。点击“一键同步”时弹出配置窗口，支持直接输入文件夹路径或点击【📂 浏览选择】任意位置的 `Client.log`，并支持记住路径免重复配置。
4. **🔄 广泛的数据兼容性（UIGF 3.0 / 鸣潮工坊 / Astrionyx）**
   - 内置格式转换引擎，支持一键导入主流工具（**UIGF 标准格式**、**鸣潮工坊 Wuwa Tracker**、**Astrionyx** 备份），补齐早前超过 180 天未同步的历史断档。
5. **📊 鸣潮工坊同款 100% 满屏大看板**
   - 横向水流出金条形图、已垫抽数水位条、出金抽数评价、专属红色圆印 **“歪”** 标记、小保底 (50/50) 与大保底 (100% UP) 智能状态监控。
6. **📜 全量日志独立视图与分页浏览**
   - 独立全量流水视图，直接与顶部卡池分类联动；默认 20 条/页，支持首页/尾页快速导航，支持按 5★ / 4★ 星级过滤及名称搜索。
7. **⚙️ 可视化自定义控制中心**
   - 点击顶栏【⚙️ 自定义配置】，随时修改角色名称、专属头像立绘链接（带实时图片预览）、资源数值 ID 绑定、卡池归属，以及外服客户端别名映射（例如 `Hiyuki` ➔ `绯雪`）。
8. **🌏 国服与国际服全服适配**
   - 自动识别海外服（港澳台/日服/美服等）与国服不同的鉴权 API，角色数据库覆盖全共鸣者与专武。

---

## 🖥️ 界面展示

* **综合欧非看板**：顶部紧凑展示小保底不歪率、总金数、UP角色平均抽数、UP武器平均抽数与出金图鉴矩阵。
* **六大卡池切换**：角色活动唤取、武器活动唤取、角色常驻、武器常驻、新手唤取、新手自选唤取。
* **可视化双视图**：
  * **📊 抽卡分析看板**：左侧横向条形出金流水 + 右侧水位进度与 ECharts 出金区间分布图。
  * **📜 单独全量日志**：清晰表格分页展示每一抽历史，默认 20 条/页。
* **⚙️ 自定义控制弹窗**：实时修改头像、新增条目、保存专属抽卡 URL、映射外服别名。

---

## 🚀 快速开始

### 0. 环境准备 (Prerequisites)
* **Python 环境**：需要安装 **Python 3.8 及以上版本**（推荐 Python 3.10 ~ 3.12）。
  * 官方下载地址：[Python 官方下载](https://www.python.org/downloads/)（或直接在 Windows 微软应用商店搜索 Python 安装）。
  * ⚠️ **重要安装提醒**：在 Windows 安装 Python 时，**务必在安装界面勾选底部的 `Add python.exe to PATH`**（将 Python 添加到系统环境变量），否则双击脚本或命令行可能会提示无法识别 `python` 命令。
* **零依赖说明**：
  * 本项目完全基于 Python 标准库开发，**无需运行任何 `pip install` 命令**，环境安装完毕即可直接开箱运行！

### 方式 A：Windows 一键启动（推荐）
1. 下载或克隆本项目仓库到本地。
2. 双击项目根目录下的 **`启动鸣潮抽卡分析.bat`**。
3. 程序会自动检测本地 Python 环境，启动本地 Web 服务并在默认浏览器中自动弹出分析面板：
   ```text
   http://127.0.0.1:8765
   ```

### 方式 B：命令行运行（跨平台 Windows / macOS / Linux）
```bash
git clone https://github.com/time2110/Mingchao_Card_Drawing_Analysis_System.git
cd Mingchao_Card_Drawing_Analysis_System
python app.py
```
终端输出运行日志后，在浏览器访问 `http://127.0.0.1:8765` 即可。

---

## 📖 如何同步游戏内抽卡数据？

1. 启动《鸣潮》游戏客户端。
2. 按 `F3` 键或点击进入游戏内 **【唤取】** 页面。
3. 点击任意卡池下方的 **【唤取记录】** 按钮进入历史记录窗口（游戏此时会在本地日志中写入包含时效凭证的 URL）。
4. 切换到本分析系统网页，点击右上角 **【一键从日志同步】**。
5. 在弹出的路径配置框中确认或选择你的 `Client.log` 所在目录（系统会自动嗅探并提供实时检测回显），点击 **【确认并开始同步】** 即可！

> 💡 **小贴士**：
> * 官方凭据的有效期通常约为 30 分钟。如果同步时提示“链接已过期”，只需在游戏内重新打开一次【唤取记录】即可再次一键同步。
> * 如果不想每次读取日志，可在【⚙️ 自定义配置】中粘贴专属链接并永久保存。

---

## 🗂️ 项目文件结构

```text
wuwa_tracker/
├── app.py                     # 本地 Web 服务核心 (纯 Python 标准库实现)
├── gacha_core.py              # 抽卡解析引擎、XOR 解密算法、增量复合去重
├── characters_db.py           # 共鸣者/武器属性数据库与自定义配置持久化
├── demo_data.py               # 仿真测试与演示数据生成器
├── 启动鸣潮抽卡分析.bat        # Windows 双击一键启动脚本
├── Client_log_解码工具_v3.bat   # 专用日志解码与 URL 提取工具
├── data/
│   ├── gacha_records.json     # 本地永久抽卡数据库 (只增不减)
│   └── custom_config.json     # 用户自定义配置 (角色/头像/别名/链接)
├── static/
│   └── index.html             # 现代化单页看板 (Tailwind CSS + ECharts)
├── .gitignore                 # Git 忽略配置 (保护私有 UID 抽卡数据)
├── LICENSE                    # MIT 开源许可证
└── README.md                  # 项目中英文说明文档
```

---

## 🧩 数据兼容与迁移说明

### 1. 导入历史数据
如果你在开服初期（超过 180 天前）曾使用过其他抽卡记录工具，并将数据导出为了 JSON 文件：
1. 点击右上角顶栏的 **【📥 导入备份】** 图标。
2. 选择历史备份文件，系统支持解析：
   * **UIGF v3.0 标准格式** (`info` + `list`)
   * **鸣潮工坊（Wuwa Tracker）** 导出的备份文件
   * **Astrionyx** 备份文件
   * **本系统原生备份文件**
3. 系统将自动按卡池拆分、提取字段、智能匹配角色映射并合并入库。

### 2. 导出备份
随时点击右上角 **【📤 导出备份】** 图标，即可一键下载格式规范的完整 JSON 文件，换电脑或备份极其便捷。

---

## ❓ 常见问题 (FAQ)

<details>
<summary><b>Q1: 为什么提示“未在日志中提取到抽卡链接”？</b></summary>
A: 鸣潮客户端只有在玩家打开【唤取记录】页面时才会将鉴权链接写入日志。请先在游戏里点开一次抽卡记录，然后再点击本工具的【一键同步】。
</details>

<details>
<summary><b>Q2: 我的游戏安装在 D 盘或自定义盘符，怎么配置？</b></summary>
A: 点击【一键从日志同步】时会弹出配置窗口，点击【📂 浏览选择】按钮，直接点选你的 <code>Client.log</code> 即可，并勾选“记住此目录为默认路径”，以后即可永久自动读取。
</details>

<details>
<summary><b>Q3: 新版本出了新限定角色，看板里没头像怎么办？</b></summary>
A: 点击右上角【⚙️ 自定义配置】，在“角色与头像”标签页输入新角色名称和任意网络图片链接，点击保存即可实时生效，无需等待代码更新！
</details>

<details>
<summary><b>Q4: 会不会有封号风险？</b></summary>
A: 绝无封号风险。本工具为纯本地离线辅助分析程序，只以只读方式读取游戏产生的文本日志 <code>Client.log</code> 并调用官方只读查询 API，不修改任何游戏内存或本地游戏数据文件。
</details>

---

## 📄 开源许可证 (License)

本项目基于 [MIT License](LICENSE) 开源。

* 免责声明：本项目为玩家自制开源工具，与库洛游戏（Kuro Games）官方无关。《鸣潮》游戏及其相关角色立绘、图标、名称等素材的版权均归属广州库洛科技有限公司所有。
