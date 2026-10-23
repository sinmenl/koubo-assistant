# 践行营 · 流水账→口播 分发包

给同伴用时：**发整个压缩包**，不要只发 `AGENTS.md`。

也可以直接分享 [GitHub 项目链接](https://github.com/sinmenl/koubo-assistant)，让对方的 Agent 按 [INSTALL.md](INSTALL.md) 安装。安装后说「用口播助手」开始，说「更新口播助手」获取后续更新。原有压缩包用法仍可使用；需要持续更新时用 Git 安装。

> 主文件已瘦身，默认路线会自动做 Don 哥的共鸣与衔接检查；其余进阶功能说关键词才加载（见下方关键词表）。

用户选定观点后，先按原流程串联相关原文，再自动调用 `dbs-resonate` 检查这份半成品，然后继续原门禁。通过门禁并按原五段结构成稿后，自动调用 `dbs-script-flow` 检查衔接；只检查不代表自动改稿。未选观点时不提前检查，未成稿时不运行衔接检查。原来的旁支卡片、风格与 memory 规则继续执行。

## 一图看懂

不知道发什么指令？先看 `口播助手-进阶指令.jpg`：我想要什么，就发对应的指令。

## 包里有什么

| 文件 | 作用 |
| --- | --- |
| `AGENTS.md` | 瘦身主文件：硬边界 + 默认路线（选型、串联、门禁、五段口播、卡标题、结束写风格与 memory）+ 关键词表 |
| `skills/jianxingying/` | 按需加载的进阶步骤：存卡、翻旧账、共鸣、顺一下、标题、灵感、复盘、风格/memory 细则、故障处理 |
| `skills/linggan/` | 胡子哥「灵感炼金炉」 |
| `skills/dongjian-card/` | 胡子哥「知识卡片锻造」 |
| `skills/koubo-huzige/` | 胡子哥「口播炼金」（黄金骨架） |
| `skills/short-video-diagnosis/` | 短视频诊断教练（错题本） |
| `skills/dbskill/` | Don 哥 [dbskill](https://github.com/dontbesilent2025/dbskill) 全套（含 dbs / resonate / script-flow 等），**已放进包内** |
| `style-profiles/` | 风格进化档案（只记文风；按用户一人一份；含 `_template.md`） |
| `memory/` | 践行记忆（记「这期做了什么」；含 `_README.md`、`_template.md`；供 `/复盘` 7 天回顾） |


## 安装（写给收到包的人）

1. 解压到你的 **Agent 项目根目录**（Cursor 打开的那个文件夹）。
2. 确认结构：

```text
你的项目/
├── AGENTS.md
├── README.md
├── skills/
│   ├── linggan/SKILL.md
│   ├── dongjian-card/SKILL.md
│   ├── koubo-huzige/SKILL.md
│   ├── short-video-diagnosis/SKILL.md
│   ├── jianxingying/       ← 按需文件：说关键词才读
│   │   ├── cards.md  history.md  resonate.md  flow.md  title.md
│   │   ├── linggan.md  review.md  style.md  memory.md
│   │   └── troubleshooting.md
│   └── dbskill/          ← Don 哥整包，解压即用
│       ├── dbs/
│       ├── dbs-resonate/
│       ├── dbs-script-flow/
│       └── …
├── style-profiles/       ← 风格档案（只记文风；可空；Agent 会按人写入）
│   └── _template.md
└── memory/               ← 践行记忆（口播结束记一条；/复盘 看近 7 天）
    ├── _README.md
    └── _template.md
```

3. 对 Agent 说「按 AGENTS.md 跑」或直接发流水账 / 输入 `/口播`。
4. 可选自建：`inbox/` 放历史分享，`output/` 放成稿。

## 关键词表

| 关键词 | 作用 | 读的文件 |
| --- | --- | --- |
| `/口播` | 主流程（默认路线，或直接发流水账） | `AGENTS.md` |
| `/存卡` | 未选中的点展开为洞见卡四件套 | `skills/jianxingying/cards.md` |
| `/翻旧账` | 钉回时刻 + 完整回顾历史分享 | `skills/jianxingying/history.md` |
| `/共鸣` | 默认在选定观点并串联后自动检查，也可单独要求深度诊断（dbs-resonate） | `skills/jianxingying/resonate.md` |
| `/顺一下` | 默认在成稿后自动检查，也可单独要求顺稿（dbs-script-flow） | `skills/jianxingying/flow.md` |
| `/标题` | 标题封面开头（dbs-title-cover-intro） | `skills/jianxingying/title.md` |
| `/灵感` | 材料薄时三刀炼灵感 | `skills/jianxingying/linggan.md` |
| `/复盘` `/7天复盘` | 扫 memory 近 7 天（可后跟用户标识） | `skills/jianxingying/review.md` |
| `/诊断` | 短视频数据诊断 | `skills/short-video-diagnosis/SKILL.md` |
| 「按胡子哥口播」 | 黄金骨架那套（与五段骨架二选一） | `skills/koubo-huzige/SKILL.md` |

## 来源说明

胡子哥（姜胡说）skill 摘自其「0摩擦一条龙：灵感+洞见卡+口播」公开分享；短视频诊断提示词来自用户提供的原文。转发给同伴时请注明出处，尊重原作者更新。

内附 Don 哥 dbskill 的出处及许可见 [SOURCE.md](skills/dbskill/SOURCE.md) 和 [LICENSE](skills/dbskill/LICENSE)。本项目安装入口只注册口播助手，所需 Don 哥模块继续从包内按原流程读取。
