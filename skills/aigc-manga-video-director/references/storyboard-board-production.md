# Storyboard Board Production

Use this reference when creating a storyboard board for AIGC manga/drama production.

## Board Purpose

A storyboard board must guide production, not just describe a scene. It should make the visual decision for every shot clear enough for drawing, image generation, video generation, editing, or team review.

## Board Units

Each panel should contain:

- shot ID
- duration
- aspect ratio or panel shape
- key frame image or image placeholder
- user-provided image references placed as `@图片名` links in the relevant panel or prompt field, with no position/path/file-extension inside the mention
- screen action
- dialogue or narration
- camera language
- composition note
- lighting and color note
- image prompt only if explicitly requested
- video prompt
- continuity note

## Layout Choices

Choose layout based on use:

- **Vertical short drama**: 9:16 panels, 2 columns for review, strong face/action readability.
- **Manga page**: variable panels, rhythm controlled by panel size and reading path.
- **Production board**: regular grid, one shot per card, dense notes for generation.
- **Pitch board**: larger images, fewer notes, strongest visual beats only.

Default to production board unless the user asks for a polished pitch board.

## Panel Design Rules

- Use one main readable action per panel.
- Make the emotional focus visible in the first second of reading.
- Keep screen direction consistent across consecutive panels.
- Keep every panel aspect ratio within `long side / short side <= 2.5`. Do not use extremely narrow or extremely wide panels such as `1:3`, `3:1`, `9:24`, or `24:9`.
- Prefer practical ratios such as `9:16`, `16:9`, `1:1`, `4:5`, `3:4`, `2:3`, `3:2`, `2.35:1`, and `1:2.5`.
- Use close-up panels for decisions, clues, facial rupture, hand detail, or object reveal.
- Use wide panels when location, distance, power relationship, or movement path matters.
- Mark panels that require AI image generation, video generation, Photoshop cleanup, or manual drawing.

## Board Output Format

Use this table for text-first boards:

When images are supplied, add `参考图` after `镜头` and put shot-specific `@图片名` references there.

`镜头 | 画幅 | 时长 | 分镜画面 | 角色动作 | 台词/旁白 | 镜头语言 | 构图/调度 | 光影色彩 | 生图提示词 | 视频提示词 | 连贯性备注 | 制作备注`

For a visual board, create or request a CSV with these columns:

If reference images are separate from the board thumbnail, add `reference_image` after `shot` and place `@图片名` references in that column.

`shot,image,ratio,duration,visual,action,dialogue,camera,composition,lighting,image_prompt,video_prompt,continuity,production_note`

Then use `scripts/make_storyboard_board.py` to make an HTML review board.

## AIGC Continuity

Always track:

- same character face and hairstyle
- same outfit and props
- same location geography
- eye line and screen direction
- lighting direction
- emotional progression
- which shots need the same seed/reference image

## Quality Check

Before finishing, verify:

- the board can be followed without reading the original script
- no panel aspect ratio exceeds `2.5:1` or `1:2.5`
- each panel has a unique visual job
- prompts match the panel composition
- notes explain what must stay consistent
- no panel is just a vague mood description
