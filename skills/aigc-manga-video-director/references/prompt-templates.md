# Prompt Templates

Use these templates when writing AIGC manga/drama video prompts. Prefer concrete camera instructions over generic labels. Do not output image prompts unless the user explicitly asks for image/still-frame/keyframe generation prompts.

Templates are reference structures, not mandatory forms. Select, merge, shorten, or expand them according to the specific task: source material, shot complexity, one-shot vs multi-shot structure, reference images, audio, target model, and whether the user needs analysis, a copyable prompt, or a production board. If the user provides a template, learn its useful ordering and constraints, then adapt it to the current shot instead of copying the layout mechanically.

Default video prompt target: Seedance 2.0 and Seedance 2.0 Fast. Read `seedance-prompting.md` when writing final prompts for these models.

Before final Seedance output, read `seedance-preflight-and-bilingual.md` and run a mental preflight: can the clip execute physically, preserve identity, follow one camera logic, and end on the intended frame? Revise before output when the answer is no.

Default final prompt output has two versions:

- `完整制作版`: detailed prompt using the current full structure.
- `精简版`: compressed prompt under 2000 Chinese characters per prompt.

Both versions should use medium density: enough detail to reproduce the shot, no repeated adjectives or unnecessary theory. Remove duplicate wording before removing time, image references, motion, camera path, composition, continuity, or avoid constraints.

For prompt batches, write shared character, scene, style, stability, and avoid rules once before the prompts:

`全局人物: @角色A, @角色B + identity, wardrobe, props`

`全局场景: @场景A + location geography, lighting direction, key props`

`全局风格: [shared style]`

`全局稳定性: [shared continuity]`

`全局避免: [shared negatives]`

Individual shot prompts should not repeat the same character/scene/style `@` names. Omit unified fields by default; do not write `参考图: 同全局参考图`, and do not include `风格` when it only means global style. Use `人物: 同全局人物`, `场景: 同全局场景`, `风格: 同全局风格`, or `稳定性: 同全局稳定性` only when the user asks for standalone per-shot prompt blocks.

When character consistency matters, build compact character anchors before the shot prompts. Use `references/character-asset-anchors.md` for the full anchor pattern. In the prompt itself, keep only useful invariants:

`全局人物: @角色A + face shape, eye design, hair silhouette, outfit layers, key prop, expression range; @角色B + ...`

`全局稳定性: keep face, hair silhouette, outfit, key props, eye line, screen direction, and lighting direction consistent; only allow shot-specific expression, pose, dirt, damage, or prop-state changes when stated`

Do not paste a full character dossier into every shot. Put the anchor once globally, then write per-shot changes such as expression, pose, injury, prop position, or crop risk.

## Global Style Prompt

`vertical manga-drama frame, cinematic comic realism, clean character design, expressive eyes, detailed clothing folds, controlled line art, rich but not noisy background detail, dramatic lighting, high contrast focal emphasis, coherent color script, production storyboard quality`

Adapt style to the user's target tool and aesthetic. Keep character identity and clothing consistent across all shots.

## Image Prompt Template

Use this section only when the user explicitly asks for image prompts, still-frame prompts, keyframe image prompts, or storyboard-board image-generation fields. Do not include image prompts by default.

`[character identity and appearance], [expression], [action], [location and time], [shot size], [camera angle], [composition geometry], [foreground/midground/background layers], [lighting direction and quality], [color palette], [mood], [manga/drama visual style], [key props], [quality constraints]`

Required details:

- character identity: age, face type, hairstyle, outfit, key prop
- action and expression: one main readable action, one emotional state
- shot size and angle: not just "cinematic shot"
- composition: subject placement, depth, negative space, attention path
- lighting/color: direction, contrast, color temperature, emotional color

## Video Prompt Template

`Start with [starting frame]. The camera [specific path] at [speed/easing], using [lens/depth feel]. [Subject] moves [subject action and direction]. Foreground [foreground motion], background [background motion/parallax]. Composition changes from [start composition] to [end composition]. Emotion shifts from [start emotion] to [end emotion]. End on [ending frame].`

