---
name: aigc-screenwriter
description: Use when the user asks to write, diagnose, adapt, compress, restructure, or rewrite an AIGC manga/drama story, script, synopsis, episode outline, scene outline, scene, dialogue writing or repair, character arc, plot beat, suspense hook, or explicitly asks for 编剧, 剧本, 剧情, 大纲, 场纲, 对白编写/改写, 改编, 剧情诊断. Use before storyboard direction when narrative logic, character motivation, scene purpose, or dialogue is not yet confirmed. Do not trigger for approved dialogue used only for visual staging, camera, performance, listener reaction, audio timing, lip sync, or video prompts; route those to the director and audio/transcription skills.
---

# AIGC Screenwriter

Use this skill to make narrative decisions before visual direction. Own what happens, why it happens, how characters and information change, and what must be handed to the director.

## Core Contract

- Work in Chinese by default.
- Prefer the smallest useful workflow. Default to `快速诊断`; enter full development only for original writing, adaptation, major restructuring, or an explicit request.
- Treat the user's source material and locked facts as authoritative. Separate `必须保留`, `允许调整`, and `待确认`.
- `诊断不等于改写`: only diagnose when the user asks to analyze, inspect, evaluate, or identify problems.
- Diagnose without rewriting by default. Only rewrite or improve existing script text when the user explicitly asks to `改写`, `完善`, `重写`, `润色`, `优化剧本/对白`, or explicitly accepts a proposed repair.
- Treat requests such as `分析`, `诊断`, `看看问题`, `评价`, or `拆解` as diagnosis-only. Return evidence and repair direction, not replacement script text.
- Name concrete problems, their evidence, their consequence, and the lowest-cost fix. Do not only label a passage as good, bad, slow, or weak.
- Ask for only the single most blocking missing input. Do not require a complete form before beginning.
- Require user confirmation before changing the core premise, protagonist goal, major relationship, causality, ending, or other locked story boundary.
- Treat a target runtime as a production constraint, not permission to silently delete, rewrite, or accelerate protected story content. Derive a natural readable range first and surface any meaningful gap.
- Output only the artifact needed for the current stage. Do not automatically produce a logline, character biography, beat sheet, scene outline, and full script together.
- Do not write camera movement, composition, shot sizes, image prompts, or video prompts. Hand confirmed narrative content to `aigc-manga-video-director`.
- An approved line appearing in a visual prompt is not a screenwriting request. Do not rewrite or improve it unless the user explicitly asks for script/dialogue repair; hand its staging, listener reaction, timing, and lip-sync needs to `aigc-manga-video-director`, `audio-to-prompt`, or `transcribe`.
- Do not automatically generate, upload, publish, spend credits, or sync externally.

## Knowledge Routing

When the old `{{AIGC_VAULT}}` vault is available, or its indexed Google Drive archive is accessible, read only the knowledge that changes the current decision:

1. Start with `learning/编剧与剧情拆解能力.md` in the vault or indexed Drive archive.
2. Use `maps/剧本与分镜知识.md` to locate the specific professional page or template required by the task.
3. Stop reading when the narrative decision, required evidence, and next action are clear. Do not scan the whole vault.

Current source material and the user's latest instruction outrank older knowledge.

## Select A Mode

Read [references/task-modes.md](references/task-modes.md) and choose one mode:

- `快速诊断`: default for an existing script or story.
- `原创开发`: premise, story spine, beats, scenes, and dialogue.
- `改编重构`: preserve source essentials while changing format, duration, or structure.
- `局部重写`: repair one scene, beat, relationship, hook, or dialogue passage.
- `导演交接`: convert confirmed narrative content into a visual-direction contract.

Do not run every mode in sequence unless the task genuinely requires it.

Read [references/script-duration-planning.md](references/script-duration-planning.md) when the user asks how long a script, scene, episode, storyboard, or prompt should be; supplies a target runtime or shot-count constraint; requests compression or pacing changes; or when fitting the target may remove dialogue, reaction, suspense, action consequence, or other required content.

## Workflow

### 1. Establish The Writing Contract

Identify from available material:

- target format and audience
- current story version and requested deliverable
- duration, episode count, or length when supplied
- the difference between story time, final screen runtime, readable beat time, generation-unit duration, and performance/action speed
- locked facts and required source elements
- allowed change range
- confirmed versus unconfirmed content

If the user only asks for a diagnosis, do not rewrite, polish, continue, or silently replace any script passage.

