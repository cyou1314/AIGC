# AIGC Manga Production Playbook

Current company workflow: read `company-directing-standard.md` first. Its scoped locks, 2.5 planning profile, viewing-first design and one-complete-version delivery override conflicting legacy examples below.

Use this playbook for the user's recurring workflow: sketch/rough video analysis, shot language breakdown, storyboard planning, and Seedance 2.5 (company planning profile) prompt writing.

## Default Working Style

Always optimize for production use. The user needs outputs that can be used to generate manga-drama shots, not only film-theory commentary.

Default output language: Chinese.

Default target model for video prompts: Seedance 2.5 (company planning profile; verify the actual generation surface).

Main shot table placement: put the shot table at the very top or the very bottom of the answer. Default to the top for video analysis, storyboard plans, and production handoff. Use the bottom only when a short conclusion or warning must come first. Do not place the shot table in the middle between long analysis sections.

Image reference placement: when the user provides images, place them inline exactly where they are used. The `@` mention should contain only the image name, not position, coordinates, file path, or role/location text. Do not dump all images in a separate reference list if they can be attached to specific shots or prompt fields.

Prompt versioning: default to one complete copyable prompt; provide these variants only when requested:

- `完整制作版`: detailed production prompt using the current full structure.
- `精简版`: compressed copyable prompt under 2000 Chinese characters per prompt.

Style placement: for a batch of prompts, write shared style once as `全局风格` before the prompt list. Do not repeat the same long `风格` text in every shot. In individual shots, use `风格: 同全局风格` only when the block must remain copyable.

Unified reference placement: for character, scene, and style references that apply across the whole batch, describe them once at the beginning and `@图片名` them once there. Individual shot prompts should omit those unified fields by default. Use `同全局人物`, `同全局场景`, or `同全局风格` only when the user asks for each shot to be fully standalone.

Quota policy: keep deep analysis. Save quota by avoiding duplicate wording, repeated style/stability/avoid fields, redundant near-identical frames, and unnecessary all-frame inspection. Do not save quota by making camera movement, composition, blocking, or prompt strategy shallow.

Density policy: write with medium density. Do not overcomplicate outputs with repeated adjectives, long theory, or unnecessary fields, but do not omit practical controls: timecode, needed `@` names, start/end frame, subject action, camera path/evidence, composition change, continuity, generation risks, and avoid constraints. Remove repeated wording before removing control information.

Template policy: treat templates as references and examples, not fixed obligations. For each task, choose the structure that fits the specific material, shot count, camera complexity, reference images, audio, target model, and desired deliverable. When the user provides a template, learn the useful logic, field order, constraints, and negative-control style, then adapt them case by case.

Character anchor policy: when recurring characters matter, create compact character asset anchors before final prompts. An anchor should lock the details that prevent identity drift: face shape, eye design, hair silhouette, outfit layers, key props, posture habits, expression range, and forbidden changes. Put anchors once in `全局人物` and `全局稳定性`; individual shots should only carry deltas such as pose, expression, damage, dust, prop state, or crop risk. Read `character-asset-anchors.md` for the full pattern.

Default Seedance prompt block:

`时间: ...`

`参考图: @图片名 / @图1 / @角色A` when images are provided and relevant. Use only the image name after `@`; strip file extensions like `.png`, `.jpg`, `.jpeg`, `.webp`; the field name explains how it is used.

`首帧: ...`

`运动: ...`

`镜头: ...`

`尾帧: ...`

`风格: ...`

`稳定性: ...`

`避免: ...`

Include `时间` or `时间段` when recreating a source video 1:1. Use source-video timecode/time range, for example `时间: 00:12.4-00:16.8`.

Do not include separate `模型` or `比例` fields unless the user explicitly asks. Treat `时间` as source-video timing, not a Seedance parameter.

## Autonomous Learning Policy

Learn from the user's corrections while working.

When the user says a format, prompt style, analysis method, ratio rule, Seedance behavior, or storyboard convention is better, treat it as a candidate long-term preference.

Persist it into the skill when:

- it can improve future AIGC manga video analysis or production
- it is not a one-off requirement for a single clip
- it does not conflict with a stronger existing rule
- it can be written as a clear operational rule

Do not persist:

- one-time episode-specific plot details
- temporary style experiments
- private project facts unless the user clearly wants them reused
- rules that are ambiguous or conflict with existing constraints

