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

## 公司写实短剧时间线模板（按任务选用）

用户提供的公司模板可作为写实真人短剧的输出结构参考。适用于用户要求公司格式、真人影视质感或带对白的表演型时间线提示词。保留其他项目的既定风格，不自动用于动画、产品、无对白或其他类型任务。

### 方案优先于模板

用户提供此公司格式用于学习，不要求固定照搬。优先选择当前剧情、情绪、素材和生成条件下最合适的方案，以叙事清楚、表演可读、镜头衔接、动作可实现和提示词可执行为判断依据；不宣称未经生成验证的方案具有客观最优效果。模板的字段、排列、景别、镜头数量、运镜、风格与声音配置均可取舍。只有用户在当前任务明确要求沿用公司格式或指定约束时才锁定对应项；不得仅因曾见过示例就自动启用它的美式英语、9:16、写实影调或禁配乐要求。吸收有用控制逻辑，舍弃重复、冲突或不适合本场的写法。

### 可复用结构

按下列顺序组织，缺失但不影响创作的字段可省略，不机械填满：

```text
全局视听与表演：[写实程度、影调、构图、景深、节奏、对白语言/口音、字幕/配乐策略]
场景：[已提供的场景参考及日夜状态]
角色：[已提供的角色参考及本场服装]
道具：[已提供的道具参考；锁定数量和归属]
视觉锚点：[角色辨识、关键接触部位、情节道具与空间边界]
站位与轴线：[画面左右、前中后景、面朝方向、视线对象和移动路径]
环境状态：[光源方向、软硬程度、色温（有依据时）、材质、环境及动作音效]
画面：
起止时间：【景别｜机位/角度｜具体运镜】起始状态；主体动作与接触/后果；构图或焦点变化；角色【可见表演、声线、语速】：“精确台词”；台词起止（规划/实录依据）；听者反应；尾帧及切镜接口。
时长：[成片目标；生成单元另外规划]
连续性与负面约束：[身份/服装/道具/轴线/视线/物理连续性；当前项目禁止项]
```

模板字段中的素材引用只能使用当前实际提供的裸名 `@名称`，全局引用一次，镜头中直接使用角色短名。用户文本中列出名称但没有附件时，可以保留其命名，不宣称已检查参考图或建立真实素材绑定。不把示例中的角色、场景、道具写成通用默认项。

### 表演与声音

- 以呼吸、停顿、眼神、下颌、手部和重心变化描述表演，并为每个节拍选择少量最有因果作用的变化。不在一句对白上堆叠所有微表情或相互冲突的激烈/克制指令。
- 每句对白明确说话人、精确原文、开口和收尾时间、声音意图、正常语速及必要气口；明确关键听者反应发生在台词下还是台词后。无音频时标记时间为估算，不假称实录验证。
- 美式英语、禁止中文、禁止字幕、无背景音乐、只保留环境与动作音效，是这类公司项目可选预设，不是所有任务默认。区分提示词说明语言与生成视频内的对白/可见文字语言；项目要求英文时不得把中文台词写进生成内容。
- 仅在当前任务启用禁配乐时移除音乐，改用具体脚步、衣料、呼吸、器物、空间回声等组织声音节奏。

### 优化与交付前检查

- 将“电影质感/Netflix影调”等效果词转化为本场可执行的主辅光关系、对比、肤色、材质与构图，避免把一个品牌当作唯一、固定的影调。硬光不等于面部过曝，浅景深不能破坏多人站位或接触动作的可读性。
- 时间线完整覆盖目标时长，不留无人说明的空档。片尾余量明确用于反应、动作后果或下一镜接口，不平均分配镜头。生成平台限制与成片时长分开检查，不保证任意平台可一次生成24/30秒。
- 应用 `shot-language.md` 的相邻镜头检查。正反打先锁定轴线与屏幕视线；“特写转中景”须说明是连续后拉还是切镜；“侧移抓拍”须写明路径、速度与终点，不能只写名称。
- 前后核对道具数量、胸针/徽章等物件区别、持握到佩戴的状态转换，以及衣料褶皱/损伤。不得擅自解决影响剧情的道具矛盾，需要时指出待确认处。
- 区分材质形变与接触压痕：硬质框柱保持刚性，受压衣料及软组织产生合理褶皱/压痕；动作可见但不要求材质穿透。人体能否进入/退出由空间、姿态和碰撞条件支持。
- 方位描述同时落到画面站位，不只写东南西北。没有高低落差时，“居高临下”作为表情/姿态或机位效果表达，不凭空增加台阶和高度。
- 围观人群、镜面/屏幕倒影保持低复杂度；若反射中必须呈现关键信息，明确主体、角度与内容，避免无数独立变形影像抢占焦点或破坏连续性。
- 重复的字幕、文字、水印、logo禁令可合并为清楚的一处约束。保持完整提示词可复制，不添加无关制作理论。
