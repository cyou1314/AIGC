# Script Duration Planning

Use this reference when a script, scene, episode, storyboard, or prompt must fit a runtime; when the user asks how long it should be; or when a target duration may force story loss. The purpose is to derive a readable duration from narrative content before assigning shots.

## Separate The Five Clocks

Never treat these as interchangeable:

1. `故事时间`: how much time passes inside the fictional world.
2. `成片时长`: how long the audience watches the scene, sequence, or episode.
3. `节拍可读时间`: how long each story beat needs to be perceived, understood, and felt.
4. `生成单元时长`: the duration allowed or chosen for one model generation or extension.
5. `表演/动作速度`: how quickly a character speaks, reacts, or moves inside the shot.

`动作更快` does not automatically mean `成片更短`. A platform's generation-unit limit determines splitting and handoff strategy, not permission to compress the story.

## Authority Order

Use this order when constraints conflict:

1. exact supplied audio, timecode, or locked dialogue performance
2. mandatory story beats and protected facts
3. user target runtime and delivery format
4. genre rhythm and audience comprehension
5. model generation-unit limits

A target runtime is a production constraint, not silent permission to delete or rewrite protected story content. When it cannot fit safely, show the conflict and ask for the smallest decision that changes the result.

## Build The Time Contract

Record only the fields needed for the current task:

```text
时间合同:
目标成片时长:
自然时长区间:
依据: 实际音频 | 已确认时间码 | 文本估算 | 分镜估算
不可压缩节拍:
可安全压缩节拍:
可选节拍:
对白/音频锁定:
空间建立与信息揭示预算:
人物反应与决策预算:
动作准备/接触/后果预算:
转场与剪辑接口预算:
合法重叠:
生成单元限制:
差额:
结论: 可直接规划 | 可安全压缩 | 需拆生成单元 | 建议延长 | 需确认删改剧情
```

For one simple, already confirmed shot, use a light check: primary beat, readable action/reaction, dialogue/audio, endpoint, and whether they fit. Do not force the full contract onto every prompt.

## Estimate Natural Runtime

Use a range first. Avoid fake frame-level precision before audio, performance, or storyboard timing exists.

```text
自然时长区间
= 锁定对白/音频
+ 可读动作阶段
+ 反应与决策
+ 空间建立/信息揭示
+ 必要停顿、后果和剪辑接口
- 能同时被清楚理解的合法重叠
```

Do not double-count a sound bridge, off-screen line, or reaction that can genuinely overlap another visual beat. Do not overlap two elements when the audience must read both separately.

The following are planning starting points, not hard quotas or model guarantees:

| Beat type | Initial planning range | Protect |
|---|---:|---|
| simple establishing or empty shot | 2-5 s | geography, clue, absence, pressure, or reveal job |
| one simple readable action | 2-4 s | preparation and a clear endpoint |
| causal action with contact/consequence | 4-8 s | trigger, preparation, contact, consequence, settle |
| emotional reaction or decision | 2.5-6 s | trigger, internal change made visible, decision endpoint |
| suspense setup to reveal | 4-10 s | expectation, delay, evidence, reaction or reveal |
| dialogue from real audio | actual audio plus needed reaction/edit handles | normal delivery and required lip visibility |
| text-only Chinese dialogue | infer roughly 3-4 Chinese characters/s, then add pauses and listener response | mark as inferred until performed or recorded |
| montage insert | 0.7-2.5 s | only when immediate recognition is enough |

Adjust after considering staging, number of active subjects, action complexity, unfamiliar information, emotional weight, and whether a reaction must be read. Never turn these ranges into a universal average shot length.

## Dialogue Time And Breath-Space Contract

Do not estimate a dialogue scene from character count alone. For every important line or conversational turn, budget:

```text
对白轮次时长
= 开口前的注意/吸气/决定
+ 实际发声
+ 句内停顿、换气、犹豫或强调
+ 未与发声合法重叠的听者反应
+ 句尾气口、余韵、决定或切镜接口
```

Record when useful:

```yaml
speech_timing:
  speaker:
  exact_line:
  evidence: recorded_audio | timed_read | text_estimate
  delivery_mode: restrained | natural | urgent | overlapping | whispered | shouted
  estimated_or_actual_rate:
  pre_speech_cue:
  spoken_duration:
  internal_pauses_and_breath:
  breath_spaces: physiological | semantic_turn | emotional_processing | listener_or_edit
  overlap:
  listener_reaction_window:
  post_line_hold:
  total_turn_budget:
  confidence:
```

Authority and estimation:

1. `recorded_audio`: use actual onset, offset, pauses, breaths, interruptions, and tails.
2. `timed_read`: when exact dialogue exists but no final audio, one natural read in the intended emotion is better than a formula. Keep the measured time plus any visual reaction or edit handle that was not present in the read.
3. `text_estimate`: normalize punctuation, numbers, dates, English, acronyms, and stage directions into how they would actually be spoken. Then use a range and mark it inferred.

