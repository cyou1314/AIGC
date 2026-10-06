# 安装与首次运行

## 1. 安装策略

推荐保留一个Git仓库作为工作方法的版本源，另外保存项目、输出和Obsidian知识库。不要把素材、机器路径或账号放进仓库。安装器只管理本仓库的Skill和知识模板，不安装模型、不登录服务、不改其他Skill。

核心要求：Git、Python 3.10+、可访问此私有仓库的GitHub账号。发布前实际测试解释器为Python 3.12。媒体任务需要额外依赖，见[平台说明](PLATFORMS.md)。新机器需要自行安装Codex并完成官方登录。

## 2. 获取仓库

已认证GitHub CLI时运行 `gh repo clone cyou1314/AIGC`；或者使用已认证Git的 `git clone https://github.com/cyou1314/AIGC.git`。登录只在官方界面完成，不在聊天、配置文件或远程URL中填Token。

macOS终端：

```bash
cd AIGC
python3 --version
python3 scripts/validate.py
python3 scripts/manage.py install --workspace "$HOME/AIGC-workspace"
python3 scripts/doctor.py
```

Windows PowerShell：

```powershell
Set-Location AIGC
py -3 --version
py -3 scripts/validate.py
py -3 scripts/manage.py install --workspace "$env:USERPROFILE\AIGC-workspace"
py -3 scripts/doctor.py
```

上述命令不保证系统已经安装依赖；解释器版本不够先升级Python。Windows有多个Python时显式用 `py -3.12`，macOS同理选定正确解释器。不要依赖另一个应用自带、可能随更新改变路径的Python。

## 3. 接入已有Obsidian知识库

先确认真实vault目录，而不是把占位符当路径。`--vault` 指向要放这些项目页/知识的目录，可以是完整vault，也可以是vault中的Codex子目录。

macOS示例（先替换路径）：

```bash
python3 scripts/manage.py install --workspace "$HOME/AIGC-workspace" --vault "/absolute/path/My Vault/Codex"
```

Windows示例（先替换路径）：

```powershell
py -3 scripts/manage.py install --workspace "$env:USERPROFILE\AIGC-workspace" --vault "D:\My Vault\Codex"
```

可选参数：`--outputs` 设置成品目录；`--skills-dir` 指定Codex的实际Skill目录。默认Skill目录为 `CODEX_HOME/skills`，未设置CODEX_HOME时使用用户目录下的 `.codex/skills`。自定义目录必须同时能被当前Codex会话发现。

安装后在Skill目录的父目录生成：

- `aigc-workflow.json`：本机路径与版本配置，禁止提交。
- `aigc-installed.json`：托管文件摘要和备份事务索引，禁止提交。
- 工作区 `.aigc-backups/<事务ID>/`：可恢复备份，保留到确认新版本可用。

## 4. 首次冲突处理

遇到同名Skill，安装器在任何目标改变前停止。先比较仓库与已有Skill；想保留旧版就暂停迁移或选择隔离安装目录，想采用本仓库版本才加 `--adopt-existing`。已有托管Skill被本地修改时，先把改动合并回Git仓库；确认备份并替换才加 `--replace-local`。

已有个人知识文件不会直接覆盖；新模板进入vault的 `.incoming/`，人工比较后合并。不要把 `.incoming/` 直接整目录覆盖回vault。

## 5. 媒体分析依赖（按需）

无需每个任务都安装全部依赖。需要转录、抽帧或图像分析时再创建环境。

macOS：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/doctor.py
```

Windows：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/doctor.py
```

Windows无需执行激活脚本，因此不必为了此仓库修改全局执行策略。后续媒体脚本用同一虚拟环境解释器；安装Skill时使用的Python路径会写入相关说明，移动/删除环境后需要重新安装更新路径。

`requirements.txt`是宽范围可选依赖清单，不是锁文件。稳定生产环境应记录实际安装版本；不要在交付中途无理由升级媒体库。

## 6. 验收首次安装

开启新的Codex会话确认17个Skill可见，指定 `$aigc-production-router` 制作一个明确目标，先让它报告当前主Skill、缺少输入、能力边界和唯一下一步。随后使用项目页脚本建立测试项目并核验路径。安装成功与生成成功分别验收。

自定义 `--skills-dir` 不在默认CODEX_HOME时，`doctor.py`不会自动找到那份安装配置；设置对应CODEX_HOME或AIGC_WORKSPACE/AIGC_VAULT/AIGC_OUTPUT_ROOT再检查。
