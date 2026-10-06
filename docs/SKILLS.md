# Skill目录与调用边界

本仓库包含17个本地Skill；9种生产路由不是9个都能独立生成的本地引擎。外部专家Skill随插件提供，不打包在这里。

| 本地Skill | 职责 | 常用配合 |
|---|---|---|
| [aigc-production-router](../skills/aigc-production-router/SKILL.md) | 判断类型、当前动作与主Skill；检查路由合同 | 项目页、类型profile |
| [aigc-project-prompt-loop](../skills/aigc-project-prompt-loop/SKILL.md) | 多轮叙事项目、分镜/提示词与版本闭环 | 编剧、导演、静帧、QC |
| [aigc-screenwriter](../skills/aigc-screenwriter/SKILL.md) | 剧本写作、诊断、改编、压缩与因果结构 | 项目循环、导演 |
| [aigc-manga-video-director](../skills/aigc-manga-video-director/SKILL.md) | 参考视频分析、镜头、动作与分镜指导 | ffmpeg、转录、编剧 |
| [aigc-image-director](../skills/aigc-image-director/SKILL.md) | 静帧、概念、角色/商品/海报设计指导 | 实际生图工具、图片替换 |
| [aigc-commercial-content](../skills/aigc-commercial-content/SKILL.md) | 广告/UGC/商品的事实、卖点、脚本与渠道 | 对应商业生成专家 |
| [aigc-audio-production](../skills/aigc-audio-production/SKILL.md) | 配音、音乐、音效与音频交付协调 | 转录、声音服务、ffmpeg |
| [audio-to-prompt](../skills/audio-to-prompt/SKILL.md) | 音频的词句/情绪/节奏转视觉提示词 | transcribe、导演 |
| [transcribe](../skills/transcribe/SKILL.md) | 语音转文字、时间信息/说话人按能力 | 合法转录API、本地预处理 |
| [ffmpeg](../skills/ffmpeg/SKILL.md) | 抽帧、代理、音频提取与确定性预处理 | 导演、转录、后期 |
| [prompt-optimizer](../skills/prompt-optimizer/SKILL.md) | 指令澄清、约束冲突与工具专用提示优化 | 编剧/导演或目标工具 |
| [aigc-output-qc](../skills/aigc-output-qc/SKILL.md) | 实际视频与连接镜头验收、返修判定 | 真实视频、分镜、生成记录 |
| [storyboard-image-replacer](../skills/storyboard-image-replacer/SKILL.md) | 图片分镜板按格替换，保留其他区域 | 已有板、目标图、图像工具 |
| [jianying-editing](../skills/jianying-editing/SKILL.md) | 安全检查/编辑现有剪映或CapCut工程 | CLI、备份、编辑器验收 |
| [capcut-edit](../skills/capcut-edit/SKILL.md) | CapCut CLI操作配方与工程编辑 | 已确认CLI结构及工程副本 |
| [auto-edit-video](../skills/auto-edit-video/SKILL.md) | 本地原始口播自动保守粗剪 | 本地媒体、内部工程、导出 |
| [obsidian-codex-knowledge-loop](../skills/obsidian-codex-knowledge-loop/SKILL.md) | 持久项目页、生成/交付回执、收尾与知识升级 | 所有类型、实际证据 |

## 选用规则

- 新项目不明确：路由Skill先判断；已有专家请求直接使用专家。
- 新故事：编剧；已确认剧本做镜头：导演；连续多轮叙事：项目循环协调。
- 实拍原口播粗剪：auto-edit-video；已有剪映草稿：jianying-editing；只换编码/抽帧：ffmpeg。
- 只做海报：image-director协调，按需要调用实际生图/设计工具；不套用叙事全流程。
- 只要讲稿/提示词不触发生成；真实成片请求需要实际文件与相应验收。
- QC Skill当前专门负责视频，不自动覆盖模型、音乐、表格；这些由对应分支验收。
- 音频转录、声音生成、音乐生成、音频转视觉是不同能力，不能因为名称相近互相替代。

## 维护结构

每个Skill以 `SKILL.md` 为入口；说明里的触发范围应准确，操作细节放 `references/`，确定性工作放 `scripts/`，关键行为放 `tests/`。只读取本次任务必要参考，避免每次把所有资料加载。

新增生产域先更新 `production-profiles.json` 和相关测试，再增加真正有价值的Skill。新增Skill后同步验证脚本期望名单、README数量、本页、来源与CHANGELOG。不要仅堆叠重复包装。

正式变更必须回答：解决哪个重复问题、是否影响旧项目、必要依赖、失败停点、实际证据、如何回滚。多个项目重复成功后才能将候选经验晋级为默认规则。
