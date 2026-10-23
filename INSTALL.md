# 发链接安装，之后一句话更新

把下面这段发给能操作本机文件与命令的 Agent：

> 请安装这个口播助手：https://github.com/sinmenl/koubo-assistant 。先读取 README.md 和 INSTALL.md，按项目的安装入口操作；装好后告诉我如何开始。以后我说「更新口播助手」时，从这个仓库更新，保留我的记忆、风格和稿件。

使用时说「用口播助手」，再发流水账。以后说「更新口播助手」。使用者仍需要自己的 Agent 或模型服务；安装本项目不会附送模型或自动打开后台服务。

## 给执行安装的 Agent

需要 Git 与 Bash。macOS／Linux 可直接运行；Windows 使用 Git Bash。若缺少这些工具或安装权限，如实说明当前缺项，不把下载文件说成已安装成功。

1. 先检查已安装的 `koubo-assistant` Skill 入口与它指向的真实目录。已有同源安装时直接使用该目录；用户要更新则执行更新，不重复下载。已有同名其他来源或真实目录时保留并报告冲突。
2. 首次安装将完整仓库克隆到独立的稳定目录。默认建议 `~/.local/share/koubo-assistant`，也可使用用户指定的空目录。不要克隆到现有项目根、不要覆盖使用者原有 `AGENTS.md`。公开仓库无需项目作者提供任何账号凭证。

```bash
git clone --branch main --single-branch https://github.com/sinmenl/koubo-assistant.git "$HOME/.local/share/koubo-assistant"
```

若默认目录已存在但不是已确认的同源安装，停止并说明，不删除重装。父目录不存在时先创建该父目录。不要把上述路径硬套到使用者指定的位置。

3. 在克隆所得的项目根运行：

```bash
bash scripts/manage.sh install
bash scripts/manage.sh status
```

脚本复用包内的 `dbs-install-skill` 安装器，只将根 `SKILL.md` 注册为 **koubo-assistant**。公共入口为 `~/.agents/skills/koubo-assistant`，安装器还会为本机已存在、需专属入口的 Agent 建立链接；原有真实目录或其他来源不会被覆盖。不要对整仓库执行批量 `skills add --all`，也不需要另外安装整套 dbskill。

4. 安装成功须确认：脚本退出成功，入口指向当前克隆目录；从入口能实际读到本项目 `AGENTS.md` 及包内 `dbs-resonate/SKILL.md`、`dbs-script-flow/SKILL.md`。再确认当前宿主已发现 `koubo-assistant`；有些宿主需要刷新 Skill 列表或新开会话。在宿主发现之前，只报告文件／入口已安装，不能声称当前会话已能自动调用。

若宿主不支持安装器提供的入口，可直接打开克隆目录，并明确说「读取这里的 AGENTS.md，按口播流程执行」。这时更新需在该目录发起，不承诺在任意聊天中自动识别。

## 更新

已发现入口的 Agent 收到「更新口播助手」后，先通过 `koubo-assistant` 入口定位原克隆目录，再运行：

```bash
bash scripts/manage.sh update
```

脚本核对来源并获取 `main`，只允许在干净的 `main` 上快进更新。本地规则有修改、出现额外提交、远端与本地分叉或可能占用个人文件时停止，不自动覆盖、合并或删除。不要以 `reset --hard`、`clean`、强制检出、自动暂存或重新解压覆盖来绕过停止。

个人文件继续按原流程保存在本项目 `memory/`、`style-profiles/`；`inbox/` 与 `output/` 可放资料和成稿。这些个人文件不随常规更新提交或上传，原有模板仍由项目维护。若使用者自行改了 `AGENTS.md` 等跟踪文件，需先由使用者决定如何保留，再处理更新。

更新后报告实际新旧版本，重新读取新说明。入口是指向同一目录的链接，正常更新不需要重新安装，也不需要重新下载全部第三方 Skill。

压缩包解压不带 Git 更新记录。已有压缩包使用者应另行克隆安装，再按本人意愿复制自己的记忆／风格／稿件；不要在旧目录直接覆盖安装。不要把历史标签 `v0.2.0` 当成当前版本，安装与更新均跟随 `main`。
