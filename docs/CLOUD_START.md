# AIGC Codex Cloud Start skill

此内容用于新版Codex Cloud环境的Start skill字段。只负责启动就绪检查，不启动付费生成，也不把所有工作强制路由到AIGC。

1. 使用已选中的cyou1314/AIGC仓库。定位顺序为环境变量AIGC_REPO_ROOT、当前工作目录中的scripts/cloud-init.sh、/workspace/AIGC/scripts/cloud-init.sh。找不到时停止并报告checkout缺失，不从不明来源下载脚本。
2. 在环境设置/启动验证阶段运行仓库的 `bash scripts/cloud-init.sh`（从真实仓库目录执行，或传真实脚本绝对路径）。它会安全初始化 `$HOME/.agents/skills`、配置与工作区指令，检查结构、路径和原生Codex发现。脚本完全幂等，无需安装全部媒体依赖。出现同名Skill、用户修改、指令或路径冲突时，保留原文件与备份，报告具体阻塞；不要加adopt-existing/replace-local来掩盖冲突，不修改平台CODEX_HOME。
3. 用 `python3 scripts/doctor.py` 确认实际配置为 `$HOME/.agents/aigc-workflow.json`，工作区为配置的AIGC_WORKSPACE，vault与outputs存在。源码模板保留占位符，运行时知识文件不得含未替换的AIGC路径占位符。
4. 用 `python3 scripts/check_codex_discovery.py` 确认Codex自身skills/list发现并启用全部17个AIGC Skill。另核对当前任务的原生Skill清单；若独立CLI发现通过但任务清单仍缺失，标为blocked-discovery，不能报告正式投用成功。无需批量读取所有17个SKILL.md。
5. 本工作流没有必须常驻的Web服务。不调用付费媒体生成、登录、上传、GitHub推送或知识晋级来验证启动。媒体运行时和服务账号只在用户实际请求时按需检查。
6. 就绪后遵守仓库AGENTS.md。普通新/混合AIGC项目用aigc-production-router；明确专家与既有项目优先。Seedance镜头导演用aigc-manga-video-director；图片设计/编辑用aigc-image-director；已有剪映工程用jianying-editing；其他任务保持自己的流程。
7. 设置任务验证通过后保存并Republish环境，才能捕获供新任务使用的准备状态。随后在全新网页任务中进行零生成的17个Skill发现与四场景调用验收；未实测跨任务恢复时只报告“需新任务复验”。
