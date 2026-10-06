# Storyboard Format

Use this format for AIGC manga/drama storyboard planning.

## Required Columns

When the user supplies images, add a `参考图` column near the front of the table and place `@图片名` references at the shot where they apply. Strip file extensions like `.png/.jpg/.jpeg/.webp`. Do not repeat global character/scene/style references in every shot; mention them once in the global block. Do not put image position, coordinates, or file path inside the `@` mention.

`镜头 | 时长 | 画面描述 | 角色动作 | 表情 | 台词/旁白 | 景别 | 机位 | 镜头运动 | 构图 | 光影色彩 | 情绪功能 | 视频提示词 | 连贯性备注`

## Shot Description Rules

- Write the visual image first, then the emotion.
- Keep one primary action per shot.
- Make the camera readable to a generation model.
- Preserve screen direction and eye line across adjacent shots.
- Use close-ups for decisions, clues, and emotional rupture.
- Use wider shots when spatial relationship matters.

## Beat Expansion

When turning a script beat into shots:

1. Establish location and relationship.
2. Show the pressure source.
3. Cut to reaction.
4. Reveal clue or emotional change.
5. End on a visual hook.

## Fight Choreography And Rhythm

- Do not divide a fixed runtime into equal shot durations by default. Let anticipation, fast exchanges, impact inserts, spell release, and aftermath take different amounts of screen time. Treat storyboard time as edit timing; source generation clips can be longer and trimmed.
- Before camera prompts, lock the action chain: starting stance and attack line → defense/dodge and contact point → counter → opponent/environment reaction → recovery position. Name the weapon path, body/footwork, target, screen direction, and end pose for each move. Keep the geography and weapon hand consistent across cuts.
- For magic, specify its visible trigger, where energy comes from, how the body/weapon releases it, its travel path, how the opponent blocks or evades it, and the resulting change to the body or environment. Reuse one stable visual rule for smaller spells; reserve a clear, staged build/release/travel/impact/aftermath for the finisher.
- Use slow motion selectively for a key contact, charge, or decision. A full-frame effect should preserve the attack direction and enough silhouette to read the move, then clear to show impact and recovery. Do not replace choreography with flashes, particles, or camera shake.
- For a complex climax, split generation into anticipation, release, and impact/aftermath units and cut them together, rather than asking one short clip to perform several actions and effects at once.

## AIGC Production Notes

Add notes for:

- character consistency
- prop continuity
- location geography
- costume continuity
- lighting direction
- whether an image prompt is explicitly requested; otherwise write only the video prompt
