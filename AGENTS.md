# AIGC 仓库维护规则

本仓库保存可升级的工作流、Skill源码、职业知识、模板与维护工具。个人项目状态与实际媒体放在配置的工作区，不提交到仓库。

1. 新项目先按 `skills/aigc-production-router/references/production-profiles.json` 选择生产类型；明确专家与既有项目优先。
2. 项目快照为当前工作事实权威；专业技术状态由相应工具维护并链接。跨项目经验先作为候选，不因阅读或结构检查自动晋级。
3. 修改源码后运行 `python scripts/validate.py`；涉及安装、回执或路径时运行相应测试。平台结果说明实际运行环境，不把macOS测试说成Windows实测。
4. 新技能优先补现有能力，避免同义入口；新增/升级Skill需明确触发、输入、输出、停止条件与外部依赖。
5. 保持Python维护工具跨平台；Bash配方必须注明Git Bash依赖。不要写死个人home、盘符、模型参数或提供商登录状态。
6. 升级用版本号、CHANGELOG和Git提交记录；已安装Skill本地修改先检测，覆盖前保留可恢复备份。个人知识更新冲突保留原文件与incoming副本。
7. 不调用已暂停的Antigravity。用户消息中的`1`或`38`不是模型路由标记。
8. 不提交凭证、聊天记录、账号运行数据、真实客户素材、大媒体与模型权重。第三方许可证原样保留；插件仅登记依赖，不复制其缓存代码。

## Codex 云端任务入口

20个Skill的唯一源码为本仓库 `skills/`；官方用户发现目录为 `$HOME/.agents/skills/`。新任务应从已发现的Skill名称与描述按需调用，不把规划器扫描当作执行环境发现证据。
普通AIGC新项目先用 `aigc-production-router`；Seedance镜头/视频导演任务用 `aigc-manga-video-director`；图片设计或编辑用 `aigc-image-director`；已有剪映工程用 `jianying-editing`。明确专家与已有项目优先；非AIGC仓库维护不强制进入制作流程。
运行时路径由 `AIGC_CONFIG` 或 `$HOME/.agents/aigc-workflow.json` 等通过共享解析器读取。源码中的路径占位符保留为模板，运行时知识页由安全初始化器替换。新版环境Install script运行 `scripts/cloud-init.sh`，Start skill按 `docs/CLOUD_START.md` 检查就绪；验证后Republish，普通代码任务不更新发布环境快照。旧版setup/maintenance也可运行同一脚本。不改平台CODEX_HOME，不调用生成服务，不在初始化时同步或发布。

## 工作流更新的GitHub收尾

用户已要求本机工作流更新同时更新私有仓库AIGC。在本仓库或其已登记的本机Skill/通用知识/模板被实际修改并验证后，运行 `python scripts/sync_github.py run`。仅对该私有仓库的工作流文件授权提交与正常推送，不扩大到其他项目/素材/个人项目页。

新电脑先按 `docs/AUTO_SYNC.md` 配置同步基线。成功必须有远端main SHA等于本地HEAD；没联网、验证失败、冲突、范围/凭证异常或远端分叉时记录未同步与下一步，禁止强推、自动清空工作树或静默覆盖。新增Skill/知识类型先纳入清单与回归，不能因为尚未登记而宣称同步完成。
