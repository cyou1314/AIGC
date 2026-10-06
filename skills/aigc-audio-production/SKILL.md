---
name: aigc-audio-production
description: Plan and coordinate AIGC audio deliverables such as voiceover, dubbing, podcasts, music, sound effects and mix preparation. Use when the requested output is sound or an audio production plan. Pure transcription belongs to transcribe, and audio-to-video prompt conversion belongs to audio-to-prompt.
---

# AIGC Audio Production

Select voice, music, effects, mix/edit, or podcast mode. Establish the actual deliverable: sound file, timed takes, stems, editing plan, or generation specification. Text and a generated waveform are distinct deliverables.

## Voice / dubbing

Lock the user's text, language, names/pronunciation and chosen voice reference. Establish tone, emotional changes, natural pauses and measured target window. If a passage is too long, propose wording or window adjustments rather than silently accelerating speech. Transcription uses `transcribe`; extract/reformat actual media with `ffmpeg` when needed.

Use `narrator` only when its explicit trigger and fixed-window/continuous-read/presenter-overlay modes fit. Otherwise discover an available voice-generation tool for the requested task. Transcription credentials do not establish TTS readiness. Character dialogue and narrator delivery have different breathing and performance requirements.

## Music / sound effects

Capture scene purpose, musical energy curve, instrumentation/timbre, tempo or temporal landmarks when known, and where dialogue needs space. Sound effects specify cause, material, distance and synchronization landmark. Discover the actual music/effects generator when the user requests audio creation; do not fabricate a supported provider from the installed transcribe or image tools.

If the provider cannot be used, deliver the specification and name the blocked sound-production action. A specification is not a produced audio file. For a sequence, link cues to real media timecodes, labeling estimates when no timed source exists.

## Editing / mixing / checks

Keep original files. Use a supported media/editor tool for trims, crossfades, leveling and stems. Loudness, sample rate, channels and delivery codec come from the actual use case/user requirements; do not enforce one universal broadcast target.

Inspect durations and technical validity, then listen to the relevant output for wording, pronunciation, unwanted cuts, distortion, noise and the intended emotional result. If audio playback is unavailable, mark the listening check pending. Do not claim it sounds correct from a transcript or file size.

Return actual files and known measurements; record voice/text version or music/cue version and any pending check in the project page. For video integration, hand off real durations/landmarks and stems. `audio-to-prompt` can then own translating those observations into visual prompts.