When persisting a rule, update the narrowest relevant file:

- `aigc-manga-production-playbook.md` for workflow preferences
- `seedance-prompting.md` for Seedance prompt behavior
- `character-asset-anchors.md` for recurring character identity, outfit, prop, expression, and anchor rules
- `sketch-video-understanding.md` for rough/sketch video interpretation
- `storyboard-board-production.md` for storyboard board rules
- `shot-language.md` for camera/composition terminology
- scripts only when repeatable automation should change

After updating, tell the user the rule was added and summarize it in one sentence.

## Default Task Routing

### User provides a script or asks to start from script

Do this:

1. Extract recurring characters, scene/time/atmosphere, and emotional beats.
2. Build provisional character anchors for recurring characters before writing final shot prompts.
3. Convert beats into shot IDs and decide which beats need video-style camera detail.
4. Ask for missing character or scene references only when they materially affect consistency.
5. Continue into storyboard planning or prompt writing with global character/scene/style/stability blocks.

### User says "分析视频"

Do this:

1. Run the fast shot pipeline when a local video is available.
2. If it is a sketch/rough storyboard video, enhance frames and read sketch intent.
3. Produce a quick shot map first.
4. Deep-read every important or confusing shot, especially difficult camera moves, composition changes, action peaks, reveals, and continuity-critical beats.
5. Output shot language plus Seedance-ready prompts.

If the user provides still images together with a video, map them to shot IDs or prompt roles first:

- character identity reference: place the image name in `参考图` or `稳定性`
- scene/background reference: place the image name in `参考图` or `首帧`
- start frame: place the image name in `首帧`
- end frame: place the image name in `尾帧`
- composition/style reference: place in `构图`, `风格`, or the shot table `参考图` column
- unknown image role: label as `@图1`, `@图2` and state the inferred use in normal text, not inside the `@` mention

Default sections:

- `快速镜头地图`
- `重点镜头深读`
- `Seedance提示词`
- `连贯性风险`
- `下一步建议`

### User says "做分镜" or "分镜版"

Do this:

1. Convert beats or source video into shot IDs.
2. Keep one main action per shot.
3. Include shot size, camera angle, camera movement, composition, and story function.
4. Add Seedance video prompt for each shot. Add image prompt only when the user explicitly asks for image/still-frame prompts.

Default columns:

`镜头 | 画面 | 动作 | 台词/旁白 | 景别 | 机位 | 运镜 | 构图 | 情绪功能 | Seedance提示词 | 连贯性备注`

### User says "做分镜板"

Do this:

1. Build a board-oriented shot list.
2. Keep panel aspect ratio within `long side / short side <= 2.5`.
3. Include enough notes for drawing, image generation, video generation, and review.
4. If a CSV is created, it can be converted to HTML using `scripts/make_storyboard_board.py`.

Default columns:

`镜头 | 画幅 | 时长/节奏 | 分镜画面 | 角色动作 | 台词/旁白 | 镜头语言 | 构图/调度 | 光影色彩 | Seedance提示词 | 连贯性备注 | 制作备注`

Do not use extreme panel ratios such as `1:3`, `3:1`, `9:26`, or `26:9`.

### User says "写提示词"

Do this:

1. Ask or infer whether the prompt is for image generation, Seedance video generation, or both.
2. If no model is named, assume Seedance 2.5 (company planning profile) for video.
3. Build or update character anchors when recurring characters or character references are present.
4. Include source time/time range when recreating source video; do not output model/ratio fields by default.
5. Insert user-provided images into the prompt where they matter, especially `参考图`, `首帧`, `尾帧`, `风格`, and `稳定性`. Use `@图片名` only; do not include position, coordinates, path, or file extension in the mention.
6. Make camera motion concrete and start-to-end.
7. Output one complete copyable version; add a concise alternative only when requested.
8. If modifying an existing prompt, always return the complete final prompt, not only the changed part.
9. Keep the prompt medium-density: concise enough to copy, complete enough to reproduce the shot. Do not pad with repeated style words or theory.

## Sketch And Rough Animatic Reading

For sketch videos, do not expect finished visual detail. Read the intent:

- frame boundary
- subject placement
- horizon and vanishing direction
- camera height
- tilt/dutch angle
- subject scale changes
- foreground overlap
- motion arrows or repeated poses
- background guide lines
- crop changes

Use confidence labels:

`可确认: ...`

`推断: ...`

