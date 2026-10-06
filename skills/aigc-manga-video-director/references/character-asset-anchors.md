# Character Asset Anchors

Use this reference when the user provides character images, character sheets, a script with recurring characters, or asks for style-consistent prompts across many storyboard shots.

The goal is to lock identity before writing shot prompts. A character anchor is not a long biography; it is a compact production contract for what must remain stable across images and video generations.

## When To Build Anchors

Build or update character anchors when:

- a new named character appears in a script or storyboard
- the user provides character reference images
- several shots reuse the same character
- face, hair, clothing, prop, pose, or expression continuity is important
- prior outputs show face drift, outfit drift, or inconsistent props

Do not force a full anchor table for a tiny one-off shot unless identity drift is likely.

## Anchor Fields

Use the smallest set that affects generation:

`角色锚点: @角色名`

`核心身份: [age/role/archetype/story function]`

`脸部不变项: [face shape, eye shape/color, brows, nose/mouth, skin tone, marks/scars]`

`发型不变项: [hair length, silhouette, bangs, tied/loose state, color, ornaments]`

`服装不变项: [main outfit silhouette, fabric/material, dominant colors, armor/jewelry/layering]`

`标志道具: [weapons, pendants, tools, divine marks, recurring props]`

`体态/动作习惯: [posture, gait, hand habits, fighting stance, gaze behavior]`

`表情范围: [default expression plus allowed emotional variations]`

`禁改项: [what must not change, such as hairstyle, eye color, outfit color, prop side, facial mark]`

For batches, compress anchors into `全局人物` and `全局稳定性`; do not repeat the entire anchor in every shot.

## Script Intake

When starting from a script:

1. Extract recurring characters and create provisional anchors.
2. Extract scene/time/atmosphere as `全局场景` candidates.
3. Mark each beat with emotion and story function.
4. Ask for character or scene images only when the missing reference would materially affect consistency.
5. Convert anchors into storyboard/prompt constraints after the shot plan is clear.

## Prompt Usage

Use anchors like this:

`全局人物: @杨戬 + [short identity and visual invariants]; @角色B + [short identity and visual invariants]`

`全局稳定性: keep each character's face shape, eye design, hair silhouette, outfit layers, key props, screen direction, and lighting direction consistent across all shots`

Inside each shot, write only deltas:

- temporary expression
- pose/action
- damage, dust, sweat, or lighting change
- prop state changes
- camera-specific crop risks such as hands, face profile, or hidden prop

## Continuity Audit

Before final prompts, check:

- whether every recurring character has a stable `@` name
- whether the same character changes face, hair, outfit, or prop without intent
- whether a shot-specific expression contradicts the allowed expression range
- whether a key prop switches side, disappears, floats, or changes shape
- whether character position, eye line, and screen direction still match adjacent shots

If a prompt may break identity, add the risk to `生成难点` or `稳定性` instead of adding a long repeated anchor.
