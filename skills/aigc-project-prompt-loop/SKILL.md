---
name: aigc-project-prompt-loop
description: Run multi-turn narrative AIGC video/storyboard prompt projects, including manga, drama, animation, MV and song-based sequences, from reference or script through shot prompts and revision. Use 开始 or 结束 only in an established narrative-video context or when explicitly invoked. New image, UGC, audio, 3D, research and software projects select their own production route.
---

# AIGC Project Prompt Loop

Use this skill as the project conductor for one AIGC manga/drama production thread. It keeps the work coherent from `开始` to `结束`: analyze reference material, absorb storyboard/character/scene inputs, write prompts, revise them through user feedback, and close by extracting reusable learning from the final accepted version.

## Core Contract

- Work in Chinese by default.
- Treat `开始` as opening this loop only when narrative-video intent is established. For an untyped project use `aigc-production-router`; an existing project keeps its recorded route.
- Treat the user's `结束` as project closeout: keep the latest prompt pack internally, audit the whole project process, and evolve the reusable rules with additions, corrections, merges, demotions, and deletions.
- Use this skill to manage state and sequencing; use specialized skills for deep work.
- Prefer practical production outputs over theory: shot tables, storyboard logic, prompt packs, revision notes, continuity risks, and final copyable prompts.
- Keep outputs medium-density: concise enough to copy, complete enough to reproduce the shot.

## Project State

Maintain project state in the project page managed by `obsidian-codex-knowledge-loop`; that page is the source of truth across turns and devices. Chat memory is only a working cache. At start, create or recover the page; after material changes, update its snapshot and knowledge capsule; after real generation, append a receipt.

- `阶段`: start, video-analysis, input-collection, prompt-draft, revision, output-qc, closeout.
- `参考视频/素材`: video files, screenshots, extracted frames, audio, scripts, rough animatics.
- `分镜板`: panel order, shot IDs, compositions, actions, dialogue, time or duration.
- `人物`: `@` reference names, identity, wardrobe, props, expression rules, continuity risks.
- `角色锚点`: recurring character invariants such as face, hair, outfit, props, expression range, and forbidden changes.
- `场景`: `@` reference names, geography, lighting direction, era/style, reusable background rules.
- `全局规则`: style, stability, avoid rules, model target, aspect ratio, naming conventions.
- `最新提示词版本`: the complete current prompt pack, not only patches.
- `用户修改意见`: reusable preferences versus current-task-only changes.
- `过程证据`: initial assumptions, each material change, rejected drafts, accepted revisions, generation feedback, and final outcome.
- `生成结果验收`: accepted exceptions, QC verdict, observed evidence, repair decision, and whether the latest prompt needs revision.

When state is missing, ask for only the next blocking input. Do not restart the entire workflow unless the user asks.

## Workflow

### 1. Start

When the user says `开始`:

1. Invoke `obsidian-codex-knowledge-loop`: recover an existing project page or create one from the quick template, then read `当前快照` and `当前知识胶囊`.
2. Identify available materials and record authoritative inputs, constraints, output root, and one next step on the project page.
3. If video/reference footage is present, move directly to video analysis.
4. If a script is present, treat it as a valid starting material: extract characters, scenes, emotional beats, and then route character/staging work to `aigc-manga-video-director`.
5. If no material is present, ask the user for the first asset needed: reference video, storyboard board, character references, scene references, script, or target prompt goal.
6. Briefly state the current phase and what will happen next.

### 2. Analyze Video Or References

For video, rough animatic, sketch video, screenshots, or frame sequences:

- Use `ffmpeg` first only when deterministic preprocessing materially helps: media metadata, target-range trimming, lightweight proxy creation, frame/audio extraction, conversion, normalization, compression, or output verification. Skip it when the original source is already suitable.
- Use a new `output_path` and preserve the original `source_path` by default. Pass `purpose`, `operation`, `preserve`, `constraints`, `verification`, and exactly one `downstream_skill` in the handoff.
- Route verified video/frame derivatives to `aigc-manga-video-director`; route verified dialogue audio to `transcribe` or `audio-to-prompt`; retain verified `ffprobe` metadata in project state when useful.
- FFmpeg does not own visual analysis, transcription, emotional interpretation, or final prompt writing. The selected downstream specialist produces that output once.
- Use `aigc-manga-video-director` when available.
- If audio or dialogue matters, use `transcribe` or `audio-to-prompt` when available.
- Analyze enough to support later prompt writing: shot IDs, time ranges, start/end framing, camera movement, composition, blocking, emotion, continuity, and generation risks.
- Preserve evidence. Separate observed visual facts from inferred directorial intent.
- Prefer staged sampling and contact sheets for long videos, then deep-read important shots.

The output of this phase should become the shot backbone for later prompts. Do not write final prompts yet unless the user has already provided characters/scenes/style targets or asks for an early draft.

### 3. Absorb Storyboard, Character, And Scene Inputs

