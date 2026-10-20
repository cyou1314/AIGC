<!-- Adapted from user-supplied MIT reviewer; see ../scripts/LICENSE.prompt-review-checks. -->

# 相邻分镜空间连续性检查

Read [公司提示词审查](company-prompt-review.md) for the trigger and permission mode first. Review existing prompts; do not generate a new story, train a model, or install the source repositories. User permissions outrank upstream camera preferences.

## Input and permission

Accept labeled or equivalently clear inputs:

```text
【上一分镜提示词】
……完整提示词……
【下一分镜提示词】
……完整提示词……
【模式】
只检查，不修改。
```

Or an explicit editing mode:

```text
【模式】检查并只修改下一分镜的画面部分，其他内容保持不变。
```

Absent mode means review only. If one prompt is missing, extract what is available and mark the missing boundary `需要人工判断`; do not invent it or pronounce a pair continuous. For authorized changes, follow [公司审查与权限](company-prompt-review.md). Return the **entire next prompt**, not both prompts concatenated and not only a patch. Never change the previous prompt unless separately authorized.

## Extract the actual boundary

1. Read both complete prompts, using their global locks as context. Identify the previous prompt's **last shot, after its final action/camera move**, and the next prompt's **first shot, before its first new action**. A later corrective move does not repair a contradictory opening frame.
2. Process turns, movements, releases, transfers and cuts in chronological order. A character who starts left but ends right is right in the outgoing state. If a range contains several cuts, use its last/first actual shot, not the whole range's initial composition.
3. Extract only stated facts or uniquely determined consequences. Preserve exact names and `@` tags. An unseen reference image supplies no verified positions. If prior footage is supplied and inspected, distinguish observed state from prompt intention; otherwise never claim to have inspected frames.
4. Quote the supporting time range and exact phrase for each fact. Record ambiguity or absence explicitly. A cropped-out person/prop is not an exit, disappearance, release, or transfer.
5. Maintain a row per character and prop. Do not collapse three-person scenes into one permanent pair: name the dominant speaker–listener relation for each turn and rebuild the axis when that relation changes.

### Boundary state tables (internal first, summarize in output)

| Field | 上一分镜结束状态 | 下一分镜开场状态 |
|---|---|---|
| Visible people | actual visible names, partial bodies | actual visible names, partial bodies |
| Screen placement | left/center/right for each | left/center/right for each |
| Depth | foreground/midground/background for each | foreground/midground/background for each |
| Body | orientation relative to scene anchors AND screen-facing when known | same two coordinate descriptions |
| Gaze | target, horizontal direction, height | target, horizontal direction, height |
| Pose | standing/sitting/kneeling, supports/contacts | opening pose and supports/contacts |
| Action | `action_end`, completed/in-progress result | `action_start`, receiving state before new action |
| Motion | `motion_vector`, exit edge | `motion_vector`, entrance edge |
| Props | exact tag, owner, anatomical left/right/both hands, state | exact tag, owner, anatomical hands, state |
| Dialogue | current speaker and OS/VO/onscreen mode | current speaker and mode |
| Face | main readable face and front/three-quarter/back view | main readable face and view |
| Foreground | person, back/back-of-head/shoulder/front | person and view |
| Lip-sync | stated current owner/silence | sole owner, all visible people who must remain silent |
| Camera | angle, position, movement endpoint | angle, position, movement startpoint |
| Axis | owning pair or direction of travel, fixed orientation of axis | owning pair/direction and axis orientation |
| Camera side | identified side of that axis, or unknown/on-axis | side of the same oriented axis, or unknown/on-axis |
| Evidence | quotes; unknown or inferred facts labeled | quotes; unknown or inferred facts labeled |

### Handoff vocabulary

- `action_start` / `action_end`: physical state at the boundary, not a mood or the action's name alone. Distinguish raising a hand, holding it raised, lowering it; do not repeat a completed strike as a new start.
- `handoff_out` / `receiver_in`: the key facts the prior shot hands over and the next must receive. Carry an unseen person's/prop's established state as offscreen continuity, without forcing them into a close-up.
- `motion_vector`: screen movement direction, distinguished from the edge crossed. In an ordinary same-direction cut, exiting right and entering from the **left** can both mean movement toward screen-right. Exiting right and entering right is suspect only when the route, camera relation and uninterrupted travel establish that it is a reversal.
- `spatial_bridge`: the evidenced movement, neutral view, landmark, re-establishing view, or other device that makes the changed geometry readable. “自然切换” alone establishes nothing.
- `prev_transition` / `next_transition`: incoming/outgoing edit relationship and its evidence (action match, reverse, eyeline match, deliberate discontinuity). An L/J-cut is an audio bridge, not automatic permission to flip visual geography.

