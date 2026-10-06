# Fast Video Workflow

Use this reference when video analysis feels slow or the input video is longer than a few seconds.

## Principle

Do not begin with exhaustive frame extraction. Start with a cheap visual index, then spend attention deeply on useful moments. This workflow saves quota by choosing frames better, not by making the analysis shallow.

## Pass 1: Visual Index

Create:

- 8-16 representative frames for short clips
- 16-32 representative frames for longer clips
- a contact sheet
- a timestamp manifest

Use low resolution first, usually width 512-768 px. High resolution is only needed for faces, hands, props, text, and composition-critical frames.

## Pass 2: Shot Map

From the contact sheet, identify:

- scene or location changes
- action peaks
- emotional reaction beats
- camera movement candidates
- composition changes
- key props or clues

Output a quick shot map before deep analysis:

`shot | time range | why it matters | needs deep read?`

## Pass 3: Targeted Deep Read

Only deepen frames that matter:

- start/mid/end frames of a camera move
- before/after reveal
- reaction close-up
- composition shift
- prop/clue close-up

For each selected shot, inspect 2-4 frames, not dozens.

Selected shots still require deep reading: movement evidence, start/end framing, path/axis, speed/easing, composition geometry, blocking, foreground/background layers, generation risk, and reproduction strategy.

## When to Ask for Scope

If the video is long or the user asks for "analyze this video" without a target, use one of these defaults:

- analyze the first 30-60 seconds
- analyze the most visually dense 10-20 seconds if already known
- produce a fast shot map first, then ask which shots need deep prompts

## Tool Preference

Use `scripts/fast_sample_video.py` if available and `ffmpeg` is installed. It creates a timestamped frame folder, a manifest, and a contact sheet.

If `ffmpeg` is not available, do not attempt slow exhaustive extraction. Ask for screenshots/keyframes or request that `ffmpeg` be installed for fast local analysis.