`设计补充: ...`

For difficult angles:

`角度拆解: 地平线 / 镜头高度 / 倾斜 / 焦段感 / 景深层次 / 前景遮挡`

For motion:

`运动拆解: 起始画面 -> 运动路径 -> 结束画面`

If several readings are plausible, give 2-3 interpretations and explain what evidence would decide between them.

## Shot Analysis Rubric

For every important shot, cover:

- `画面证据`: what the frame actually shows.
- `运动判断`: camera move, subject move, edit, crop move, or combined motion.
- `构图判断`: geometry, depth, attention path, negative space, screen direction.
- `镜头意图`: pressure, reveal, relationship, rhythm, emotion, clue, reversal.
- `生成难点`: identity, hands, prop, angle, parallax, camera path, continuity.
- `复刻策略`: how to reproduce it in AIGC.

For camera movement, go beyond the movement name. Decompose:

- movement type: physical camera, zoom/crop, subject movement, edit/reframe, or mixed movement
- start/end framing: subject scale, crop, camera height, angle, and screen position
- path and axis: push/pull, pan/tilt, truck, crane, orbit, handheld drift, diagonal move
- speed/easing: sudden, smooth, accelerating, decelerating, stepped, impact shake
- evidence: parallax, foreground occlusion, background reveal, horizon/vanishing-line shift, frame-edge behavior, motion blur, focal-depth change
- production intent: pressure, reveal, surveillance, power shift, disorientation, intimacy, rhythm

Avoid shallow labels. Expand:

Bad: `低角度推镜, 很有压迫感。`

Good: `画面把人物放在下三分之一, 楼梯线向头顶汇聚, 镜头从中景向上推近, 前景扶手向下滑出画面, 使角色从被空间压住变成直面威胁。`

## Seedance Prompt Rules

For each continuous camera shot, use a clear motivated movement logic. A generation prompt may contain multiple shots or beats; choose structure from the viewing task, not a fixed move count.

Prefer:

- one subject action
- one camera path
- one foreground/background motion note
- one clear ending frame
- continuity constraints

Avoid:

- multiple unrelated camera moves
- vague words like "cinematic" without camera detail
- generic emotions without visible action
- changing location or outfit inside one shot
- adding model/ratio fields unless requested
- omitting source time/time range when the task is 1:1 video recreation

When revising prompts, never answer with only the changed segment. Always regenerate the full copyable final prompt block, even if only one line changed.

Default to one complete copyable version. Optional requested variants:

- `完整制作版`: use the full prompt pattern below.
- `精简版`: keep the same timecode, needed `@` references, subject action, camera path, composition change, ending frame, style, and stability constraints, but keep the prompt under 2000 Chinese characters.

Both versions should be medium-density. The full version is production-complete, not bloated; the concise version is shorter, not shallow.

For multiple prompts, write:

`全局人物: [@角色A, @角色B + identity, wardrobe, props, continuity rules]`

`全局场景: [@场景A + location geography, lighting direction, key props]`

`全局风格: [shared manga-drama style, finish, line quality, color logic]`

`全局稳定性: [shared face, hair, outfit, props, screen direction, lighting direction]`

`全局避免: [shared negative constraints]`

Then omit repeated full character, scene, style, stability, and avoid wording from each shot. Do not write `参考图: 同全局参考图`, and do not include a `风格` field when it is simply the global style. Use `人物: 同全局人物`, `场景: 同全局场景`, `风格: 同全局风格`, `稳定性: 同全局稳定性` only when the user asks for standalone per-shot prompt blocks. Only add shot-specific notes when that shot intentionally changes character state, location details, lighting, color, finish, or texture.

Prompt pattern:

`时间: [原视频时间段/时间码；如未知，用镜头编号加约略时间，不要编造精确时间].`

`参考图: [@图片名 / @图1 / @角色A；只放本镜头真正需要的非全局图片，@ 后只写名字，不写位置、路径、后缀].`

`首帧: [角色/姿态/构图/环境/光线].`

`运动: [主体动作 + 场景运动 + 情绪变化].`

`镜头: [景别/机位/镜头路径/速度/焦段感/景深].`

`尾帧: [最终构图/表情/动作状态].`

`风格: [漫剧视觉风格/线条/光影/色彩/完成度].`

`稳定性: [脸/发型/服装/道具/场景/光线方向/视线方向].`

