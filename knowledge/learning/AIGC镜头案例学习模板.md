---
type: template
domain: cinematography-storyboard
updated: 2026-08-06
tags:
  - 学习/镜头
  - 学习/案例
  - 学习/提示词
---

# AIGC 镜头案例学习模板

本模板记录“为什么镜头有效、如何复用、何时不要用”，不收集孤立提示词。每张案例卡只记录一个镜头或一组具有同一导演逻辑的镜头。

## 证据与范围

```yaml
case_id:
source:
source_type: 用户素材 | 公开作品 | 生成成片 | 失败结果 | 用户修正
evidence: 观察帧/视频时间码/用户确认/公开原作者说明/二手转述
scope: 本项目有效 | 候选 | 同类项目可复用 | 已验证
confidence: 高 | 中 | 低
rule_status: 候选 | 有效 | 稳定 | 降级 | 归档
validation_scope: 未生成 | 已生成未QC | 单镜头验证 | 多镜头验证 | 多项目验证
evidence_level: E0 | E1 | E2 | E3 | E4
baseline_version:
preserve:
failure_class:
earliest_divergence:
changed_control:
verification_window:
repair_decision: accept | trim | post_fix | revise | local_regenerate | split | rebuild_contract | redo
regression_cases:
rule_decision: keep_candidate | promote_effective | keep_stable | narrow_scope | downgrade | merge | archive
archive_reason:
```

当来源是公开创作者、电影导演或视频分析时，补充：

```yaml
creator_or_director:
work_or_clip:
public_url:
source_timecode:
learning_focus: 镜头 | 调度 | 动作 | 表演 | 声音 | 剪辑 | 资产 | 工作流
copy_boundary: 只提取方法，不复制角色/IP/完整场面调度
```

公开作品只吸收导演语法，不复制角色、IP、独特构图或完整场面调度。二手资料中的工具、成本和作者归因单独标记为待核验。

## Shot DNA

```yaml
story_purpose:
emotional_change:
attention_order:
spatial_relation:
visual_hierarchy:
shot_size_and_lens_feel:
camera_path:
camera_motivation:
composition_geometry:
foreground_midground_background:
lighting_source_and_material_response:
lighting_state:
dominant_source_landmark:
key_direction:
shadow_side:
light_quality:
color_relationship:
atmosphere_layers:
material_response:
visual_continuity_state:
action_causality:
dominant_charisma_mode:
subject_roles:
action_staging_graph:
axis_depth_force:
camera_action_coupling:
contact_proof:
reaction_hierarchy:
entry_state:
exit_state:
edit_handle:
sound_or_rhythm:
generation_risk:
performance_beat:
dialogue_contract:
speaker_identity_state:
listener_or_observer:
listener_reaction_trigger:
listener_reaction_timing_or_latency:
listener_reaction_channel:
listener_emotion_change:
listener_reaction_strength: micro | readable | active
listener_reaction_endpoint:
listener_vocal_status: silent_listener | whisper | interruption | shared_vocal_action
attention_owner: speaker_delivery | listener_interpretation | shared_power | initiator_action | receiver_consequence | shared_danger
reaction_priority: speaker_delivery | listener_interpretation | shared_power | physical_consequence | initiator_action | receiver_consequence | shared_danger
audio_over_listener: true | false
axis_and_eyeline:
audio_authority:
sound_edit_sync:
coverage_or_cut_point:
sequence_arc:
beat_map:
cut_motivation:
visual_bridge:
sound_bridge:
next_match:
reference_role_map:
reference_conflicts:
authority_source:
continuity_state:
audio_contract:
```

## 规则提炼

```text
为什么有效:

适用场景:

不适用场景:

提示词应保留的控制点:

允许模型发挥的部分:

最小复用版本:
```

## External Case Translation

```text
观察事实:
导演推断:
可迁移变量:
适用镜头:
不适用镜头:
最小规则:
对当前素材的试用方式:
实际结果: 未验证/有效/失败/待复核
```

## 生成对照

只有真实生成或QC证据存在时填写：

```yaml
baseline:
preserve:
changed_control:
observed_result:
failure_class:
verification:
next_action:
```

没有真实生成证据时，写“未验证”，不要把案例里的最终提示词当成成功证明。

## 升级判断

- 单次公开案例或单项目经验：保留为 `候选` 或 `降级观察`。
- 用户明确接受、真实生成/QC改善或多项目重复有效：才考虑 `强化`。
- 与现有规则重复：`合并`；可能误导后续：`改写`、缩小范围或删除。
- 若本次生成只改变一个主要变量，记录变量前后的差异；若同时改变多个变量，只能标记为观察，不能据此升级规则。
- 单帧漂亮但无法完成叙事、连续性或剪辑接口的结果，不升级为有效规则。
- 多模态案例必须记录每个参考素材的主要职责；未解决的参考冲突不能写成已验证经验。


---

## 本地吸收说明

- Drive 原文：https://drive.google.com/file/d/122Ctc3hRVtfwTKB8IgE2IVXYINKFqnZj/view?usp=drivesdk
- 本地归属：`learning\AIGC镜头案例学习模板.md`
- 处理方式：保留原知识正文，补入当前 Obsidian Codex 作为可检索知识页；执行时仍由对应本地 Skill 负责。
- 证据边界：文本被读取和整理不等于真实视频生成或成片 QC 已通过。
