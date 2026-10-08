# Shot Language Reference

Use this reference for precise camera, composition, and motion language in AIGC manga/drama analysis.

## 景别

- 大远景: environment dominates; use for scale, isolation, city pressure, battlefield, destiny, or arrival.
- 远景: full subject in environment; use for spatial relation and loneliness.
- 全景: full body action; use for walking, fighting, entering, falling, or body-language beats.
- 中全景: knees-up; use for confrontation, gesture, and relationship distance.
- 中景: waist-up; use for dialogue and readable expression plus body language.
- 中近景: chest-up; use for emotional pressure and intimate dialogue.
- 近景: face or hands dominate; use for reaction, decision, fear, tears, clue, or hesitation.
- 特写: eyes, mouth, object, wound, phone, letter, weapon; use for turning points and memory hooks.
- 极特写: one detail fills frame; use sparingly for shock, clue reveal, or psychological intensity.

## 机位和角度

- 平视: neutral alignment, realistic dialogue, audience beside the character.
- 低角度: dominance, threat, heroic pressure, worship, intimidation.
- 高角度: vulnerability, surveillance, weakness, shame, fate pressure.
- 俯拍: layout, isolation, ritual order, powerlessness, tactical geography.
- 仰拍: grandeur, oppression, revelation, authority.
- 过肩: relationship, confrontation, withheld information, reaction tension.
- 侧面: emotional distance, parallel conflict, silent stalemate.
- 背影: secrecy, departure, loneliness, unresolved intent.
- 主观镜头: immersion, fear, memory, discovery, unreliable perception.

## 镜头运动

Name camera movement only when visible or intentionally designed. Add path, speed, and effect.

Before naming the move, decide what causes the frame change:

- camera movement: foreground/background parallax or perspective changes
- zoom/crop: frame tightens without meaningful parallax
- subject movement: subject scale/position changes while environment stays stable
- edit/reframe: composition jumps without continuous motion
- mixed movement: camera and subject move together, or camera move plus zoom/crop

For strong production notes, describe: start framing, end framing, movement axis, path, speed/easing, pivot or anchor point, parallax layer, foreground mask, focal-depth change, and emotional effect.

- 推镜/dolly in: camera physically moves closer; background parallax changes. Use for pressure, intimacy, clue emphasis, decision.
- 变焦推近/zoom in: frame tightens without parallax. Use for psychological pressure, melodrama, sudden realization.
- 拉镜/dolly out: camera moves away. Use for consequence, loneliness, reveal of surrounding danger.
- 横移/truck: camera slides left or right. Use to reveal hidden subject, track parallel movement, create unease.
- 跟拍/tracking: camera maintains distance with moving subject. Use for pursuit, urgency, daily-life flow.
- 摇镜/pan: camera pivots horizontally. Use to search, reveal, connect two subjects, or create reaction chain.
- 俯仰/tilt: camera pivots vertically. Use to reveal height, authority, body-to-face emotion, or object-to-owner relation.
- 升降/pedestal or crane: camera rises/falls. Use for status change, reveal, collapse, scale.
- 环绕/orbit: camera circles subject. Use for romance, suspicion, vertigo, decisive transformation.
- 手持/handheld: unstable frame. Use for panic, immediacy, documentary realism, loss of control.
- 静止镜头/locked-off: no camera movement. Use for ritual, suspense, emotional weight, oppressive stillness.

## 构图

Describe composition as geometry plus attention path.

- 三分法: subject on vertical third; readable and balanced.
- 中心构图: iconic, direct, ritual, confrontation.
- 对称构图: order, control, ceremony, artificial calm.
- 框中框: confinement, secrecy, observation, memory.
- 前景遮挡: spying, intimacy, danger, depth.
- 留白: loneliness, threat, emotional distance, waiting.
- 引导线: corridors, roads, light beams, rails guide the eye.
- 景深分层: foreground/midground/background carry separate information.
- 倾斜构图: unease, chaos, psychological collapse.
- 压迫式构图: ceiling, wall, crowd, or negative space squeezes the subject.
- 反差构图: bright/dark, large/small, crowded/isolated, warm/cold conflict.

## 漫剧常用情绪功能

- 建立关系: show who controls space and who reacts.
- 强化压迫: make subject smaller, blocked, lower, or trapped by foreground.
- 揭示秘密: move from obstruction to clue, or from character to object.
- 情绪爆点: tighten from body language to face/eyes/hands.
- 节奏缓冲: locked-off or wider shot after intense close-ups.
- 反转: reframe so background information becomes foreground meaning.

## 相邻镜头与剪辑节奏检查

适用于剧本转分镜、多镜头视频提示词和镜头方案修改；单镜头不强制安排切镜。

- 先确定每次切镜带来的新信息、动作阶段、视线关系或情绪变化，再选择景别与机位。不能只改变景别名称而不改变实际画面。
- 逐对检查相邻镜头的主体、景别/主体画面占比、机位夹角、构图、视线、运动方向和运镜方式。避免同一主体在相近景别、相近角度、相似构图之间无意跳切。
- 相同主体、相近景别的机位切换，可参考30度原则；它是经验指导，不是硬性数值，也不替代180度轴线、视线和动作连续性检查。
- 景别差异不足时，优先考虑有叙事理由的角度变化、明确的景别变化、动作匹配或线索/反应插入。切换到不同主体即使景别相同也可成立；不得机械要求每镜头改变景别或强制隔级切换。
- 连续同类景别、固定机位或重复推镜必须有明确目的，例如对话关系、压迫、重复喜剧或有意跳切。无目的的重复应调整；不为追求变化添加无关镜头。
- 根据地理关系和叙事信息安排远景/全景、动作景别与细节/反应镜头。不得默认用连续近景代替环境建立，也不得设置固定景别比例。
- 根据可读动作、对白、反应与后果分配长短镜头，禁止平均分摊总时长或套用统一镜头长度。生成单元时长与剪辑镜头时长分开规划；无实录音频或已确认分镜时，精确时间仅标作规划/估算。
- 交付前内部完成相邻镜头检查；发现无意重复或跳切先修改提示词。只在关键选择或未解决风险需要用户判断时简短解释，不默认输出完整检查表。