Text-only Chinese planning ranges are candidate starting points, not performance requirements:

| Delivery | Rough spoken-unit rate | Use and risk |
|---|---:|---|
| restrained, hesitant, grief, suppressed emotion | about 2.0-3.2 Chinese spoken units/s | protect breath, hesitation, and thought change; character count strongly underestimates time |
| clear natural conversation or exposition | about 3.0-4.5 units/s | default estimate; add phrase pauses and listener processing |
| urgent, argument, command, panic | about 4.0-5.5 units/s | use mainly for short phrases; clarity and lip sync risk rise quickly |

Whispering and shouting are delivery qualities, not automatic speed settings. Urgency is often clearer through shorter clauses, interrupted breath, fast turn-taking, and motivated overlap than through forcing every syllable faster.

Treat `气口` as a deliberate time unit, not empty delay:

- `生理换气`: supports sentence length, exertion, crying, shouting, injury, or fatigue.
- `语义转折`: separates ideas so an important word or reversal can land.
- `情绪消化`: lets thought, fear, shame, grief, calculation, or resolve become visible.
- `听者/剪辑气口`: gives the partner a readable response or creates a clean cut, sound bridge, reveal, or reaction endpoint.

Initial text-planning ranges may be useful: a short phrase/breath space about `0.2-0.5 s`, a semantic or listener-processing space about `0.5-1.2 s`, and a major emotional/suspense hold about `1.2-3.0 s`. These are candidates, not fixed punctuation rules. Do not insert a pause at every comma; keep only the gasps, holds, and silences that perform a narrative, acting, physical, or editorial job. Replace estimates with timed performance as soon as it exists.

Do not double-count a listener reaction that occurs clearly under the speaker's audio. Add separate time when the reaction, decision, joke, reveal, or power change must land after the line. In multi-speaker scenes, intentional overlap can shorten screen time but increases comprehension, speaker-identity, and lip-sync risk; never use overlap only to force the script into a target duration.

If an approved line does not fit, first simplify or move simultaneous visual action, carry audio over a listener/insert/next shot, split at a meaningful breath space, or extend the shot. Shorten or rewrite the line only when the user requests or confirms dialogue revision.

## Genre And Scene-Type Planning

- `动作/打斗`: protect anticipation, force path, contact, consequence, and recovery. Speed may shorten transitions, but impact still needs a readable before/after.
- `悬疑/惊悚`: protect withheld information, off-screen cue, delay, observer reaction, and reveal. Removing the pause may destroy the scene rather than improve pace.
- `情感/关系`: protect listener reaction, silence, hesitation, distance change, and decision. Dialogue length alone underestimates the scene.
- `喜剧`: protect setup, expectation, beat, payoff, and reaction. Cutting the gap often removes the joke.
- `信息/剧情推进`: protect causality and comprehension. Compress repeated explanation before accelerating essential exposition.
- `蒙太奇/音乐段落`: group images by phrase, energy change, or story progression; do not force a cut on every beat.
- `环境/氛围`: keep time only when the environment establishes geography, pressure, clue, absence, aftermath, or transition. Decorative atmosphere is compressible.

## Resolve A Runtime Conflict

When `目标成片时长` is shorter than the safe natural range, use this order:

1. remove repeated information, decorative actions, and duplicate reaction beats
2. overlap compatible sound and image beats without reducing comprehension
3. shorten entrances, exits, neutral travel, and off-face non-dialogue action
4. merge beats only when their function, causality, and state change remain readable
5. split the work into generation units while preserving the intended final runtime
6. recommend a longer runtime or a second scene/episode/Block
7. delete, rewrite, or move protected content only after explicit user approval

Keep visible dialogue and required lip sync at normal performance speed. Do not solve a duration gap through unnatural fast speech, unrequested slow/fast motion, or by omitting listener and consequence beats.

When a meaningful conflict remains, present at most three production choices:

```text
方案A 自然版: duration range; benefit; cost; risk; suitable use
方案B 安全压缩版: target; exactly what is compressed; benefit; cost; risk
方案C 改剧情版: only with confirmation; exactly what would be removed/moved and what meaning is lost
```

Do not choose a story-changing option for the user.

## Beat Allocation Handoff

Before shot planning, hand the director a compact allocation table:

```text
节拍ID | 剧情功能 | 必须/可压缩/可选 | 音频依据 | 自然区间 | 目标分配 | 可重叠项 | 镜头数候选 | 风险
```

The screenwriter protects story function and estimates readable beat time. The director decides shot count, shot duration, visual overlap, cut points, camera, blocking, and edit handles. The project loop owns the confirmed target, unresolved gap, generation-unit plan, and version state.

Lock exact shot durations only after real audio, a confirmed storyboard, or a user-approved allocation makes exactness useful. Otherwise preserve ranges and assumptions.
