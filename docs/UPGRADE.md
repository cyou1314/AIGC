# 升级、版本与回滚

## 一、正常升级

Git仓库是工作方法的版本源；安装目录是部署结果。`manage.py upgrade`只安装当前仓库版本，不联网拉取，避免创作中自动改变流程。

macOS：

```bash
git status --short
git pull --ff-only
python3 scripts/validate.py
python3 scripts/manage.py upgrade
python3 scripts/doctor.py
```

Windows：

```powershell
git status --short
git pull --ff-only
py -3 scripts/validate.py
py -3 scripts/manage.py upgrade
py -3 scripts/doctor.py
```

如 `git status` 显示修改，先查看diff、提交到自己的分支或妥善备份；不要用reset硬清理。拉取失败不能忽略继续宣称升级到最新。

安装器沿用机器配置；使用自定义Skill目录时在upgrade/rollback也传同一个 `--skills-dir`。成功输出包含version、transaction与backup，保存到本机维护记录。新Codex会话重新确认Skill已加载。

## 二、保护本地修改

| 情况 | 默认行为 | 处理 |
|---|---|---|
| 首次同名Skill未托管 | 全部写入前停止 | 比较；确认替换时 `--adopt-existing` |
| 托管Skill出现本地修改 | 全部写入前停止 | 把有效改动合入仓库；确认替换时 `--replace-local` |
| 个人知识/项目模板已修改 | 保留原文件，新版进入 `.incoming` | 按文件合并，不全量覆盖 |
| 重复安装同一内容 | 保留不变内容；更新事务索引 | 不会反复重写全部Skill |
| 安装中途失败 | 恢复已开始的文件变更 | 当前内容保存在备份，读错误再重试 |

备份包括被替换文件和事务日志；失败或回滚时移开的当前版本在 `rollback-current/`，不是删除。备份可能包含自己的知识，必须按私有内容保存，不上传。

## 三、回滚

默认回滚注册表的最近事务；为明确选择版本，建议给出安装输出中的ID（下面占位符需替换）：

```text
python scripts/manage.py rollback --transaction TRANSACTION_ID
```

回滚后出现本地编辑时会拒绝覆盖。先比较新编辑；确需回滚再加 `--replace-local`，这些被移开的新文件仍保留在备份。注册表找不到时可额外传绝对 `--backup-root` 与 `--transaction`。同一已回滚事务不能反复执行。

Skill回滚不自动回滚你已经产生的影片/图像或改变的编辑工程。生产资产有独立版本和备份。首次安装回滚可能移除刚安装的全部受管文件，事先读事务日志确认范围。

## 四、发布规范

- PATCH：修复说明、路径和非破坏性缺陷，如1.0.1。
- MINOR：新增兼容能力/模板/Skill，如1.1.0。
- MAJOR：破坏性项目结构、安装/回执合同改变，如2.0.0；必须写迁移和回滚说明。

推荐变更流程：创建功能分支 → 修改最小必要部分 → 跑验证 → 最小实际样本 → 更新VERSION/CHANGELOG/来源摘要 → diff审查 → 合并 → 打版本tag → 另一台设备拉取。可以使用PR评审，但初始仓库不强制复杂审批牺牲创作效率。

`python scripts/source_manifest.py` 输出当前Skill摘要JSON供审阅后更新 `sources.json`；正文换行归一化，减少Windows checkout换行差异。它不自动下载上游、不包含机器绝对路径。

不要原样抄上游全部更新：先比较许可证、行为、API与适配，排除私有fixture、凭证、媒体和无关项目；保留当前有效安全边界。模型变化通过集成文档和实际样本确认，不把短期模型排行固化成Skill。

## 五、CI模板启用

`ci/github-actions.yml`已准备双平台Python回归。初次发布未放入 `.github/workflows/`：发布所用GitHub OAuth权限有repo，但没有workflow写权限，避免为了初始备份扩大账号授权。

想启用时，由账号所有者通过官方流程补齐workflow权限，再把模板保存为 `.github/workflows/validate.yml` 并提交。实际查看Windows/macOS两项运行结果后更新验证记录；模板存在不等于通过。标准库回归不需要服务密钥或付费生成。
