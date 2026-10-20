# Seedance Preflight And Bilingual Prompting

Current company workflow: read `company-directing-standard.md` first. Its scoped locks, 2.5 planning profile, viewing-first design and one-complete-version delivery override conflicting legacy examples below.

Use this reference before delivering final Seedance prompts, especially for storyboard-to-video, action shots, prompt revision, multi-shot continuity, or when the user asks whether the video will run well.

Core principle: do a mental Seedance run before output. Do not only ask "is the prompt beautiful"; ask "can this short clip physically execute, preserve identity, follow one camera logic, and end on the intended frame?"

## Preflight Simulation Loop

Before final prompt delivery, silently simulate the clip in this order:

1. **Mode check**: T2V, I2V, V2V, R2V, first/last-frame, edit, extend, or sequence.
2. **Reference role check**: every `@` asset has one main role: identity, first frame, last frame, scene, camera, action, rhythm, audio, style, outfit, or prop.
3. **Start frame check**: the first visible state is clear enough for Seedance to begin without guessing.
4. **Action physics check**: the body can complete the described action within the duration; no impossible teleporting, sudden costume change, or too many attacks.
5. **Camera check**: a motivated viewing structure; physically connected paths within continuous shots, explicit cut/receiving state at edits, valid coverage at hidden transitions. Compound movement is allowed when readable and motivated.
6. **Continuity check**: face, hair, outfit, prop, screen direction, lighting direction, location geography, and emotional state carry from the previous shot.
7. **Occlusion/artifact check**: risky hands, face contact, fast weapon near face, multiple people, fabric, smoke, text, and extreme rotations are simplified or constrained.
8. **Endpoint check**: the last frame is specific: pose, crop, eye line, prop position, environment reaction, and whether motion stops or continues into the next shot.
9. **Retake prediction**: name the most likely failure and repair it before output.

If the preflight finds a serious risk, revise the prompt first. If the risk depends on missing user material, output the prompt plus one short "建议补充/修改" note.

## Preflight Score

Use this internal scoring when useful:

| Item | Pass condition |
|---|---|
| Clarity | coherent viewing tasks with readable state changes, not unrelated event overload |
| Motion | subject movement and camera movement are separated |
| Duration | action fits the clip length |
| Identity | character anchors or `@` roles are strong enough |
| Continuity | previous shot state is not contradicted |
| Endpoint | final frame can be imagined exactly |
| Risk | known failure has a mitigation |

If two or more items fail, rewrite before final output.

## When To Ask The User To Modify

Suggest a user-side modification only when it will materially improve generation:

- Provide a first frame when identity, pose, or composition must be exact.
- Provide a last frame when the ending pose, transformation result, or emotional endpoint must be exact.
- Split production units only when readable action, dialogue, transition, or surface limits require it; multiple beats alone do not require splitting. Preserve current duration and no-cut locks.
- Add a character reference when face, outfit, or prop consistency is central.
- Add a scene reference when location geography, lighting direction, or set scale matters.
- Use a video reference only for camera/action/rhythm, and explicitly forbid identity or scene transfer if needed.

Do not ask for more material when a clear prompt can solve the issue.

## Bilingual Prompt Policy

Mixed Chinese-English prompting is useful as a practical heuristic, not a guaranteed quality switch.

Default for this user:

- Use Chinese for story intent, character emotion, relationship, performance, continuity, scene geography, and user-facing copyability.
- Use concise English for common film/video terms that are often more stable and compact: `slow dolly in`, `locked-off camera`, `shallow depth of field`, `deep focus`, `low-angle medium shot`, `over-shoulder`, `soft rim light`, `hard backlight`, `one continuous shot`, `no cuts`, `no angle switch`.
- Keep the prompt readable. Do not alternate languages every phrase.
- Keep dialogue and on-screen text in the language the user wants to appear or be spoken.
- For less common spoken languages, explicitly mark the language before the line.
- Do not use English to bypass safety filters or hide intent.

Best structure:

```text
中文主体: 角色、剧情、动作、情绪、场景、连续性。
English camera/style tags: slow dolly in, low-angle medium shot, shallow depth of field, soft rim light, one continuous shot, no cuts.
中文稳定性/避免: 保持人物脸型、发型、服装、道具一致，避免手部变形、随机转场、镜头跳切。
```

## What To Keep In Chinese

- character identity and relationship
- emotion arc
- performance details
- dialogue, when the output should speak Chinese
- plot causality
- costume and prop continuity
- scene layout and screen direction
- production notes for the user

Example:

```text
杨戬站在破碎神殿门口，白色战袍被风压向身后，眉心第三只眼微微发光。他先不出手，只抬眼看向远处敌人，表情冷静克制。
```

## What Can Stay In English

Use these terms when they shorten and clarify technical direction:

```text
slow dolly in
slow pull-back
locked-off camera
low-angle medium shot
over-shoulder foreground
shallow depth of field
deep focus
soft rim light
hard backlight
one continuous shot
no cuts
no angle switch
handheld tension
smooth lateral tracking
camera orbits 45 degrees
```

Avoid excessive English adjective stacks:

Bad:

```text
epic cinematic ultra detailed masterpiece cool badass dramatic anime style
```

Better:

```text
低机位中景，人物保持完整剪影；slow dolly in，背景神殿柱子产生轻微视差；soft rim light 勾出发丝和战袍边缘。
```

## Final Prompt Preflight Note

When useful, include a compact note before or after the final prompt:

```text
预演判断: 这个镜头可以跑，但动作量偏高，建议拆成两个 4-6 秒镜头；如果必须一条生成，保留拔剑和定格，删除第二次攻击。
```

For routine prompts, do the preflight silently and only output the improved prompt.
