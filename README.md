<div align="center">

# 真斗 · TrueStars

**紫微斗数 · 只说真话的命理**

一个会说"这个我算不了"的命理 skill —— 因为它看不起那些什么都敢算的。

`Claude Code Skill` · `紫微斗数` · `精确排盘` · `可视化命盘`

</div>

---

## 这是什么

真斗（TrueStars）是一个 [Claude Code](https://claude.com/claude-code) skill：输入生辰，它会**精确排盘**、给出**有主见、不装神**的解读，并生成一张**东方古典风格的可视化命盘**（独立 HTML，浏览器直接打开）。

它跟市面上的算命工具不一样的地方，只有一句话：

> **市面上九成的算命是一门恐惧生意——把话说得神神叨叨、无所不知，用一句"你命里有一劫"套住你，再卖你一个转运的方法。真斗站在它的对立面。**

- **技法上真专业** —— 排盘、四化、大限，用数据说话（基于 [`iztro-py`](https://pypi.org/project/iztro-py/) 精确计算，非模板套话）
- **态度上不装神** —— 不神秘化、不吓唬人、不故弄玄虚
- **边界上很清醒** —— 紫微能算什么、不能算什么，门儿清；算不了的直接说算不了

## 特点

| | |
|---|---|
| 🎯 **精确排盘** | 三合派 × 中州派方法论，十二宫 / 四化 / 大限 / 流年完整计算 |
| 🗣 **诚实人格** | 三条铁律：区分能答/不能答、用错方法当场认、命盘是概率地图不是判决书 |
| 📅 **进阶模块** | 用田宅宫四化算"哪年适合买房"、八宅命卦算个人方位、两人合盘 |
| 🎨 **古典视觉** | 米白纸感 + 朱砂红 + 赭金，印章篆刻、中英混排，老月份牌风格的可视化命盘 |
| 🖐 **手相互证** | 可选：上传手相照片，与命盘交叉验证 |
| 🔧 **校准机制** | 解读后追问 3–5 个关键问题，把准确度从 ~70% 推向 85%+ |

## 安装

将本仓库的 `skills/mingli-master/` 目录放入你的 Claude Code skills 目录：

```bash
cp -r skills/mingli-master ~/.claude/skills/
```

首次使用前安装排盘依赖：

```bash
python3 -m pip install iztro-py --user
```

## 使用

在 Claude Code 里直接说：

```
帮我看看命盘：1995年4月29日 上午10点，女，湖南郴州
```

skill 会自动触发，完成排盘 → 解读 → 生成 HTML 命盘。也支持：

- `帮我算一下事业运 / 感情 / 财运`
- `我哪一年适合买房？`（田宅宫流年模块）
- `帮我和对象合个盘`（合盘模块）

## 项目结构

```
skills/mingli-master/
├── SKILL.md                      # skill 主定义与工作流
├── scripts/
│   ├── calculate_chart.py        # 排盘引擎（含真太阳时校正）
│   ├── generate_html.py          # 可视化命盘生成器
│   ├── calculate_horoscope.py    # 流年四化飞宫（买房/婚姻择年、合盘）
│   └── calculate_bazhai.py       # 八宅命卦方位（风水模块）
└── references/
    ├── interpretation_guide.md   # 解读人格与三条铁律（灵魂）
    ├── stars_reference.md        # 十四主星 + 辅煞速查
    ├── four_hua_reference.md     # 四化飞星引擎
    └── extended_modules.md       # 买房择年 / 八宅方位 / 合盘
```

## 设计原则

真斗不预言死亡、不制造恐惧、不替代人生决策。它只说"这个格局倾向于……"，永远把行动权交还给你：

> 象由心生 · 命由象推。命盘显示可能性，行动决定现实。

## 致谢

排盘计算基于开源库 [iztro-py](https://pypi.org/project/iztro-py/)。

## License

[MIT](LICENSE) © [katrinazeng](https://github.com/katrinazeng)

<div align="center">
<br>
<code>真</code>　真斗 · TrueStars
</div>
