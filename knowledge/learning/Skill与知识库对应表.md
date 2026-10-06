# Skill 与知识库对应表

> Skill 执行任务，知识页提供判断标准，项目页保存事实与证据。

跨类型总入口：`aigc-production-router` → [[agent/跨类型AIGC生产工作流]]。商业生产使用 `aigc-commercial-content`，独立声音生产使用 `aigc-audio-production`；R0–R8只按需要复用。

| 线路 | 任务 | 主 Skill / 工具 | 对应知识 | 完成证据 |
|---|---|---|---|---|
| R0 | 项目启动、恢复、收尾 | `obsidian-codex-knowledge-loop` | [[AIGC项目统筹与提示词能力]] | 项目状态、路径和下一步已回写 |
| R1 | 剧本、人物、场景、对白 | `aigc-screenwriter` | [[编剧与剧情拆解能力]] | 结构或文本达到本轮目标 |
| R2 | 视频分析、分镜、运镜 | `ffmpeg`、`aigc-manga-video-director` | [[AIGC导演能力]]、[[镜头语言与分镜能力]] | 有镜头分析、分镜或提示词 |
| R3 | 图像生成与修改 | `aigc-image-director` → `imagegen`/所选工具、`storyboard-image-replacer` | [[图像导演与视觉设计能力]] | 实际图片及请求范围的视觉核验 |
| R4 | 转写、声音与表演 | `transcribe`、`audio-to-prompt` | [[声音情绪与表演能力]] | 有音频事实、转写或声音方案 |
| R5 | 提示词诊断与修订 | `prompt-optimizer` | [[AIGC项目统筹与提示词能力]] | 冲突消除，目标和约束清楚 |
| R6 | 成片验收与返修 | `aigc-output-qc` | [[成片验收与返修能力]] | 实际成片和明确验收结论 |
| R7 | 知识整理与周复盘 | `obsidian-codex-knowledge-loop` | [[知识晋级与淘汰规则]] | 判重、分类和证据更新完成 |
| R8 | 创建或升级 Skill | `skill-creator` | [[Skill创建与知识回写流程]] | 结构与真实行为验证通过 |

## 证据状态

| 状态 | 可证明 | 不能证明 |
|---|---|---|
| 文本完成 | 脚本、分镜、提示词或规则存在 | 已生成结果 |
| 文件存在 | 文件可读取 | 内容合格 |
| 结果生成 | 图片、视频或音频实际存在 | 已符合目标 |
| QC 通过 | 已有对照和验收结论 | 其他版本也通过 |

## 回写位置

- 当前任务事实与单次经验候选 → `projects/`
- 跨项目方法 → `learning/`
- 稳定流程与治理规则 → `agent/`
- 可触发、可执行、可验证的重复能力 → `{{SKILL_ROOT}}/`

当前 Skill 根目录：`{{SKILL_ROOT}}/`。执行前以实际安装清单为准。