`避免: [脸崩/手崩/服装变化/背景跳变/乱抖/水印/文字].`

## Timed Storyboard Prompt Contracts

Apply these contracts whenever a user asks for a generation-ready video prompt from storyboard boards, audio, or endpoint images.

- **实际素材引用契约**: inspect the assets that actually exist in the supplied folder or attachments before writing the prompt. Use only those real bare `@name` references, without file extensions. Assign each reference one explicit role in normal text. Never mention an absent video, audio, image, or board reference.
- **复合分镜时间映射**: when one board image contains several internal panels, every timed prompt segment must name both the board and its internal panel or panel range, for example `0.00-1.20秒｜@分镜1·内部分镜1→2`. Do not write only a global board list and leave the timeline unmapped.
- **台词与对嘴时间契约**: every spoken beat states the speaker, exact line, and exact time range. A supplied `@audio` controls voice, tone, pacing, pauses, and lip-sync timing; the visual instructions control camera and performance. When compressing to a user-specified target duration, compress non-dialogue or off-face beats first and preserve visible lip-sync sections at normal speed.
- **目标时长契约**: the user's requested generation duration overrides the source clip duration. Build a timeline that ends exactly at that target. Do not add source-duration, speed-ramp, or post-production slowdown instructions unless the user requested them.
- **运镜分解契约**: write the camera change inside each relevant time block and distinguish `摇` (pan/tilt from a fixed camera position), `移` (truck/pedestal/track), `推/拉` (dolly in/out), and `滚转/倾斜`. State direction, path, speed or easing, subject being followed, and the ending framing. Do not infer a movement type that is unsupported by the reference.
- **场景非转移契约**: storyboard composition and scene geography decide what exists in frame. A broader scene reference transfers only explicitly requested attributes such as material, palette, atmosphere, or texture. Do not import landmarks, props, openings, altars, beams, or lighting events that are absent from the storyboard unless the user asks for them.
- **尾帧精确锁定**: when a final-frame image is supplied, it is the exact endpoint for shot size, camera height and angle, roll, crop, character pose, and composition. The camera may move toward that endpoint, but once it arrives it stops: no continued pull-back, pan, tilt, track, or roll. Character breathing, cloth, hair, flame, petals, and other motivated micro-motion may continue unless the user requests a frozen frame.
- Keep project-specific facts project-specific. Details such as a particular hand staying out of frame, petal color, flame color, named character action, or one-off effect are not reusable defaults unless the user explicitly promotes them to a project rule.

## Continuity Checklist

Check every generated shot for:

- same character face and hairstyle
- same outfit and key props
- same character anchor invariants unless a shot explicitly changes them
- same location geography
- consistent eye line
- consistent screen direction
- believable lighting direction
- emotion progression
- shot-to-shot action continuity

If the prompt may break continuity, add a `连贯性风险` note.

## Deliverable Levels

Use the smallest useful deliverable unless the user asks for more.

### Quick

Use for first-pass understanding:

- shot map
- 3-5 important shots
- concise Seedance prompt examples

Even in Quick mode, important camera movement and composition claims must include evidence. Keep the answer shorter by reducing repetition, not by using vague labels.

### Standard

Use for normal production:

- full shot table
- deep read for key shots
- Seedance prompt per shot
- continuity notes

### Detailed

Use when the user asks to go deep:

- shot map
- per-shot evidence and interpretation
- storyboard board fields
- image prompts only if explicitly requested
- Seedance prompts
- negative prompts
- continuity and generation risk notes
- optional CSV/HTML board

## Final Response Preference

Keep final answers practical:

- place the main shot table at the top by default, or at the bottom if it works better as an appendix
- do not bury the shot table between analysis paragraphs
- when images are supplied, put `@图片名` references where they are used; strip `.png/.jpg/.jpeg/.webp` suffixes; for unified character/scene/style references, mention them once in the global block, not repeatedly in every shot
- provide one complete copyable prompt by default; a concise alternative under 2000 Chinese characters is optional when requested
- keep deep analysis for important shots; save quota through less repetition and better frame selection, not through shallow reading
- keep wording medium-density: simple and direct, but preserve timecode, camera path/evidence, composition change, continuity, and generation risks
- choose templates case by case; do not hard-apply a template when the material needs a different structure
- lead with what was analyzed or created
- give tables for production data
- keep prompts easy to copy
- mention files generated if any
- do not over-explain tools unless the user asks
