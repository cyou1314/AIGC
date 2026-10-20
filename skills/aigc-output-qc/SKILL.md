---
name: aigc-output-qc
description: Use when a generated AIGC video or connected clip sequence needs post-generation review, 成片验收, 视频验收, 结果检查, 对比分镜, 对比提示词, 返修判断, 是否重做, continuity review, lip-sync review, tail-frame validation, or an evidence-backed repair direction for manga/drama production.
---

# AIGC Output QC

Judge generated video against its real production contract. Preserve usable work and choose the lowest-cost valid repair.

## Core Boundary

- Review generated video or connected video sequences only. Text-only Seedance prompt review belongs to the company review mode in `aigc-manga-video-director`; a passed text ledger is not a media verdict.
- Use static images as character, scene, style, composition, first-frame, or final-frame evidence; do not review them as standalone outputs.
- Inspect actual supplied assets before naming or judging them. Keep `@` references as real bare names without file extensions.
- Do not generate, edit, upload, spend credits, or submit a retry automatically.
- Return repair deltas. `aigc-project-prompt-loop` owns the complete revised prompt.
- Separate observed evidence from inferred cause.

## Required Evidence

Use what exists: generated video, latest prompt, storyboard plus exact panel range, real references, first/final-frame locks, supplied audio, exact dialogue timing, previous accepted endpoint, and next-shot continuity.

If a required comparison source is missing, judge only supported dimensions. Use `证据不足` for the unsupported contract instead of guessing.

Read `references/qc-contract.md` for the detailed input contract, review dimensions, cause classes, action ladder, and examples.

## Review Workflow

1. Identify the asset ID, intended shot, and available contract evidence.
2. Use `ffprobe` for metadata. Ask `ffmpeg` for only the proxy, trim, frames, or audio derivative needed for inspection.
3. Sample the start, action beats, dialogue beats, transitions, and end. Deep-read only risky ranges.
4. Ask `aigc-manga-video-director` for observed visual, camera, action, artifact, and continuity evidence.
5. Use `transcribe` or `audio-to-prompt` when exact words, delivery, pacing, sound, or lip sync matter.
6. Compare evidence with the contract, assign one verdict, then choose the lowest-cost valid action.
7. Record accepted exceptions so later checks do not repeatedly flag them.

Exact supplied audio controls dialogue timing and delivery. An exact supplied final-frame image controls endpoint framing, camera geometry, crop, pose, subject state, and composition, not merely style. Require pixel-identical output only when the user explicitly asks for it.

## Verdict Rules

Use exactly one:

- `通过`: no contract-breaking issue; safe to continue.
- `可修后通过`: the core result is usable and a localized edit is cheaper and safer than regeneration.
- `需要重做`: identity, main action, camera logic, narrative information, visible dialogue/lip sync, exact endpoint, or cross-shot continuity fails fundamentally.
- `证据不足`: required evidence is missing, unreadable, or contradictory.

Issue severity:

- `阻断`: prevents intended use.
- `重要`: materially weakens production quality.
- `轻微`: optional polish; never forces regeneration alone.

Do not use percentage scores.

## Repair Decision

Choose the first valid action:

1. accept;
2. trim, reframe, replace audio, or localize a post-production repair;
3. revise one prompt control and regenerate the affected clip or range;
4. split an overloaded shot;
5. rebuild a conflicting reference or contract.

Do not hide identity, story, action, lip-sync, or continuity failures behind post-production. Do not discard a successful subject, performance, and camera take for an isolated repairable background defect.

Use `ffmpeg` only for deterministic inspection, trim, retime, crop, reframe, or compositing with supplied material. Do not claim it can invent a generative background repair.

## Output Contract

Lead with:

```text
验收结论: 通过 | 可修后通过 | 需要重做 | 证据不足
适用范围: [asset ID / shot / time range]
结论依据: [short observed-evidence summary]

问题清单:
- 级别:
  时间/区域:
  目标要求:
  实际证据:
  影响:
  原因分类:
  最省成本处理:

返修交接:
- preserve:
- change:
- remove:
- add:
- verification:
- downstream_skill:

下一步:
[one concrete action]
```

For `通过`, omit empty problem and repair sections. Mark uncertain causes as inference.

For `证据不足`, use only:

```text
验收结论: 证据不足
适用范围:
结论依据:
缺失证据:
下一步:
```

## Companion Skills

- `ffmpeg`: deterministic metadata, inspection derivatives, trim, retime, crop, reframe, or supplied-material compositing only.
- `aigc-manga-video-director`: visual, camera, action, artifact, and continuity evidence.
- `transcribe`: exact speech recognition and timing.
- `audio-to-prompt`: delivery, emotion, pacing, sound, and supported lip-sync evidence.
- `aigc-project-prompt-loop`: project state and complete prompt revision.

## Quality Gate

Before returning:

- the verdict matches the strongest supported issue;
- every issue cites an actual time range or visible region when available;
- evidence and inference are distinguishable;
- missing references do not become invented facts;
- the proposed action is cheaper than the next alternative without sacrificing a core requirement;
- no paid or destructive action has been taken;
- QC returns deltas, not a competing full prompt.
