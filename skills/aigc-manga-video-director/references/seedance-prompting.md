# Seedance 2.0 Prompting

Use this reference when writing prompts for Seedance 2.0 or Seedance 2.0 Fast.

For deeper Seedance 2 directing behavior, also read `seedance-2-director-rules.md`. Use this file for the stable shot-block format and prompt field conventions; use `seedance-2-director-rules.md` for mode selection, `@` reference role maps, first/last-frame bridges, V2V/R2V/edit/extend workflows, timeline prompting, audio/dialogue/rhythm, character blocking, compression, and retake troubleshooting.

## Model Assumptions

Seedance 2.0 supports multimodal audio-video generation with text, image, audio, and video inputs. It is designed for control over performance, lighting, shadow, and camera movement. Public technical material describes 4-15 second outputs and mentions the Fast version as the low-latency accelerated variant.

For this user's workflow, default to image-to-video or reference-driven prompts when a sketch frame, storyboard frame, or extracted keyframe is available.

## 2.0 vs 2.0 Fast

- **Seedance 2.0**: use for important shots, complex camera movement, difficult angles, multi-subject blocking, emotional beats, and shots where visual quality matters most.
- **Seedance 2.0 Fast**: use for iteration, simple single-action shots, rough timing tests, alternate camera trials, and prompt debugging.

For Fast, simplify the prompt. Use one main action, one camera move, one emotional change. Avoid stacking several reveals, turns, gestures, and lens changes in one clip.

## Prompt Structure

Write prompts in this order:

1. **First frame**: subject, pose, camera angle, composition, environment, lighting.
2. **Subject motion**: exactly what the character/body/object does.
3. **Camera motion**: path, direction, speed, easing, and whether the movement is push, pull, pan, tilt, orbit, tracking, handheld, or locked.
4. **Scene motion**: foreground/background movement, parallax, cloth, hair, smoke, rain, light flicker.
5. **Ending frame**: final crop, emotion, subject scale, and composition.
6. **Style and continuity**: manga-drama look, character consistency, clothing, props, location.
7. **Avoid**: deformations, identity drift, excessive camera shake, random background changes.

## Seedance Shot Template

Use this for each shot:

`时间: [source video timecode or time range, e.g. 00:12.4-00:16.8].`

`参考图: [@image-name / @图1 / @角色A references when supplied and relevant; use only the image name after @, without file extension].`

`首帧: [clear key frame description].`

`动作: [single readable subject action].`

`镜头: [specific camera path, speed, focal/depth feel].`

`场景运动: [foreground/background/parallax/environment motion].`

`尾帧: [ending frame and emotional state].`

`风格: [AIGC manga drama style, lighting, color, finish level].`

`稳定性: keep the same face, hairstyle, outfit, prop, location geography, screen direction, and lighting direction.`

`避免: inconsistent face, warped hands, changed outfit, random background, uncontrolled zoom, excessive shake, flicker, text artifacts, watermark.`

Do not output separate model or aspect-ratio fields by default. Include source time/timecode when the task is 1:1 video recreation. Treat `时间` as the original video's timing reference, not a Seedance parameter.

## Prompt Version Rule

When outputting final Seedance prompts, provide two versions by default:

- `完整制作版`: full detailed prompt using the standard fields.
- `精简版`: compressed prompt under 2000 Chinese characters per prompt.

The concise version must preserve source timecode, useful `@` references, main subject action, camera path, composition change, ending frame, style, and stability constraints. Remove redundant adjectives, repeated continuity notes, and secondary environmental details first.

Use medium density in both versions: the full version should be complete but not bloated, and the concise version should be shorter but not shallow. Prefer one clear sentence per control point. Delete repeated global style/reference text, duplicate negatives, and stacked adjectives before deleting motion, composition, continuity, or risk controls.

## Style Once Rule

For a batch of Seedance prompts, write shared character, scene, style, stability, and avoid rules once at the beginning:

`全局人物: @角色A, @角色B + identity, wardrobe, props.`

`全局场景: @场景A + location geography, lighting direction, key props.`

`全局风格: [shared manga-drama style, line quality, lighting logic, color palette, finish level].`

`全局稳定性: [shared face, hair, outfit, props, screen direction, lighting direction].`

`全局避免: [shared negative constraints].`

Do not repeat the same character, scene, or style `@` names inside every shot. Do not write `参考图: 同全局参考图`. Omit `风格` in individual shot prompts when it is simply the global style. Use `人物: 同全局人物`, `场景: 同全局场景`, `风格: 同全局风格`, or `稳定性: 同全局稳定性` only when the user asks for standalone per-shot prompt blocks. Add shot-specific notes only when the shot changes character state, location detail, lighting, color, texture, or finish.

