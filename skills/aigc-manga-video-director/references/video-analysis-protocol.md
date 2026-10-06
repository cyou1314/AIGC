# Video Analysis Protocol

Use this protocol when the user asks for deeper video understanding.

## Observe Before Naming

Do not name a camera move first. First compare what changes:

- subject size changes: possible dolly, zoom, or subject movement
- background parallax changes: physical camera movement is likely
- background does not shift while subject enlarges: zoom or crop is likely
- foreground crosses frame: tracking, dolly, or subject passing foreground
- horizon tilts or frame shakes: handheld, dutch angle, impact, instability
- eye line changes: reaction, reveal, or power shift

Then name the camera movement and explain the evidence.

Classify the movement before writing prompts:

- physical camera movement: parallax, foreground/background relationship, horizon or vanishing-line shift
- zoom/crop: subject scale changes while background relationship stays mostly fixed
- subject movement: subject changes size or position while frame and background remain stable
- edit/reframe: sudden discontinuity, jump in composition, or no continuous motion bridge
- mixed movement: camera, subject, and/or zoom happen together; separate each layer

## Shot Analysis Checklist

For each shot, answer:

1. What is the first readable frame?
2. What is the last readable frame?
3. What changes between them?
4. Which object or face attracts attention first?
5. What does the foreground hide or reveal?
6. How does the background add story information?
7. Does the camera move, subject move, or both?
8. Is the movement smooth, sudden, handheld, mechanical, or eased?
9. What is the movement axis and anchor: push/pull, lateral, vertical, pivot, orbit, diagonal, or handheld drift?
10. What evidence supports the movement: parallax, foreground occlusion, background reveal, frame edge, horizon, vanishing lines, motion blur, focal-depth change?
11. What emotion does the shot create?
12. What must be preserved in an AI-generated remake?

## Camera Movement Evidence

Use this format:

`运动判断: [camera/subject/both]`

`证据: [size change, parallax, foreground shift, background reveal, horizon change, motion blur, screen direction]`

`运动拆解: [start framing -> path/axis -> speed/easing -> end framing]`

`复刻控制: [camera height, focal/depth feel, parallax layer, foreground mask, screen direction]`

`效果: [pressure, reveal, intimacy, threat, loss of control, rhythm]`

## Deep Composition Analysis

Analyze:

- frame geometry: thirds, center, symmetry, diagonal, frame-in-frame
- subject weight: left/right/top/bottom, large/small, isolated/crowded
- depth: foreground, midground, background
- attention path: where the eye enters, where it lands, where it exits
- negative space: what empty area implies
- occlusion: what is hidden and why
- screen direction: left-to-right/right-to-left movement or gaze
- power relationship: high/low, near/far, dominant/subordinate placement

## Strong Output Pattern

For important shots, use:

`观察: ...`

`运动判断: ...`

`构图判断: ...`

`情绪功能: ...`

`复刻策略: ...`

This keeps the analysis from collapsing into short labels.
