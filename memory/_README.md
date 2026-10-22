# 会话记录模板说明

本目录只放可分发的说明与模板。个人会话不再写在这里；旧个人文件只有用户明确指定迁移时才读取。

## 默认不记录

复制根目录的 `config.example.json` 为 `local/config.json` 后按需配置：

| 配置项 | 含义 |
| --- | --- |
| `profile_id` | 当前身份的安全标识；不能用路径或 `..`，多人分别设置 |
| `record_sessions` | 默认 `false`；明确启用后才在本期结束时记录 |
| `learn_style` | 默认 `false`；独立控制是否保存文风反馈 |
| `timezone` | 默认 `Asia/Shanghai` |

用户只说「保存这期」时，只保存本期，不自动开启长期记录。已经确定的身份可以沿用；未确定时不能写到公共 `default.md`。

## 个人文件放哪里

```text
local/                             # 被 Git 忽略，不进入上传包
├── config.json                    # 个人设置
├── inbox/                         # 用户主动放入的原始材料，可选
├── sessions/{profile_id}/
│   └── {session_id}.md             # 一期一文件
└── style-profiles/{profile_id}.md  # 只记有用户证据的文风偏好
```

一期修改多次仍用同一个 `session_id`，更新当前内容并保留变化说明。会话模板见 [_template.md](_template.md)，写入细则见 [memory.md](../skills/jianxingying/memory.md)。

对 Agent 说 `/复盘` 或 `/7天复盘` 可读取当前授权身份的近七天记录。成稿、拍摄、发布是不同状态，未反馈时拍摄／发布状态为「未知」。记录缺失时也可以提供材料直接复盘，不必先开启自动记录。