Add duration if needed:

`Duration: 4-6 seconds.`

## Seedance Prompt Block

Use this compact block for each final Seedance shot:

`时间: [source video timecode/time range for 1:1 recreation]`

`参考图: [@图片名 / @图1 / @角色A when supplied and useful; @ mention uses name only, no file extension]`

`首帧: [subject, pose, composition, environment, lighting]`

`运动: [subject action + camera movement + foreground/background motion]`

`镜头: [shot size, angle, lens/depth feel, speed/easing]`

`尾帧: [ending composition and emotion]`

`风格: [manga-drama style, color, line/detail level]`

`English camera/style tags: [optional concise terms such as slow dolly in, locked-off camera, shallow depth of field, soft rim light, one continuous shot, no cuts; omit if not useful]`

`稳定性: [same face/outfit/props/location/lighting direction]`

`避免: [negative prompt]`

Do not include model or aspect ratio fields by default. Include source time/time range for 1:1 video recreation when available. Treat `时间` as original-video timing, not a Seedance parameter.

When the user provides images, insert each image where it belongs instead of listing images separately. The `@` mention uses only the image name without `.png/.jpg/.jpeg/.webp`; the field explains the role. Examples: `参考图: @角色A`, `首帧: @图1 + description`, `尾帧: @图2 + description`, `稳定性: keep identity consistent with @角色A`.

For the `精简版`, keep only the timecode, required `@` references, main action, camera path, composition change, ending frame, visual style, and continuity constraints. Remove repeated adjectives and secondary details first.

For the `完整制作版`, do not add extra fields just to look detailed. Keep practical fields and make each sentence carry a control point.

Use Chinese as the main prompt language for story, emotion, action, continuity, and dialogue. Add English camera/style tags only when they are shorter and clearer than Chinese, and keep them tied to concrete visual control. Do not add English adjective stacks such as `epic cinematic ultra detailed masterpiece`.

When a clip is meant to connect into the next shot, do not end the prompt with the subject fully stopping, posing, or settling unless the user asks for a held hero frame. Write the tail frame as continuing motion: the body weight is still transferring, fabric and hair still carry inertia, eyeline or walking direction leads into the next shot, and the camera keeps a small amount of movement instead of locking off.

## Camera Prompt Expansion

Weak:

`slow push-in close-up`

Strong:

`camera begins in a waist-up three-quarter view with the heroine placed on the left third, then slowly dollies forward and slightly downward over 5 seconds; the background corridor expands with subtle parallax, foreground curtain edge slides out of frame, depth of field tightens from both characters to her trembling eyes, ending in a tense close-up with the villain blurred behind her shoulder`

Before expanding a camera prompt, identify whether the source implies physical camera movement, zoom/crop, subject movement, edit/reframe, or mixed movement. Strong camera prompts should name the movement path, axis, speed/easing, start and end crop, foreground/background parallax, and focal-depth change.

Weak:

`pan to reveal the villain`

Strong:

`locked frame begins on the empty doorway and the heroine's shadow in the foreground; camera pans right at a controlled, suspenseful speed, following her eye line until the villain is revealed in the far background under a cold ceiling light; foreground wall edge briefly masks the reveal, ending with both characters separated by a vertical doorframe`

Weak:

`dramatic low angle`

Strong:

`low-angle medium shot from below the stair landing, the antagonist centered and towering over the frame, ceiling lines converging behind his head, warm light cutting across one side of his face, the protagonist's shoulder blurred in the lower foreground to show power imbalance`

## Negative Prompt Template

`inconsistent face, changed hairstyle, wrong outfit, extra fingers, distorted hands, unreadable eyes, broken anatomy, floating props, inconsistent lighting direction, random background, messy panel layout, overexposed face, blurry focal subject, text artifacts, watermark`

## Continuity Notes

For each shot, include continuity constraints:

- same face, hairstyle, outfit, body type
- same key prop position
- same location geography
- consistent eye line and screen direction
- lighting direction remains believable
- emotion progresses from previous shot

If the character anchor is incomplete, flag it before final output instead of hiding the risk inside generic negatives.
