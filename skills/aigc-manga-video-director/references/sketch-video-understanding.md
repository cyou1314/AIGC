# Sketch Video Understanding

Use this reference when analyzing rough storyboard videos, sketch animatics, stick-figure videos, pencil sketches, simple line art, layout drafts, or low-detail shot plans.

## Core Principle

Treat the sketch as a director's intent map, not as finished image detail. The important information is usually:

- frame boundary and aspect ratio
- subject scale and placement
- horizon line and vanishing direction
- foreground/midground/background separation
- arrows, motion lines, smear shapes, and repeated poses
- occlusion and overlap
- camera height and tilt
- how subject size, crop, and screen position change over time

Do not penalize the input for missing face, clothing, lighting, or environment detail. Infer only what the sketch supports and mark uncertain parts as `推断` or `设计补充`.

## What To Read In Rough Drawings

### Perspective And Angle

Look for:

- horizon line: high horizon implies looking down; low horizon implies looking up.
- vertical convergence: strong convergence can indicate low-angle or high-angle distortion.
- floor/ceiling/wall guide lines: use them to infer camera tilt and lens feel.
- scale exaggeration: oversized foreground hand/head/weapon often implies wide-angle close camera.
- overlap: a foreground shape covering a character can imply depth and voyeuristic framing.
- tilted frame: diagonal ground or verticals can imply dutch angle or psychological instability.

### Camera Movement In Animatics

Separate three possibilities:

- **Camera move**: the whole composition shifts, scales, or rotates while subject drawing stays similar.
- **Subject move**: the subject pose/location changes while background frame stays stable.
- **Edit/reframe**: sudden change in crop, angle, or subject size without continuous transition.

Use evidence:

- whole frame enlarges: push-in, zoom-in, or digital crop.
- background guide lines slide with parallax: physical dolly/truck is more likely.
- frame pans across a large drawing: pan/tilt over storyboard art, not necessarily diegetic camera movement.
- subject grows while background relation stays similar: zoom/crop or subject walking toward camera.
- foreground shape crosses screen faster than background: tracking or depth parallax.

### Readability Over Detail

For each sketch shot, answer:

1. What is the intended focal object or person?
2. Where is the viewer placed?
3. Is the camera above, below, beside, behind, or inside the subject's viewpoint?
4. What moves: camera, subject, frame crop, or edit?
5. What is the emotional/directorial purpose of the unusual angle?
6. What must be preserved when turning it into finished AIGC visuals?

## Output For Sketch Videos

Use a confidence split:

`可确认: ...`

`推断: ...`

`设计补充: ...`

For difficult angles, add:

`角度拆解: horizon/camera height/tilt/lens/depth/foreground`

For motion, add:

`运动拆解: start frame -> movement path -> end frame`

## Prompt Conversion

When turning sketch video into AIGC prompts:

- preserve the original composition geometry before adding visual detail
- keep camera angle and subject scale from the sketch
- add environment, clothing, lighting, and style as controlled design layers
- do not let decorative detail change the intended camera language
- state whether the camera move is observed, inferred, or designed

## Hard Rule

If a sketch is ambiguous, provide 2-3 plausible interpretations and name what visual evidence would decide between them. Do not collapse uncertainty into one confident answer.
