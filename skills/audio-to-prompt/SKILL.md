---
name: audio-to-prompt
description: "Transcribe audio and fuse spoken content, emotion, tone, pacing, and sound cues into image/video generation prompts. Use when the user provides audio/video files or transcripts and asks for 提示词, prompt engineering, AIGC image/video prompts, emotional prompt fusion, voice-to-prompt, 音频转录, 情绪分析, 台词转分镜, or converting audio content into cinematic, manga, visual, storyboard, or video-generation prompts. Pair with $aigc-manga-video-director when the task also needs reference-video analysis, shot-by-shot camera movement, composition, storyboard tables, Seedance prompts, or manga/drama production direction."
---

# Audio To Prompt

Transform audio into a prompt-ready creative brief: transcript, content summary, emotional intent, sound cues, and a final prompt for image or video generation.

## Workflow

1. Collect the source: audio/video file path, transcript text, or pasted dialogue.
2. When deterministic preprocessing materially helps, pair with `$ffmpeg` before transcription for video-to-audio extraction, target-range trimming, format conversion, channel/sample-rate normalization, or safe loudness normalization. Skip it when the original source is already usable.
3. Use a new `output_path`, preserve the original `source_path`, and pass `purpose`, `operation`, `preserve`, `constraints`, `verification`, and exactly one `downstream_skill` (`transcribe` or `audio-to-prompt`). Verify the relevant stream, duration, codec, sample rate, or channel count with `ffprobe` before continuing.
4. Keep ownership boundaries explicit: FFmpeg changes containers and streams only; `$transcribe` owns speech recognition; this skill owns emotion, pacing, delivery, sound interpretation, and prompt fusion. FFmpeg does not perform transcription or prompt writing.
5. If only an audio/video file is provided, transcribe it first. Prefer the existing `$transcribe` skill or its bundled CLI when available.
6. Extract content facts: who speaks, what happens, explicit objects, setting, actions, and narrative stakes.
7. Extract emotional evidence:
   - Separate directly observed audio cues from transcript-only inference.
   - Mark uncertainty when emotion is inferred from words rather than heard from audio.
   - Capture emotional trajectory, not only one label.
8. Convert the analysis into a prompt brief using `scripts/build_prompt_brief.py` when a structured reusable output is useful.
9. Write the final generation prompt for the requested target: image, video, storyboard, manga panel, voiceover moodboard, or generic prompt text.

## Pairing With Video Analysis

Use this skill with `$aigc-manga-video-director` when the source has both audio/emotion and visual direction needs.

Recommended order:

1. Use `$audio-to-prompt` to extract transcript, speaker intent, emotional arc, delivery rhythm, and sound cues.
2. Use `$aigc-manga-video-director` to analyze visual shots, camera movement, blocking, composition, timecodes, and generation risks.
3. Merge both outputs by shot ID or time range.
4. Write final prompts where the video-analysis skill controls camera/composition and this skill controls dialogue meaning, emotional continuity, tone, pacing, and sound atmosphere.

Handoff fields:

- `time_range`: audio/video time range when available.
- `transcript`: exact line or concise dialogue summary.
- `emotion_arc`: emotion at start, turn, and end.
- `delivery_cues`: pace, pauses, breath, volume, emphasis, laughter, sighs, or trembling.
- `sound_atmosphere`: ambient sound, silence, music mood, or sonic texture.
- `visual_prompt_injection`: short phrase to add into the image/video prompt.

When both skills produce prompts, do not duplicate the full prompt twice. Prefer one final prompt block that combines:

- camera path, composition, blocking, and shot continuity from `$aigc-manga-video-director`
- transcript meaning, emotional arc, delivery rhythm, and sound atmosphere from `$audio-to-prompt`

## Pairing With Output QC

When `aigc-output-qc` reviews a generated dialogue clip, return:

- exact transcript and supplied dialogue time range;
- audible delivery, pauses, emphasis, breath, and pacing evidence;
- visible lip-sync observations only where the supplied video supports them;
- uncertainty when cause or alignment cannot be confirmed.

Do not assign the final QC verdict. `aigc-output-qc` owns adjudication and the lowest-cost repair decision; `aigc-project-prompt-loop` owns the complete revised prompt.

## Transcription Rules

- Preserve important wording, pauses, repeated phrases, laughter, sighs, hesitation, and emphasis when they affect emotion or intent.
- If diarization is requested or multiple speakers are likely, keep speaker labels.
- If the transcript is noisy, include a short uncertainty note and avoid overfitting visual details to unclear words.
- Do not invent audio emotion. If only text is available, state that emotion is inferred from wording.

## Emotion Fusion

Capture four layers:

1. Content: literal meaning, topic, scene, events, and named entities.
2. Delivery: pace, volume, pitch movement, pauses, breath, laughter, trembling, firmness, softness, fatigue, or urgency.
3. Emotion: primary emotion, secondary emotion, intensity, changes over time, and contradictions between words and delivery.
4. Creative translation: visual atmosphere, lighting, camera movement, composition, color, texture, character expression, and rhythm.

Use concrete creative terms instead of generic labels. For example, turn "sad" into "quiet grief, lowered gaze, slow breathing, cool low-contrast light, still camera, sparse background."

## Output Format

Default to Chinese if the user writes Chinese. Provide:

```markdown
## 转录摘要
...

## 情绪与声音线索
- 主要情绪:
- 情绪变化:
- 可听见/可确认的线索:
- 仅从文本推断的线索:

## 提示词素材
- 人物/主体:
- 场景:
- 动作:
- 情绪表现:
- 视觉风格:
- 镜头/运动:
- 声音氛围:
- 避免:

## 最终提示词
...
```

For video prompts, include camera movement, duration, temporal beats, and transitions. For still images, focus on subject, composition, lighting, texture, and expression.

## Prompt Brief Script

Use `scripts/build_prompt_brief.py` to turn transcript text plus emotion notes into a consistent Markdown or JSON prompt brief.

Examples:

```bash
python scripts/build_prompt_brief.py transcript.txt --medium video --emotion "suppressed anger shifting into resignation" --language zh --out prompt_brief.md
python scripts/build_prompt_brief.py transcript.txt --medium image --emotion "warm nostalgia" --style "cinematic manga" --json --out prompt_brief.json
```

The script does not analyze audio by itself; use it after transcription or after manually noting emotion cues.

## Reference Map

- `references/prompt-patterns.md`: prompt structure, emotion vocabulary, and target-specific fusion patterns.