## Deep But Efficient Rule

Do not make prompts shallow to save quota. Preserve the deep read of important shots: timecode, useful `@` references, first frame, subject action, camera path, scene motion, end frame, continuity, and reproduction risks. Save quota by using `全局人物`, `全局场景`, `全局风格`, `全局稳定性`, and `全局避免` once, and by removing repeated adjectives or duplicate continuity text.

Medium-density prompt checklist: keep `时间`, needed `@` names, `首帧`, main action or `运动`, `镜头`, scene/parallax movement when relevant, `尾帧`, shot-specific stability, and avoid constraints. Omit `参考图: 同全局参考图`, repeated `风格`, and any explanation that does not help Seedance reproduce the shot.

## Image Reference Rule

- When the user provides images, place each image in the field that uses it, but write the mention as `@图片名` only.
- Use `参考图` for shared character, scene, style, or composition references.
- Use `首帧` for a start-frame image reference and `尾帧` for an end-frame image reference.
- Use clear image names such as `@图1`, `@图2`, `@角色A`, or the real uploaded image name when available.
- Do not put position, coordinates, file path, file extension such as `.png`/`.jpg`, or role/location words inside the `@` mention. Write the role in the field name or surrounding text instead.
- Do not attach every supplied image to every prompt. Only include images that help the shot being written.

## Timecode Rule

- Use exact source time range when available, e.g. `时间: 00:12.4-00:16.8`.
- If exact time is unknown, use shot ID plus approximate time, e.g. `时间: S03 / 约00:12-00:16`.
- If no source video timing exists, omit `时间` rather than inventing it.
- When revising prompts, preserve or add the best available source time in the complete final prompt block.

## Prompt Revision Rule

When revising an existing prompt, always return the complete final prompt block. Do not provide only the changed sentence, partial paragraph, or patch-style edits.

Even if only one field changes, rewrite the full copyable prompt. Return both `完整制作版` and `精简版` unless the user asks for one version only:

`时间: ...`

`参考图: ...`

`首帧: ...`

`动作: ...`

`镜头: ...`

`场景运动: ...`

`尾帧: ...`

`风格: ...`

`稳定性: ...`

`避免: ...`

If the original prompt uses the compact block with `运动` instead of separate `动作` and `场景运动`, preserve that structure but still return the complete final block.

## Motion Rules

- Keep one clear movement per prompt.
- Use a slightly longer motion description when the camera move and subject action both matter.
- Use multi-beat motion only when the shot has a start, development, and ending beat.
- Do not put more than one major camera move in a Fast prompt.
- Before naming a camera move, decide whether the image change comes from physical camera movement, zoom/crop, subject movement, edit/reframe, or mixed movement.
- Describe camera movement with start framing, end framing, path/axis, speed/easing, parallax or foreground/background evidence, and focal-depth change.
- For difficult sketch angles, preserve the sketch's camera height, tilt, and subject scale before adding visual detail.
- When using a start/end frame workflow, make the text describe the bridge between the frames, not a new unrelated scene.

## Good Seedance Prompt Example

`时间: 00:12.4-00:16.8`

`参考图: @角色A, @楼梯间`

`首帧: vertical 9:16 manga-drama frame, the heroine is seen from a low-angle three-quarter view at the bottom of a stairwell, her face half hidden by the foreground railing, cold blue light from above, the antagonist's shadow falls across the wall behind her.`

`动作: she slowly raises her eyes from the floor toward the unseen antagonist, fingers tightening around the phone.`

`镜头: camera performs a slow dolly-in with a slight upward tilt over 5 seconds, changing from medium shot to tense close-up, shallow depth of field tightening on her eyes.`

`场景运动: foreground railing slides downward across the frame, background stair lines stretch with subtle parallax, dust particles drift in the cold light.`

`尾帧: end on a close-up of her frightened but determined eyes, the antagonist's shadow still visible behind her.`

`风格: cinematic manga drama, clean line art, realistic lighting, cool blue shadows, high contrast, controlled detail.`

`稳定性: same face, hairstyle, school uniform, phone, stairwell geography, lighting direction.`

`避免: changed face, extra fingers, distorted phone, random stair layout, excessive shake, overexposure, text artifacts, watermark.`

## Bad Prompt Pattern

Avoid:

`A girl is scared, cinematic, camera moves, anime style, very detailed.`

Reason: no first frame, no ending frame, no camera path, no subject motion, no continuity constraints.