When the user provides storyboard boards, character images, scene references, or written notes:

1. Map every provided asset to a stable role.
2. Convert image references to bare `@name` format. Strip file extensions, paths, coordinates, and role labels from the `@` value itself.
3. For recurring characters, build compact character anchors before final prompts: face, hair, outfit, props, expression range, posture habits, and forbidden changes.
4. Build or update the global blocks:
   - `全局人物`
   - `全局场景`
   - `全局风格`
   - `全局稳定性`
   - `全局避免`
5. Connect each storyboard panel to the matching shot ID from the video analysis when possible.
6. Flag conflicts early, such as mismatched character identity, changed wardrobe, impossible camera continuity, unclear scene geography, or missing start/end frames.

Do not repeat global reference images and global style inside every shot unless the user explicitly asks for fully standalone per-shot prompts.

### 4. Draft Prompt Pack

Write the first usable prompt pack after the video/storyboard/reference context is sufficient.

Default structure:

```text
项目提示词 v1

全局人物: @角色A ...; @角色B ...
全局场景: @场景A ...
全局风格: ...
全局稳定性: ...
全局避免: ...

S01 / 分镜1
时间/来源: ...
视频提示词: ...
连续性: ...
生成风险: ...

S02 / 分镜2
...
```

Do not include image-generation prompts by default. Add them only when the user explicitly asks for 生图提示词 or image generation.

For each shot, include only shot-specific deltas:

- source timecode or storyboard panel ID
- start frame and end frame
- subject action and emotional beat
- camera path, speed/easing, angle, focal-depth feel
- foreground/background/parallax or designed motion
- composition change and attention path
- continuity constraints
- avoid rules only if this shot has special risks

Use Seedance 2.5 as the current video planning target. Follow the director Skill’s current company standard: 4–30 seconds per production unit as a user-supplied planning condition, not an internal-shot minimum or an unverified API guarantee. When revising an existing board, use the source duration as the starting point; preserve it when feasible. The user permits changing it or splitting when genuinely needed for essential action, natural dialogue or reactions; explain the source and new durations and keep an exact trailing duration in each resulting prompt. Preserve explicit duration, one-take and no-split locks. Include source ranges for recreation and deliver one complete copyable prompt unless alternatives are requested. Verify the actual generation surface before paid execution.

### 5. Revision Loop

When the user gives修改意见:

1. Choose the base: the version the user identifies, otherwise the latest confirmed complete prompt for the correct episode/board. Distinguish accepted work, an unaccepted candidate and actual media; never silently combine versions. If the base is ambiguous and changes the edit, ask which version.
2. Classify each note: `立即修改` within its authorized scope; `可复用偏好` for this project; `需要澄清` only when it cannot be safely inferred. Before changing text, identify protected dialogue, facts, asset tags, sound policy, duration, accepted staging and negative constraints; check required downstream effects without rewriting unselected boards.
3. Return the complete updated prompt for the requested scope unless the user asks for a local patch. Compare against the chosen base for unauthorized omissions, contradictions and residual old states; preserve the trailing duration line. Notes stay outside the copyable prompt and are optional.
4. Track the version when useful, without claiming user acceptance or displaying obsolete versions unless requested.

For a stronger version, make proportionate improvements to the requested elements and necessary connected details; preserve explicit locks, established story and accepted decisions unless the user opens them for revision. Do not pad with generic style adjectives.

### 6. Review Generated Video

When the user supplies a generated video or connected clip sequence for review:

1. Route the actual result and available production contract to `aigc-output-qc`.
2. For `通过`, record the result as accepted production evidence and continue.
3. For `可修后通过`, preserve the successful core and route only the localized repair. Do not discard the take by default.
4. For `需要重做`, convert the QC repair handoff into the next complete prompt version. Preserve every successful element named in `preserve`.
5. For `证据不足`, request only the missing contract evidence.
6. Record user-accepted exceptions so later QC does not repeatedly flag them.

Never submit regeneration or a paid edit automatically. QC supplies evidence and repair deltas; this project loop remains the owner of the complete revised prompt block.

### 7. End, Audit, And Evolve

When the user says `结束`:

1. Treat the current latest prompt pack as the final version unless the user says it still needs changes, and write the final version, output path, and status into the project page.
2. Keep the final prompt pack in project state, but do not show it again by default. The user already has the latest working version; only re-output the final prompt if the user explicitly asks.
3. Complete the closeout audit internally. Do not show the final prompt or full audit unless the user explicitly asks to看总结, 查看学习项, or show the closeout.
4. Audit the entire project process, not only the final prompt: initial assumptions, reference analysis, storyboard mapping, every meaningful correction, rejected approaches, accepted revisions, generation feedback, and production efficiency.
5. Run a `规则进化审计` over relevant existing rules. Assign each rule exactly one action: `保留`, `强化`, `改写`, `合并`, `降级观察`, or `删除`.
6. Do not accumulate rules by default. New learning must replace, narrow, merge with, or clearly outperform existing guidance; otherwise keep it project-local or under observation.
7. 删除不是每次收尾的必选动作，也没有删除配额。大多数项目可以没有任何删除项；仅当一条规则已几乎没有剩余适用价值，而且保留、缩小范围、改写、合并或降级观察都不合适时，才把删除作为最后手段。
8. Persist project-local evidence and the resume point on the project page. Put reusable observations in `知识候选`; promote them only through the R7/R8 governance rules and only when evidence supports it.