## Compare without inventing geometry

Check the following against both quotes and the bridge:

- Screen-left/right swaps without a stated movement under an established unchanged screen mapping.
- Body direction changes without a turn; front/back exposure changes without a camera change or turn. A legitimate reverse **does** change foreground depth and visible face without requiring the actor to turn.
- Gaze misses an explicitly required interlocutor or known target position/height. An authored glance away is not an eyeline error. Do not infer camera side from “平视/仰拍/近景” alone.
- Exit/entry edges and motion vectors imply unintended return, or a pursuit loses its established direction.
- A continuing action resets, repeats, skips an essential state, or a hand is assigned incompatible simultaneous tasks.
- A prop changes holder or anatomical hand without a transfer; reversal of the camera never swaps anatomical left/right hands.
- A reverse contradicts the pair's established positions or gaze, or the camera crosses the evidenced oriented axis without a legal bridge.
- The next opening fails to receive a key outgoing pose, support/contact, prop state or action endpoint. A missing description is uncertainty, not proof that the object disappeared.

Same-side reframing can move one person's head from center to a third of frame; do not call that a physical relocation. If mapping/camera placement is unclear, mark uncertainty rather than equating every screen coordinate change with teleportation. Do not require identical pixel composition across independent clips.

### Legal crossing / rebuilding

Accept these when actually described, not just selected by name:

1. Camera visibly travels across the established line.
2. Characters visibly move and establish a new relation axis.
3. An on-axis neutral shot bridges to the new side.
4. A wide establishes the new positions.
5. An insert/empty shot is followed by an explicit re-establishment of the space. An insert alone is insufficient.
6. The user explicitly requests intentional crossing; label it intentional, not accidental.

Track which axis, side, and spatial relations were rebuilt. A legal rebuild excuses only related camera-relative changes, not arbitrary hand swaps, wardrobe changes, action resets, or violation of an immutable user lock. Do not add a wide when the user has locked close-ups; describe an allowed camera move/other bridge if possible, otherwise report the permission limit.

A statement such as “先给同轴中性镜头，再切到北侧，重新交代B左A右” is sufficient textual bridge evidence: it supplies sequence and new geography. Do not demand an extra timestamp or invented camera coordinates. A bare “重置轴线” or an isolated vase insert without subsequent spatial establishment is insufficient. If the prior side is unknown, a repair may say “沿用上一镜同一轴线侧”; never invent north/south or rewrite the locked previous prompt to support that choice.

When geometry is insufficient, write exactly:

> 需要人工判断：现有提示词不足以确定摄影机是否跨越180度轴线。

## Dialogue / shot–reverse-shot

For triggered live dialogue load [公司审查与对白](company-prompt-review.md) and audit **each turn** across the two boundary shots (and any subsequent shot affected by the repair): speaker, readable face, foreground listener/back/head/shoulder, sole lip owner, silent people, explicit reverse cut, screen positions, gaze, and axis side.

In established reverse-shot coverage, a new speaker requires “切至反打镜头”; “焦点转移” cannot move the camera to reveal an occluded face. Preserve clear front/three-quarter speaker face and unobstructed mouth; an OTS listener appears as back/head/shoulder, never a competing front-facing speaker. For a fixed wide two-shot without conflict or an authorized clean single, preserve that composition and do not force OTS foregrounds. Pure OS/VO/phone/broadcast does not require the remote speaker to appear.

Example contract: Draven is screen-left facing right; Raven screen-right facing left. Raven speaks with Draven left-foreground back/shoulder. On Draven's line, cut to the reverse on the same axis side: Draven left readable face; Raven right-foreground back/shoulder. Only the current speaker lip-syncs. These names/positions illustrate a contract, not a universal scene template.

## Output (paired-prompt review)

Use these sections, including unknowns rather than filling them with invented facts:

```text
【检查结论】通过 / 存在确定冲突 / 需要补充信息 / 未触发
【上一分镜结束状态】已提取状态、证据时间段、未知信息。
【下一分镜开场状态】已提取状态、证据时间段、未知信息。
【镜头状态交接】动作、位置、方向、视线、道具是否连续。
【人物关系与轴线】关系轴、画面左右、朝向、视线、摄影机轴线侧、越轴判断。
【对话站位】仅在对白检查触发时输出。
【问题列表】逐条列出下列五项；无问题时写“无”。
- 问题等级：确定冲突 / 需要人工判断 / 建议优化 / 未触发此检查器
- 上一分镜证据：时间段与原文；缺失则明确写未说明。
- 下一分镜证据：时间段与原文；缺失则明确写未说明。
- 判断理由：具体状态关系；区分事实与推断。
- 最小修改建议：指向下一分镜画面；仅建议不等于授权执行。
【修改后的完整提示词】仅在明确授权修改时输出完整下一分镜。
提示词内部一致性已检查；实际生成效果未验证。
```

