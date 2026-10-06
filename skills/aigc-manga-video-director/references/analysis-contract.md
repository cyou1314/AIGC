# Analysis Contract

Use this contract to keep video analysis and prompts from becoming shallow.

## Required Per-Shot Thinking

For each important shot, produce these six parts:

1. `画面证据`: visible facts from the frame or frame sequence.
2. `运动判断`: camera movement, subject movement, zoom/crop, edit/reframe, or mixed movement, with evidence.
3. `构图判断`: geometry, depth layers, attention path, power relationship.
4. `叙事功能`: what information or emotion the shot adds.
5. `复刻策略`: what must be controlled for AIGC recreation.
6. `提示词`: video prompt by default. Add image prompt only when the user explicitly asks for it.

Do not write only "近景, 推镜, 三分法". Expand each label into visible evidence and production instruction.

Keep analysis medium-density: do not turn every shot into long theory, but do not remove evidence. For important shots, concise wording must still include motion type, evidence, composition logic, reproduction strategy, and generation risks.

For camera movement, include:

- `运动类型`: physical camera / zoom or crop / subject movement / edit or reframe / mixed movement
- `运动拆解`: start framing -> path/axis -> speed/easing -> end framing
- `证据链`: parallax, subject scale, foreground occlusion, background reveal, frame edge, horizon/vanishing lines, motion blur, focal-depth change
- `复刻控制`: camera height, focal/depth feel, foreground mask, screen direction, parallax layer, end composition

## Minimum Prompt Detail

Every video prompt must mention:

- start frame
- end frame
- camera path
- movement speed or easing
- lens/depth feel
- subject movement
- foreground/background movement or stillness
- composition change
- emotional change

If any item is not visible in the source, mark it as `设计补充` instead of pretending it was observed.

When shortening analysis, remove repeated wording first. Do not remove start/end framing, camera path, evidence chain, composition change, continuity, or avoid constraints.

## Evidence Language

Use phrases like:

- `画面证据显示...`
- `从前景遮挡变化判断...`
- `背景视差说明...`
- `主体大小变化但背景关系不变, 更像变焦或裁切...`
- `此处是设计补充, 原视频无法确认...`

## Output Shape

For deep analysis, use:

`镜头 | 时间段 | 关键帧 | 画面证据 | 运动判断 | 构图判断 | 叙事功能 | 复刻策略`

Then add:

`画面提示词: ...`

`视频提示词: ...`

`负面提示词: ...`

`连续性备注: ...`
