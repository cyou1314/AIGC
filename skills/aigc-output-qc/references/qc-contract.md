# Video QC Contract

Use this reference for detailed generated-video adjudication.

## Table of Contents

- [Input contract](#input-contract)
- [Evidence rules](#evidence-rules)
- [Review dimensions](#review-dimensions)
- [Cause classification](#cause-classification)
- [Action ladder](#action-ladder)
- [Output template](#output-template)
- [Decision examples](#decision-examples)

## Input Contract

Use only real supplied or verified values:

```yaml
asset_id: stable shot or clip identifier
media_type: video | sequence
generated_path: absolute path or attached artifact
target_prompt: latest complete prompt when available
storyboard_scope: board name and exact panel range when available
reference_roles:
  character: real references
  scene: real references
  style: real references
  first_frame: exact first-frame lock
  final_frame: exact tail-frame lock
audio_contract:
  source: supplied audio when available
  dialogue: exact speaker, line, and time range
previous_accepted_state: accepted prior-shot endpoint
next_shot_requirement: required outgoing continuity
user_priorities: explicit tolerances or must-fix items
```

Static images constrain the generated video. They are not standalone QC targets.

## Evidence Rules

Label statements as:

- `观察`: directly visible or audible in the supplied result.
- `合同`: explicitly required by prompt, board, reference, audio, or accepted state.
- `推测`: likely cause or model behavior not directly proven.

Never turn `推测` into a fact. If two references conflict, report the conflict before grading that dimension.

For video:

1. Probe metadata.
2. Sample start, end, major action beats, dialogue beats, and transitions.
3. Deep-read suspicious ranges.
4. Use continuous playback for motion, flicker, lip sync, temporal stability, or camera behavior.
5. Preserve the original; inspection derivatives are analysis-only.

## Review Dimensions

Review only dimensions supported by available evidence:

- duration, resolution, frame rate, streams, and file readability;
- face, hair, age, body shape, costume, accessories, and identity stability;
- pose, hands, limbs, contacts, and object interaction;
- prop identity, count, side, direction, and state;
- scene geography, background anchors, period, and environmental state;
- camera height, angle, lens impression, crop, path, speed, and motivation;
- subject blocking, action order, physics, contacts, and causal readability;
- composition, depth layers, attention path, and intended change across time;
- first-frame entry and exact final-frame landing;
- speaker, exact line, dialogue interval, visible lip sync, delivery, and rhythm;
- screen direction, eyeline, lighting direction, emotion, and motion continuity;
- flicker, melting, morphing, duplicate limbs, crawling texture, warping, teleporting, focus pumping, and unmotivated shake;
- connection with the previous accepted endpoint and next-shot requirement.

## Cause Classification

Choose the narrowest supported class:

| Cause | Use when |
|---|---|
| source or reference conflict | supplied constraints disagree |
| prompt omission or ambiguity | a core control is absent or unclear |
| overloaded shot | too many major beats compete in one clip |
| model deviation | the contract is clear but the result does not follow it |
| preprocessing/export artifact | the defect appears after media processing |
| post-production candidate | the core take is correct and the defect is local |
| insufficient evidence | cause or compliance cannot be supported |

Cause classification does not change observed evidence.

## Action Ladder

Escalate only when the cheaper option cannot preserve the contract:

1. `接受`: no meaningful failure.
2. `裁切/重定时/重构图`: the needed material already exists in the clip.
3. `替换音频/局部后期`: the defect is isolated and does not cross the subject or continuity foundation. Use FFmpeg only for deterministic operations or compositing with supplied replacement material.
4. `定向返修`: change one prompt control while preserving successful elements.
5. `局部范围重做`: redo only the failed dialogue, action, or endpoint range when the tool supports it.
6. `整镜重做`: a core requirement fails across the clip.
7. `拆镜`: the task is physically overloaded.
8. `重建合同`: references or requirements conflict.

Minor polish stops at steps 1-3. A locked identity, narrative action, visible dialogue timing, or exact endpoint may require steps 4-8.

## Output Template

```text
验收结论: 通过 | 可修后通过 | 需要重做 | 证据不足
适用范围: [asset ID / shot / time range]
结论依据: [observed evidence compared with contract]

问题清单:
- 级别: 阻断 | 重要 | 轻微
  时间/区域:
  目标要求:
  实际证据:
  影响:
  原因分类:
  最省成本处理:

返修交接:
- preserve: [successful content that must remain]
- change: [one or more exact failed controls]
- remove: [instructions that caused conflict or overload]
- add: [missing constraint]
- verification: [what proves the repair]
- downstream_skill: [one owner]

下一步:
[one concrete action]
```

Use one downstream owner:

- prompt revision → `aigc-project-prompt-loop`;
- visual evidence analysis → `aigc-manga-video-director`;
- audio evidence → `audio-to-prompt` or `transcribe`;
- deterministic derivative → `ffmpeg`.

If generative video cleanup is required and no authorized editing skill is available, hand the decision to `aigc-project-prompt-loop` and state the missing execution capability. Do not label FFmpeg as a generative repair tool.

## Decision Examples

### Locked costume and prop side fail

Verdict: `需要重做` when those are core continuity locks. Preserve successful camera, action, background, timing, and performance. Change only costume and prop-side controls when localized video editing is reliable; otherwise regenerate the affected clip.

### Exact final-frame lock missed

Verdict: `需要重做`. First check whether the correct endpoint already occurs earlier. If yes, trim or retime. If never reached, repair the endpoint range or regenerate with the exact final-frame contract. Compare framing, camera geometry, crop, pose, subject state, and composition. Require pixel identity only when the user explicitly requests it.

### Correct words but compressed visible lip sync

Verdict: `需要重做` when the speaking face is visible. Preserve the supplied audio and exact dialogue timing. Compress off-face or non-dialogue action before changing visible speech duration.

### Local background defect

Verdict: `可修后通过` when the subject, story, action, camera, and continuity are correct and the defect does not cross moving subject edges. Prefer crop, deterministic masking with supplied material, or an authorized localized video-editing capability over discarding the take. Do not claim FFmpeg can invent missing background content.

### Missing identity reference

Verdict: `证据不足` for target identity. The clip may still be judged for internal temporal stability. Request one accepted character reference or explicit identity anchor; do not call identity a pass or fail without it.
