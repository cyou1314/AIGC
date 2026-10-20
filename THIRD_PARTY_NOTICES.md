# 来源与许可证

本私有仓库是个人工作流的版本化集合，不对全部内容授予统一开源许可证。新增个人流程与配置由仓库所有者管理；引入内容保留其原有版权和许可证。公开仓库或重新分发之前应核对逐项来源。

| 内容 | 来源/证据 | 处理 |
|---|---|---|
| auto-edit-video | 本机已安装Skill；内含MIT许可证，版权为natyang1234及贡献者 | 保留 `skills/auto-edit-video/LICENSE.txt` 和原第三方说明 |
| auto-edit-video内OpenCC | 内含许可证和字典数据 | 保留vendor目录及其许可证 |
| transcribe | 本机已安装Skill；内含Apache-2.0许可证 | 保留 `skills/transcribe/LICENSE.txt` |
| jianying-editing | 用户私有仓库 `cyou1314/jianying-editing-skill` 的本机版本 | 保留来源方法；用户已排除CLI安装/调用，现行交付为手动剪映操作与素材交接 |
| capcut-edit | 本机已安装Skill的文档/配方快照 | 未随附capcut CLI；仅作个人备份使用，未来分发前核对上游许可 |
| AIGC专业技能/知识 | 用户原工作流与本机修订 | 保留引用、来源说明、适用范围和证据边界 |
| 外部Codex插件 | 仅集成依赖与名称 | 不打包插件缓存、服务代码、账户或凭证 |
| canvas-design / frontend-design | Anthropic `anthropics/skills`，固定提交 `dbd4588f9e1033efb41dad4bef2f7947c8993d44` | 保留各Skill原LICENSE.txt与references/upstream.md；入口为2026-10-13修改版，SOURCE.json记录来源。未打包上游字体；CJK字体按当地安装与许可检查 |
| 图像导演恢复参考 | 用户Drive `agents__aigc-image-director`目录的6份已读取通用方法 | 保留方法全文与迁移索引；历史宿主/比例不覆盖当前合同。其余14份仅目录核对，私人偏好与项目历史不上传 |

初始引入的文件摘要见 `sources.json`。摘要用于追溯快照，不代表上游未来升级自动进入本仓库。

自动剪辑上游测试内有真实Studio工程和ASR逐字转录fixture。本仓库排除这些目录，保留测试代码并在没有相应私有fixture时明确跳过相关测试；不将其原始转录上传。原已安装Skill未改变，准备阶段排除的副本在仓库外可恢复归档。

2026-10-20公司标准整合：用户上传的cinematic-storyboard-optimizer v0.4.0、使用说明与ai-cinematic-music-prompt-generator用于本私有工作流的学习适配。保留来源与适用边界，仅将决策方法重写到现有导演/音频Skill；未复制包内脚本、测试、代理配置或研究原文，未安装其依赖。附件未附统一再分发许可，不宣称已获得公开再分发授权；包作者的历史访问和测试不作为本次验证证据。

2026-10-20补充公司包：seedance-25-prompt-reviewer为MIT，已保留scripts/LICENSE.prompt-review-checks及原版权说明；移植其账本脚本、两组功能测试并适配交接参考。storyboard-lines-extract两份ZIP完全同摘要，仅保留一份的规则/本地脚本/回归，未附许可证，不对其授予公开再分发权。short-drama-poster-director未附许可证，仅在私有工作流提炼规则及关系构图原型，未复制44张图库/完整剧名数据集或其作品案例。附件中的默认飞书发布及作者历史研究/验证声明不作为本次授权或实际证据。

1.3.3补充学习：用户《内循环漫解.docx》《AI 漫剧生产实践.zip》的原件与真实作品/账号截图仅本地忽略归档；提取文本、原Markdown及来源散列作为惰性参考，现行方法另行适配。script-character-intro-cards与storyboard-prompt-trimmer两个新指令包保留原ZIP供私有追溯，未附公开再分发许可；前者的方法/设计参考并入图像入口，后者原脚本仅归档，现行受限裁段助手另写并经功能验证，不声称获得原包统一开源授权。此前重复三包按摘要去重。