Conclusion precedence: a definite conflict → 存在确定冲突; otherwise material missing information → 需要补充信息; otherwise → 通过 (may include suggestions). 未触发 means no boundary audit performed: include `未触发相邻分镜空间连续性检查。`, mark the state/axis sections 未检查, and omit dialogue and rewritten output unless separately requested. Do not report both “未触发” and “已通过全部空间检查”.

Only missing facts that affect this boundary's judgment block a pass (e.g. camera side for an alleged crossing, hand ownership for a prop handoff). A missing eye height when no height mismatch is implicated, or an irrelevant background detail, can stay unknown without blocking. Do not require every table cell to be populated.

## Deterministic ledger interface

Run `python3 scripts/prompt_review_checks.py handoff --input pair.json --json` after semantic extraction. No raw-prose parser or film-space inference is promised. Use JSON null for unknown; an empty list is an explicit empty set only when evidenced. The reviewer assigns shared canonical state tokens before comparison: different paraphrases are not automatically different physical states.

Payload keys:

- `context`: optional boolean gate signals `user_requested_spatial_check`, `known_spatial_conflict`, `live_dialogue`, `speaker_change`, `shot_relation`, `spatial_action`, `continuous_action`, `explicit_screen_position`, `two_or_more_share_scene`; exemptions `independent_single`, `pure_noncharacter`, `unrelated_montage`, `pure_audio`, `locked_fixed_wide_no_conflict`, `clear_without_spatial_handoff`.
- `previous_end`, `next_start`: `evidence` (time range + quote), `visible_characters`, `characters` (map keyed by exact name), `props` (map keyed by exact tag), `speaker`, `dialogue_mode`, `dialogue` (existing per-turn dialogue ledger row), `axis: {id, side}`, `camera_angle`, `camera_motion`, `unknowns` (material uncertainties only), optional `noncritical_unknowns` (reported but not blocking). Fields may be unknown; the script must not turn omissions into proven crossings.
- Each character: `screen_position`, `depth`, `body_orientation` (scene-relative, NOT camera-relative), `screen_facing`, `gaze_target`, `required_gaze_target` (only if explicitly required), `pose`, `face_view`, `motion_vector`, `exit_edge` or `entry_edge`, `action_end` or `action_start` (canonical physical-state token), `evidence`. Use `camera_angle`/motion strings for reporting, never automated geometry from those words.
- Each prop: `holder`, `hand`, `state`, `evidence`. Missing from a tighter frame means unconfirmed/offscreen, not owner=null.
- `handoff_out`, `receiver_in`: maps of canonical key-state tokens that must match unless a corresponding evidenced event bridges them; `next_transition`, `prev_transition`: edit relation tokens, when specified.
- `bridge`: `continuous_time` (true only for uninterrupted continuity), `screen_mapping_preserved` (true only for established matching projection), `camera_changed` (true/false/unknown), `events` and optional `axis_reset`.
- Each event: `subject` (exact person/prop/key), `field` (the compared field), `from`, `to`, `evidence`. Events must occur before the next opening state, not afterward. They explain only that transition, not unrelated mismatches.
- `axis_reset`: `kind` in `camera_crossing`, `character_reblocking`, `on_axis_neutral`, `wide_reestablish`, `insert_reestablish`, `intentional_cross`; nonempty `evidence`; `spatial_relation_established: true`; for intentional crossing also `user_requested: true`. Values are extracted assertions, not proof of rendered motion.

The CLI returns status, conclusion, routing reasons, extracted states, and issues containing both evidence fields, rationale and minimal suggestion. Its `通过` only concerns supplied canonical facts. It does not certify extraction completeness, real camera geometry, generated video or platform support. Sparse/malformed boundary records cannot pass silently.

For edit verification run `visual-only` with `mode: "visual-only-next"`, both `previous_original` and `previous_revised`, both `next_original` and `next_revised`, `reference_tags` (exact protected tag inventory), and ordered `parts` of `{kind: "locked"|"visual", original, revised}`. For review mode use `mode: "review-only"`; any changed full prompt fails. Capture the partition before editing and never widen it afterward to make a failed check pass.
