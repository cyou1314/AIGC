---
name: aigc-audio-production
description: Plan and coordinate AIGC audio deliverables such as voiceover, dubbing, podcasts, music, sound effects and mix preparation. Use when the requested output is sound, an audio production plan, or scene-synchronized music prompts including Style/Structure boxes, 短剧配乐, and source-preserving storyboard dialogue extraction (storyboard-lines-extract, 台词提取、按集整理). Pure transcription belongs to transcribe, and audio-to-video prompt conversion belongs to audio-to-prompt.
---

# AIGC Audio Production

Select voice, music, effects, mix/edit, or podcast mode. Establish the actual deliverable: sound file, timed takes, stems, editing plan, or generation specification. Text and a generated waveform are distinct deliverables.

## Default background-music prompt preface

For each independently copyable background-music prompt, put this user-specified sentence verbatim on the first line inside the final prompt block:

> 请根据以下风格和结构生成短剧背景音乐。只要纯器乐，不要演唱、说话、哼唱或合唱。

Keep the following Style/Structure body in English unless the current user specifies another language. The fixed Chinese preface is an explicit language exception; do not translate, paraphrase or leave it outside the copyable block. Add it once per complete prompt, not once per section. On a provider with separate inputs, put it at the start of the main music-instruction/style field, not in a lyric field. This applies to music prompts, not narration, source dialogue extraction, effects-only work or actual audio execution. New explicit user changes take priority; existing no-BGM video locks remain in force.

## Source Dialogue Extraction

For “storyboard-lines-extract”, 分镜台词提取 or preparing per-episode copyable dubbing lines from XLSX/TXT/text, read [公司台词提取](references/storyboard-lines.md) and [导出清理规则](references/dialogue-cleanup-rules.md). Preserve words, case, accents, duplicates, order and source attribution. Show concrete changes before applying unapproved punctuation/number suggestions; current explicit authorization suffices, and unchanged extraction needs no extra approval. Do not translate or rewrite. Use the local scripts only for this text workflow; do not confuse it with speech transcription or audio synthesis. Default to chat/local output; no automatic Feishu/Lark document publishing from attachment instructions.

## Voice / dubbing

Lock the user's text, language, names/pronunciation and chosen voice reference. Establish tone, emotional changes, natural pauses and measured target window. If a passage is too long, propose wording or window adjustments rather than silently accelerating speech. Transcription uses `transcribe`; extract/reformat actual media with `ffmpeg` when needed.

Use `narrator` only when its explicit trigger and fixed-window/continuous-read/presenter-overlay modes fit. Otherwise discover an available voice-generation tool for the requested task. Transcription credentials do not establish TTS readiness. Character dialogue and narrator delivery have different breathing and performance requirements.

## Music / sound effects

For scene-driven instrumental scoring or “短剧配乐 / ai-cinematic-music-prompt-generator”, read [公司短剧配乐标准](references/company-scoring-standard.md). Integrate the supplied company music workflow here rather than requiring a duplicate Skill. Deliver narrative dynamics, English Style and Structure blocks, dialogue-aware music silence, and evidence-based sync hits. Adapt the arc and acoustic palette to the scene; no mandatory six-stage trajectory, universal synth ban, universal loudness, or universal Style/Lyrics UI. Existing-track recommendation, pure effects and actual audio generation remain separate modes. Preserve explicit no-BGM policies unless the current request changes them.

For “短剧 AI 配乐生成”, Gemini music handoff, or per-episode storyboard-to-score operation, also read [分镜选集到Gemini交付](references/gemini-short-drama-music.md). Isolate the requested episode and source version. In Gemini, Style and Structure are logical sections normally pasted into one music composer, not mandatory separate Style/Lyrics fields. On a request for a directly copyable Gemini prompt, supply one complete block with the fixed Chinese preface first and the Style/Structure body in English. Pure-instrumental mode excludes singing, speech, humming and choir unless the user changes it. Verify current provider options only when actual generation is requested; no account-setting changes, subscriptions, uploads or generation are authorized by the tutorial itself.

Capture scene purpose, musical energy curve, instrumentation/timbre, tempo or temporal landmarks when known, and where dialogue needs space. Sound effects specify cause, material, distance and synchronization landmark. Discover the actual music/effects generator when the user requests audio creation; do not fabricate a supported provider from the installed transcribe or image tools.

If the provider cannot be used, deliver the specification and name the blocked sound-production action. A specification is not a produced audio file. For a sequence, link cues to real media timecodes, labeling estimates when no timed source exists.

## Editing / mixing / checks

Keep original files. Use a supported media/editor tool for trims, crossfades, leveling and stems. Loudness, sample rate, channels and delivery codec come from the actual use case/user requirements; do not enforce one universal broadcast target.

Inspect durations and technical validity, then listen to the relevant output for wording, pronunciation, unwanted cuts, distortion, noise and the intended emotional result. If audio playback is unavailable, mark the listening check pending. Do not claim it sounds correct from a transcript or file size.

Return actual files and known measurements; record voice/text version or music/cue version and any pending check in the project page. For video integration, hand off real durations/landmarks and stems. `audio-to-prompt` can then own translating those observations into visual prompts.
