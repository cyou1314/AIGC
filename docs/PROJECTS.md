# 项目、资产与交接合同

## 存储分层

| 位置 | 内容 | 是否进入本仓库 |
|---|---|---|
| Git仓库 | 通用Skill、代码、知识、模板、测试 | 是 |
| Obsidian/Codex目录 | 真实项目状态、决定、待跟进、个性化记忆 | 否，独立备份 |
| 项目素材目录 | 原图、原音频、原视频、权威原文、授权资料 | 否 |
| 输出目录 | 生成候选、采用版、编辑工程、导出、QC | 否 |
| 机器配置/服务账户 | 本机路径、登录与凭证 | 否 |

同一项目不允许多个页面同时声称权威；明确权威资料顺序、最新采用版本与唯一下一步。文件命名可用 `项目_资产ID_版本_用途`；版本升级不直接覆盖旧候选。

## 快速与完整项目页

小任务用[快速模板](../templates/project-quick.md)：目标、权威输入、生产类型、主Skill、约束、当前状态、交付、下一步。

系列作品或复杂项目用[完整模板](../templates/project-full.md)：加入预算、角色/资产Bible、镜头/声音/模型合同、来源、回执、验收、变更、未解决事项。深度按风险选择；不要为了填满表而凭空生成信息。

## 状态脚本

所有路径参数加引号。下例在仓库根目录运行，按实际Python命令替换；默认路径从安装配置或AIGC环境变量读取。

```text
python skills/obsidian-codex-knowledge-loop/scripts/project_state.py init --name "商品主图测试" --domain image --goal "4:5商品主图，保留原标签" --next "读取商品参考并确认精确文字" --deliverable "PNG"
python skills/obsidian-codex-knowledge-loop/scripts/project_state.py validate --project "PROJECT_PAGE_ABSOLUTE_PATH" --check-files
```

类型值为：`pending`、`narrative`、`image`、`marketing`、`presenter`、`post`、`audio`、`three-d`、`knowledge`、`digital`。未知类型不能猜，应先pending。`--vault` 和 `--output-root` 可覆盖默认路径。已有同名页面不覆盖，确需重建时 `--force` 会先备份；通常应更新快照而不是重建。

登记生成回执：

```text
python skills/obsidian-codex-knowledge-loop/scripts/project_state.py receipt --project "PROJECT_PAGE_ABSOLUTE_PATH" --block "image-01" --prompt-version "v1" --file "OUTPUT_ABSOLUTE_PATH" --status "候选"
```

登记交付：

```text
python skills/obsidian-codex-knowledge-loop/scripts/project_state.py delivery --project "PROJECT_PAGE_ABSOLUTE_PATH" --item "主图PNG" --version "v1" --file "OUTPUT_ABSOLUTE_PATH" --kind "文件" --qc "未请求"
```

真实路径必须指向非空文件。状态脚本验证文件与合同，不评价审美、不听音、不验证3D拓扑，不能自动把候选标成最终成片。更多参数先运行对应子命令 `--help`。

## 不同资产的必要合同

- 镜头：镜头ID、入出时间、人物/空间、动作原因、首尾状态、声音、提示词版本、采用文件。
- 图像：用途、像素/比例、主体身份、文字、参考职责、允许修改区域、透明/颜色需求。
- 音频：真实文本、语言、音色/授权、实测时长、采样率、声道、分轨、试听结论。
- 模型：单位/轴向、目标软件、格式、拓扑/面数、UV/材质、骨骼/动画、导入结果。
- 文档：权威来源、结构、编辑格式、引用、渲染/公式检查。
- 数字产品：技术栈、运行步骤、配置名而非密钥、核心用户路径、测试、部署访问证据。

## 跨Skill交接

使用[handoff.yaml](../templates/handoff.yaml)，至少写来源/路径/版本、输入职责、目标、必须保留、允许改变、输出、验收、下游Skill。禁止把用于构图的参考自动当人物身份，把预览自动当交付，把未经证实的故事版本当canon。

## 收尾与知识演进

只持久记录可复用背景、决定、项目状态和有证据的经验；不要转储聊天。失败经验注明原因、适用范围与版本，成功候选跨项目重复验证后再晋级。未完成项目写TODO/open-loops，并保留唯一下一步。

密钥和敏感隐私不进入记忆。记录真实制作成本与耗时，但不把一次成功/失败推广成某个服务的永久质量结论。
