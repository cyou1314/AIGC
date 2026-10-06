# Prompt Patterns

Use this reference when shaping the final prompt after transcription and emotion analysis.

## Emotion Vocabulary

Prefer specific emotional phrases:

- Quiet grief: restrained expression, slow pauses, lowered gaze, soft breath, cool muted light.
- Suppressed anger: clipped phrasing, tense jaw, sharp stillness, hard side light, narrow framing.
- Panic: fast breath, broken sentences, unstable camera, high contrast, crowded composition.
- Nostalgia: softened voice, gentle pauses, warm rim light, film grain, lingering camera.
- Awe: widened silence, rising tone, wide frame, scale contrast, slow reveal.
- Exhaustion: low energy, trailing words, heavy eyelids, desaturated palette, static framing.
- Defiance: steady tone, direct gaze, upright posture, strong contrast, forward camera push.

## Image Prompt Pattern

Combine:

1. Subject and action.
2. Emotional expression translated into face, body, and posture.
3. Setting and story context from the transcript.
4. Lighting, color, texture, and composition.
5. Style and quality constraints.
6. Negative constraints.

Template:

```text
[subject] [action] in [setting], expressing [emotion translated into visible behavior],
with [important transcript detail], [lighting/color], [composition/lens],
[style], [quality constraints]. Avoid [negative constraints].
```

## Video Prompt Pattern

Combine:

1. Duration and shot type.
2. Opening beat from the audio content.
3. Emotional progression over time.
4. Camera motion and pacing matched to delivery.
5. Sound atmosphere if relevant.
6. End frame or transition.

Template:

```text
[duration] [shot type]. Start with [opening visual beat].
As the line/content develops, the emotion shifts from [start emotion] to [end emotion].
Camera [movement], pacing [slow/fast/uneven], lighting [description],
sound atmosphere [description]. End on [final visual beat].
```

## Video Analysis Handoff Pattern

When combining with `$aigc-manga-video-director`, use the video skill for shot evidence and this skill for audio emotion.

Per-shot merge pattern:

```text
Shot [Sxx], [time range].
Visual basis: [camera path, composition, subject blocking, lighting from video analysis].
Audio basis: [transcript or dialogue summary].
Emotion fusion: [emotion arc plus delivery cues].
Final prompt injection: [short phrase that makes the audio emotion visible in expression, rhythm, lighting, camera pacing, and sound atmosphere].
```

Final video prompt pattern:

```text
[time range] [shot size and camera path from video analysis].
The line/audio expresses [transcript meaning]; delivery carries [emotion arc and prosody].
Subject movement and facial expression show [visible emotion translation].
Camera rhythm follows [audio pacing], with [lighting/color/sound atmosphere].
End frame preserves [visual continuity and final emotional beat].
```

## Manga/Storyboard Pattern

Break audio into beats:

- Beat 1: setup line or sound cue, establishing panel.
- Beat 2: emotional turn, closer framing or reaction panel.
- Beat 3: consequence or silence, final panel with strongest expression.

Preserve exact lines only when they are important dialogue. Otherwise summarize the content and let the prompt focus on visual storytelling.
