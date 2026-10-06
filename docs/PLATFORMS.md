# Windows与macOS兼容规范

## 支持层级

| 层级 | 支持方式 | 不应误判的地方 |
|---|---|---|
| 安装、升级、回滚、路由、状态 | Python标准库，pathlib路径，UTF-8 | 代码适配不等于Windows原生执行已经通过 |
| 媒体分析/转换 | FFmpeg/ffprobe与可选Python库 | ffmpeg存在不代表ffprobe也存在 |
| 自动剪辑/剪映工程 | 现有Skill、独立CLI、实际编辑器 | JSON能读不代表编辑器能重开或成功导出 |
| 外部生成 | 当前Codex插件或合法API | 本仓库不迁移登录状态、点数或插件缓存 |

## Shell与路径

Python入口优先；macOS使用 `python3`，Windows使用 `py -3` 或虚拟环境Python。所有含空格/中文路径加引号。Windows PowerShell用 `$env:NAME`，macOS用 `$NAME`，不能把Bash命令逐字粘贴到PowerShell。

仓库内 `.sh` 配方属于Bash脚本：macOS通常可执行，Windows应使用Git Bash；不想增加Bash依赖就使用其对应CLI/Python操作。每次修改批量配方前先读脚本，不默认赋予其删除、覆盖原媒体的权限。

不要跨系统复制绝对媒体路径。跨机交接应保留项目相对目录结构并重链接素材；给目标编辑器实际打开一次。编码、盘符、文件名大小写、文件权限、字体和插件版本都可能影响重开。

## 工具检查

```text
ffmpeg -version
ffprobe -version
git --version
node --version        # 仅Node型CLI需要
capcut --help         # 仅对应剪映/CapCut任务需要
blender --version    # 仅本地3D预演需要
```

FFmpeg/ffprobe应选择可信来源并加入PATH；不在仓库打包平台二进制。Windows自带时区库不完整时状态工具回退固定UTC+8，等效中国标准时间，不将其他时区伪装成相同规则。

当前来源中使用过的第三方CLI为 `capcut-cli@0.23.0`（非字节官方CLI）。可在独立Node环境执行 `npm install -g capcut-cli@0.23.0`；随后先看 `capcut --help` / `capcut describe`，核对实际命令、目标编辑器及草稿结构。此版本是引入快照，不是承诺永远适配后续剪映。

## 编辑工程安全流程

自动剪辑上游还有macOS原生增强：CoreText字幕光栅化、NSString字素边界与Vision OCR。这些不是装Python包即可在Windows复现的功能。本仓库保留源合同，不改成“看起来通过”的假兼容。

Windows用相同的剪辑决策/时间线思想，但按当前动作切换确定性FFmpeg切片、SRT/ASS字幕或本机剪映字幕排版，并在交接中记录新路径和验收。需要上游Studio原样高级字幕效果时应在macOS完成，或另开跨平台字幕引擎适配项目；不承诺本次已经移植整个CoreText引擎。基本转录也须实际安装Whisper或确认合法服务，不是Python依赖列表自动包含模型。

1. 关闭目标编辑器，保留原工程与原媒体，复制工程到新版本。
2. 读草稿与素材索引，列逐切点决策表，避免直接全局改时间戳。
3. 小批修改，检查轨道、字幕、关键帧、音量、素材引用。
4. 在目标系统编辑器重开副本，目视和试听。
5. 导出后核查时长、分辨率、帧率、字幕、声音与黑帧；实际导出文件登记回执。

CapCut国际版、剪映专业版、不同系统/版本的工程不是无条件互通。无法验证兼容时记录 `blocked-runtime`，交付剪辑决策和素材清单，不能标记“已完成成片”。

## 跨系统迁移清单

- 克隆私有仓库到新机器，运行验证和安装器；不复制旧机器aigc-workflow.json。
- vault可使用既有同步方式，但Git中的通用知识不等于完整个人vault备份。
- 项目素材通过合法文件同步/外置存储迁移；校验字节大小与摘要。
- 字体、LUT、媒体编码、工具版本、目标软件与插件逐项确认。
- 凭证在目标机器重新官方登录，API密钥用系统/服务推荐的安全方式配置。
- 运行一个最小实际任务并验证结果，记录平台与软件版本。

首次发布提供Windows/macOS CI模板，尚未据此宣称所有媒体工具、付费模型和编辑器已双平台验收。
