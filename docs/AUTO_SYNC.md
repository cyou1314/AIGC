# 本机工作流自动同步到GitHub

## 保证方式与边界

采用两层：Codex每次完成已登记工作流更新后立即执行同步；定期任务检查其他工具/手动编辑造成的漏同步。它不是系统级文件监听器，也不承诺在睡眠、断网、认证失效或应用关闭时即时上传。

发布成功只认远端main SHA与本地HEAD一致，不以“已经commit”或“准备推送”代替。遇到失败保留本机更新、备份与待推提交，下次恢复条件后重试；冲突/隐私/范围问题需要人工判断，不能保证自动解决所有情况。

## 同步范围

- 17个已登记本地Skill：现有源码、参考、配方、相关测试，以及其中新增的合规文件。
- 仓库已经列出的 `knowledge/agent`、`knowledge/learning` 页面：只取对应本机文件的新增改动。
- 快速/完整项目模板。
- 本仓库内部的维护脚本、制作手册、通用模板等合规改动。

不上传个人vault的首页/TODO/AGENTS/项目页/笔记/人员信息，也不扫描整个个人vault。凭证、媒体、插件缓存、模型和排除的上游私有转录fixture不进入同步。

新增第18个Skill或新的知识页面需要先纳入仓库、更新数量与测试，再运行 `python scripts/sync_github.py register --skill 新Skill名称` 或 `register --knowledge agent/新知识.md`。注册只建立新增项的基线，不改变旧项未同步改动；登记前审阅本机与仓库两份初始内容。不能自动把电脑上所有新插件和Skill都当AIGC工作流上传。不要删掉旧同步基线重新setup来掩盖未同步改动。

## 每台电脑首次配置

先确认GitHub官方登录有效，仓库在本机，安装路径/vault/output实际可用。同一个repo克隆不能共享机器同步配置。

macOS示例：

```bash
python3 scripts/sync_github.py setup --skills-dir "$HOME/.codex/skills" --vault "/absolute/path/My Vault/Codex" --workspace "$HOME/AIGC-workspace" --outputs "$HOME/AIGC-workspace/outputs"
python3 scripts/sync_github.py status
python3 scripts/sync_github.py run
```

Windows PowerShell示例：

```powershell
py -3 scripts/sync_github.py setup --skills-dir "$env:USERPROFILE\.codex\skills" --vault "D:\My Vault\Codex" --workspace "$env:USERPROFILE\AIGC-workspace" --outputs "$env:USERPROFILE\AIGC-workspace\outputs"
py -3 scripts/sync_github.py status
py -3 scripts/sync_github.py run
```

首次setup记录当下机器内容及仓库内容，不把所有历史平台差异直接上传。设置保存在忽略的 `.local/github-sync.json`，不能提交或跨电脑复制。历史差异如需迁移，先逐项人工审阅；之后的修改才自动识别。

私有仓库的git认证须可非交互执行。可用官方 `gh auth login` / `gh auth setup-git` 配置，或者本机仓库局部凭证助手；账号输入由用户完成，不写Token到URL。检查原点必须是配置的GitHub仓库，且仓库保持private。

## 同步顺序

本机setup后，`manage.py install/upgrade`在实际配置的生产Skill目录安装成功时，也会直接调用同步。隔离安装目录不触发生产同步；同步失败退出码3表示“安装已完成但发布阻塞”，不会回滚已经成功的安装。尚未setup的机器不会凭空得到同步覆盖。

1. 检查私有仓库身份、分支、已有暂存与远端状态。
2. 比较首次/上次确认的本机内容，提取本次新增改动。
3. 将这些改动与仓库跨平台适配做三方合并：无重叠自动合并，重叠停止。
4. 写候选前保存仓库旧文件到 `.local/sync-backups/`；不修改生产安装Skill。
5. 检查范围和疑似凭证、刷新来源摘要，运行全套回归。
6. 没有人工版本改动时自动补PATCH与CHANGELOG；提交并正常push。
7. 读回远端main SHA，确认一致才推进本机基线。

`.local/github-sync.lock`防止本工具同时运行。进程异常留下的锁必须确认无任务运行后再处理，不自动清理可能仍使用中的锁。

## 失败处理

| 情况 | 行为/恢复 |
|---|---|
| 网络或登录失效 | 不说已同步；保留提交；恢复网络/官方登录后run |
| 跨平台修改重叠 | 不覆盖；比较本机和仓库，人工合并后重跑 |
| 验证失败 | 不提交/推送；候选与原版本备份保留，修复后重跑 |
| 已有人工暂存 | 保持index，先由用户/当前任务处理，不混入自动提交 |
| 远端领先且本机干净 | 仅fast-forward，随后比较本机工作流改动 |
| 远端分叉或领先时本机有修改 | 停止；不强推或自动复杂合并 |
| 敏感内容/范围外文件 | 停止并报告文件，不打印凭证内容 |
| 编辑期间文件又变化 | 基线仍保留已观察版本，下一轮识别后续改动 |

自动检查不是完整DLP，不能识别所有隐私文本；修改工作流时仍遵守最小数据和不含凭证原则。

## 定期兜底

当前机器可在Codex添加同一聊天的每小时检查，运行本机 `sync_github.py run`。无变化不报告；成功有实质同步才报告版本/提交；失败说明所需动作，不无限重试/扩大权限。新设备需重新配置自己的定期任务；本仓库不携带用户自动化账号或机器任务配置。

涉及本地文件的定期任务要求电脑开机、应用运行且文件可访问，见[官方任务说明](https://learn.chatgpt.com/docs/automations?surface=app)。如需更短间隔可改任务频率，需考虑账户额度和编辑中的临时状态。