Never treat `结束` as just a goodbye. It means the production project is complete and should be closed cleanly.

Default user-facing closeout:

```text
项目结束
已登记本轮交付与可恢复状态；需要验证的经验保留为候选。
```

Internal closeout checklist:

```text
最终提示词:
[keep the complete latest prompt pack in state; do not display by default]

最终分镜逻辑:
- shot order and story rhythm
- camera/composition pattern
- character, wardrobe, prop, scene, lighting, and screen-direction continuity
- the storyboard-to-prompt conversion method that worked

过程审计:
- 起点与假设: what the skill assumed before real project evidence
- 有效证据: accepted revisions, successful generation feedback, better continuity, and higher production efficiency
- 失败证据: rejected wording, generation failures, repeated corrections, unnecessary steps, and outdated model assumptions
- 因果判断: what actually improved or harmed the result; do not confuse the final version with proof that every included rule helped

规则进化审计:
- 保留: still correct and useful; no rewrite needed
- 强化: repeatedly validated and should become a stronger default
- 改写: useful intent but wrong scope, wording, order, or model assumption
- 合并: duplicates or overlaps another rule; keep one clearer rule
- 降级观察: promising but supported by only one project or uncertain evidence
- 删除: last resort for a rule with no meaningful remaining use; it is optional and may be empty for the project

适用范围:
- 本项目有效: useful only for this story, characters, scene, or current model target
- 同类分镜项目有效: useful for similar AIGC manga/drama storyboard-to-prompt work
- 所有 AIGC 提示词项目默认有效: broad prompt rules that should become default behavior
- 特定模型/版本有效: keep model-specific behavior scoped instead of turning it into a universal rule

下次启动继承项:
- 是否沿用本次提示词结构
- 是否沿用本次镜头分析深度
- 是否沿用本次全局人物/场景/风格/稳定性/避免格式
- 是否沿用本次修改偏好和反例
```

Read [references/closeout-evolution.md](references/closeout-evolution.md) before performing closeout learning or modifying reusable rules.

When evolving rules, prioritize changes that would improve future behavior:

- final prompt field order and what each field must contain
- how global reference images, style, stability, and avoid rules are written once
- how per-shot prompts carry only shot-specific deltas
- which camera/composition/action details made the prompt stronger
- which user corrections prevented a bad default from recurring
- which storyboard structures should become reusable templates

Always use negative evidence. Do not preserve every failure as another warning; use the failure reason to delete, replace, narrow, or merge the rule that caused it.

## Companion Skills

Use companion skills when their trigger fits the material:

- `ffmpeg`: deterministic local preprocessing and FFprobe verification before a specialist receives video, frames, or audio.
- `aigc-manga-video-director`: deep video/reference analysis, shot-by-shot camera movement, storyboard tables, Seedance prompts.
- `audio-to-prompt`: spoken emotion, dialogue, pacing, sound cues, and audio-to-visual prompt fusion.
- `aigc-output-qc`: post-generation video verdict, evidence-backed issue classification, and lowest-cost repair handoff.
- `transcribe`: speech extraction from audio/video.
- `storyboard-image-replacer`: replacing panels in storyboard/contact-sheet images.
- `imagegen` or Cowart image skills: generating or editing bitmap assets when the user asks for images.

This skill should coordinate those outputs into one project state and final prompt pack.

## Quality Check

Before answering in any phase, check:

- The current phase is clear.
- The next requested action matches the active project state.
- Video analysis is not shallow when camera movement, composition, or blocking affects prompt quality.
- `@` image names are bare names without file extensions or paths.
- Global character/scene/style/stability/avoid rules are written once for batch prompts.
- Per-shot prompts contain the actual start-to-end motion, not only labels like "推镜" or "特写".
- Revised prompts are complete blocks unless the user asked for partial edits.
- Separate real generated outputs, user acceptance and content-QC evidence. Invoke `aigc-output-qc` for explicit quality/continuity/lip-sync/repair requests; mere final-file registration does not force editorial QC.
- Accepted defects are recorded as explicit exceptions and are not repeatedly re-flagged.
- QC returns repair deltas; this skill returns the complete updated prompt when revision is required.
- Image-generation prompts are absent unless the user explicitly requested them.
- Closeout audits the entire project process and does not treat the final prompt alone as sufficient evidence.
- Closeout reviews harmful, outdated, redundant, conflicting, or low-value rules instead of only adding new learning; deletion remains optional and requires the strongest evidence.