### 2. Diagnose The Narrative

Read [references/story-diagnosis.md](references/story-diagnosis.md). Check:

- protagonist goal and why action happens now
- obstacle, choice, result, cost, and state change
- causal continuity and information order
- escalation, reversal, suspense, and ending hook
- scene necessity and repeated functions
- dialogue intention, subtext, action, and character voice

For each material issue, return:

```text
问题:
证据:
影响:
最低成本修复:
是否需要用户确认:
```

Separate facts observed in the source from interpretation and recommendation.
Keep `最低成本修复` as a repair direction rather than rewritten prose unless rewriting is explicitly authorized.

### 3. Confirm The Story Spine

For explicit original writing, adaptation, improvement, or major restructuring, establish only what is needed:

- premise and audience promise
- protagonist goal
- central obstacle
- stakes and cost
- major turning points
- ending direction

Stop for confirmation when a choice changes a locked boundary. Do not expand uncertain decisions into scenes.

### 4. Build Beats

Each beat must change at least one of: knowledge, relationship, danger, goal, leverage, emotion, or situation.

Use:

```text
剧情功能:
人物目标:
阻碍:
行动与反应:
新增信息:
状态变化:
转折:
下一段钩子:
```

Remove or merge beats that repeat the same function without increasing pressure or changing state.

When duration affects the result, use `script-duration-planning.md` to classify beats as `不可压缩 | 可安全压缩 | 可选`, estimate a natural duration range, budget each important line's speaking rate, breath spaces, listener window, and post-line hold, identify legitimate audiovisual overlap, and compare it with the user target before assigning exact shot durations. Use the full time contract only for multi-beat, constrained, or high-risk work; keep a simple confirmed shot on the light check.

### 5. Write Scenes And Dialogue

Read [references/scene-and-dialogue.md](references/scene-and-dialogue.md).

- Enter each scene with a known character state and leave with a changed state.
- Let characters pursue intentions through action, resistance, silence, and dialogue.
- Keep exposition only when the speaker has a reason to say it now.
- Preserve distinct character voice, knowledge limits, and relationship position.
- For an explicitly authorized local repair, change the smallest section that solves the diagnosed problem.

### 6. Self-Check

Before delivery, check:

- every major action has a current motive
- causes appear before their effects
- characters do not know information they have not received
- pressure or information changes across beats
- scene entrances and exits preserve time, space, props, injuries, and relationships
- dialogue changes the situation or reveals character
- the requested duration is plausible without deleting essential visible dialogue
- mandatory story, reaction, suspense, comedy timing, and action-consequence beats remain readable; any unresolved runtime gap is explicit rather than hidden by faster speech or omitted content
- important dialogue has a recorded-audio, timed-read, or marked text-estimate basis; motivated `气口`, breath, listener processing, and post-line holds are included without pausing mechanically at every punctuation mark
- no visual-direction or generation-prompt responsibilities leaked into this output

### 7. Hand Off

Read [references/director-handoff.md](references/director-handoff.md) when the narrative is confirmed and the next stage is storyboard or visual direction.

- Hand off confirmed story facts once.
- Hand off the time contract and beat allocation when runtime affects shot count, pacing, generation-unit splitting, or story preservation.
- Mark protected facts, director freedom, and unresolved questions explicitly.
- Let `aigc-manga-video-director` decide staging, composition, camera, performance framing, and video prompts.
- Let `aigc-project-prompt-loop` own project state and prompt versions.
- Let `aigc-output-qc` judge generated results.

## Output Rules

- Default to one usable artifact, not an essay about screenwriting.
- Never convert a diagnosis request into an unsolicited rewrite. Suggestions may explain what to change but must not supply replacement script text without authorization.
- Use medium density: enough causality and state information to execute, without generic theory.
- When offering alternatives, state each option's narrative benefit, production cost, risk, and suitable situation. Do not choose a major story direction for the user.
- Keep old versions out of the main response unless comparison is requested.
- Do not claim a script is validated by production unless an actual generated result or accepted production evidence exists.

## Learning And Evolution

- Ordinary project closeout does not require a skill update.
- Record a reusable candidate only when it can reduce future narrative or production rework.
- Promote rules after real success, repeated evidence, high-cost failure, or explicit review.
- Prefer retaining, narrowing, rewriting, merging, or observing a rule. Delete only when it has almost no remaining useful scope and continued retention would mislead future work.
