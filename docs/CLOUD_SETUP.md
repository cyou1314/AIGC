# Codex 云端自动加载与验收

仓库 `skills/` 是17个Skill的唯一源码。初始化器把完整目录安全安装到 `$HOME/.agents/skills`，保留references/scripts/tests；配置与登记文件在 `$HOME/.agents`。不改平台CODEX_HOME，不下载依赖，不调用媒体生成，不自动发布GitHub。

官方依据：[本地Skill发现路径](https://learn.chatgpt.com/docs/build-skills)、[AGENTS.md范围与优先级](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[云端setup与maintenance](https://learn.chatgpt.com/docs/environments/cloud-environment)。这些文档描述支持的机制，不替代当前网页运行器的真实验收。

## 网页环境设置

先发布包含这些脚本的版本，再选择cyou1314/AIGC环境。在Setup script（也可能显示install_script）和Maintenance script字段中保存同一份 `scripts/cloud-init.sh` 的完整内容。若现有设置有其他必要步骤，保留它们并合并，不盲目覆盖。start_skill不是这套源码中的正式配置接口；若界面另有启动Skill选项，需按该平台说明核对，不能凭名字假定它执行Bash。

可以保存以下完整调用脚本，适用于仓库已经含1.1.1或更高版本的启动阶段：

```bash
#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${AIGC_REPO_ROOT:-}" ]]; then
  aigc_repo="$AIGC_REPO_ROOT"
elif [[ -f "scripts/cloud-init.sh" ]]; then
  aigc_repo="$PWD"
elif [[ -f "/workspace/AIGC/scripts/cloud-init.sh" ]]; then
  aigc_repo="/workspace/AIGC"
else
  echo "AIGC checkout unavailable; configure AIGC_REPO_ROOT." >&2
  exit 2
fi
bash "$aigc_repo/scripts/cloud-init.sh"
```

设置界面可选环境变量：AIGC_REPO_ROOT指向实际checkout、AIGC_WORKSPACE指向外部工作区、AIGC_VAULT/AIGC_OUTPUT_ROOT仅在需要不同路径时设置。默认工作区是仓库父目录下AIGC-workspace。不要依赖setup中的export传给agent阶段；运行路径已存入共享JSON配置。现有AIGC_CONFIG若指向另一安装，初始化器停止，需先在环境设置对齐。

本任务没有网页环境设置的读取/写入API，无法检查或保存远端install_script/start_skill实际值。只有用户在该环境中保存设置后，才能证明平台真正挂接了初始化流程。缓存恢复同样运行maintenance；初始化器会恢复缺失的受管Skill，已有本地修改会阻塞并保留。

## 指令范围

仓库AGENTS.md适用于该仓库任务。初始化器在仓库父目录AGENTS.md追加一个有标记的条件式入口，保留其他文本和备份；已被用户改动的AIGC标记块会停止而不覆盖。该入口只覆盖适用的工作区任务，并非任意目录的全局指令。

真正的全局规则由当前CODEX_HOME中的AGENTS.override.md或AGENTS.md提供。当前CODEX_HOME由平台管理，因此本流程不写入它。若需要工作区外全局使用，可在平台提供的自定义指令界面安全追加如下规则；若没有该界面，由管理员把同样规则合并到受支持的全局指令来源，不应写一个不会加载的旧home文件冒充成功：

```text
仅对AIGC制作或AIGC工作流维护任务应用这些规则，其他任务保持原流程。
按已发现的AIGC Skill名称与描述调用；源码在cyou1314/AIGC的skills目录。
配置读$HOME/.agents/aigc-workflow.json，仅在项目记忆需要时读配置vault的AGENTS.md。
新/混合项目先用aigc-production-router；明确专家与已有项目优先。
Seedance镜头导演用aigc-manga-video-director；图片设计/编辑用aigc-image-director；
已有剪映工程用jianying-editing。保留源素材与用户修改，不擅自生成、上传或发布。
```

## 安全与路径

同名Skill有差异且不受本安装器管理时，在任何运行时改动前停止，列出相对差异文件名。已托管Skill被编辑同样停止。确认迁移前手动审阅，不在setup里加adopt-existing/replace-local。

已有知识页只替换已知运行时路径占位符，保留自定义文本与备份；源码模板保持占位符。已有个人知识与新版模板不同则进入.incoming，不自动把新版覆盖到个人页。符号链接运行时目的路径被拒绝，避免写穿到另一目录。本流程选安全副本而非链接发布。

仓库doctor、安装版状态工具通过共享解析器找到同一配置；显式AIGC_CONFIG可用于其他安装布局。Windows/macOS继续使用跨平台Python安装器；cloud-init.sh专供Bash云端环境（本地Windows运行需Git Bash），不在PowerShell直接执行。

## 零生成验收

```bash
python3 scripts/validate.py
python3 scripts/check_codex_discovery.py
python3 scripts/doctor.py
```

check_codex_discovery使用Codex app-server的skills/list，创建新的本地发现进程但不创建thread或启动模型turn。它与workflow_plan.py的文件扫描不同；也不代表网页当前聊天发现缓存或发布后跨任务恢复。

新网页任务必须分别验证：

| 场景输入 | 期望 |
|---|---|
| 新做30秒叙事短片，先规划工作流；不调用生成 | Router选择narrative，主Skill为aigc-project-prompt-loop |
| 为Seedance设计镜头运动，只输出导演提示词 | aigc-manga-video-director |
| 编辑商品图背景，先给编辑方案，不生成 | aigc-image-director |
| 检查已有剪映工程的字幕与时间线，先只检查 | jianying-editing |

先确认会话原生Skill清单有17项，不能只手动cat SKILL.md。任务启动与缓存恢复均需独立新网页任务证明，并确认doctor/vault路径正确。未实测时标“需新任务复验”，不能标正式投用通过。生成服务登录、额度、媒体质量与Windows/macOS原生执行是按需另验项目。
