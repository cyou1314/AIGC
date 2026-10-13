# Recovered historical reference

Recovered and adapted on 2026-10-13 from the user's Drive. Historical host-specific prescriptions and fixed ratios do not override the current SKILL.md, current user request or available tools. Do not treat cited provider/model or output-quality claims as current verification.

# Reference control

Use this reference for edits, identity preservation, multi-reference generation, or any request that says “以这张图为主”, “只改一个地方”, “保持不变”, or “不要跑偏”.

## Role assignment

| Role | Lock | Do not borrow automatically |
|---|---|---|
| identity | face, hair, body proportions, wardrobe, signature marks | another reference's face or costume |
| pose/action | body orientation, gesture, contact, expression | a prettier but different pose |
| composition | framing, subject scale, camera side, negative space | a different crop or lens language |
| environment | architecture, terrain, set dressing, spatial anchors | unrelated props or palette |
| lighting | source direction, softness, contrast, color relationship | a neighboring shot's light |
| material/style | rendering medium, surface response, line or paint behavior | extra stylization not requested |
| edit target | the one region allowed to change | global restyling |

## Invariant protocol

For an edit or localized repair, explicitly write:

```text
CHANGE ONLY: <requested region or property>
KEEP UNCHANGED: <identity, pose, camera, composition, lighting, background, atmosphere, atmospheric perspective, and any other invariants>
DO NOT REINTERPRET: <reference role or named detail>
```

Repeat the invariant in every revision pass. A shorter second prompt is not safer if it drops the constraints that prevent drift.

When removing an object or region, define the replacement surface and continuity instead of leaving a visual hole:

```text
REMOVE: <the unwanted object or mark>.
REPLACE WITH: <the wall, floor, skin, fabric, hair, sky, reflection, or background structure that continues through the vacated area>.
LOCAL MATCH: preserve surrounding perspective, material pattern, edge softness, exposure, shadow, reflection, and occlusion.
```

Use one high-risk local change per pass by default. Changes may be bundled when they affect the same region and share the same geometry, light, and preservation contract; separate unrelated regions or changes likely to repaint the whole frame. This keeps revision cost practical without sacrificing the last good baseline.

For localized image edits, include tonal invariants unless the user explicitly requests a new lighting treatment:

```text
KEEP UNCHANGED: original exposure, overall brightness, midtone visibility, black level, white level, contrast, color temperature, saturation, light direction, shadow detail, highlight roll-off, atmosphere, atmospheric perspective, and subject/background brightness relationship.
LOCAL MATCH: the edited region must match surrounding exposure, color, contrast, edge softness, and light direction.
```

This prevents a local edit from being interpreted as a global darker grade. If the original image's lighting or exposure cannot be judged because the reference is unavailable, do not claim that it has been preserved; state the limitation or ask for the source image.

## Conflict resolution

1. Current user correction outranks inherited prompt language.
2. A supplied image outranks a vague prose description for appearance, palette, lighting, and set details.
3. If two references conflict, assign one as the primary identity/composition source and use the other only for its named role.
4. If the role is unclear and the conflict changes the result, ask one question; do not blend incompatible references by guesswork.

## Multi-reference sentence

Use explicit indexed roles rather than “combine these images”:

```text
参考图1仅用于人物身份与服装；参考图2仅用于场景建筑和构图；参考图3仅用于光线方向与色彩关系。不得把参考图3的主体、道具或背景带入画面。
```

## Public example or social-post reference

When the user brings a creator-shared image, gallery post, or screenshot as inspiration, assign only the requested roles:

```text
参考图仅用于：<构图 / 光线 / 色彩 / 材质 / 媒介之一或数项>。
主体身份、故事内容、文字、水印和作者签名风格不自动继承。
```

Extract high-level visual decisions—shape, value, light direction, palette, edge behavior, and texture scale. Do not copy an exact prompt, watermark, living creator's signature style, or unsupported model parameters. If the post contains a result but no editable source, treat it as a style/composition study rather than proof that a prompt will reproduce the same image.

## Sequence continuity lock

When a reference will be reused across shots, boards, or revisions, lock the interfaces that cause visual drift:

```text
LOCK: camera side, screen direction, 180-degree line, eyeline, horizon/axis, subject stance and identity, key-light side, palette relationship, lens progression, major background anchors, entry/exit direction, and prop state.
CHANGE ONLY: the requested beat, pose, expression, environment change, or local edit.
DO NOT REINTERPRET: the locked reference roles or the causal direction of the action.
```

If a deliberate transition is requested, name the transition rather than silently changing it: `time-of-day change`, `camera-side change`, `impact aftermath`, or `palette transition`. A visually attractive frame that breaks the previous camera axis, light direction, or prop state is not a reliable continuation frame.
