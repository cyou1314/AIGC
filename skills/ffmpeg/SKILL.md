---
name: ffmpeg
description: Use when local video or audio needs deterministic preprocessing for AIGC video analysis, transcription, audio prompting, proxy generation, trimming, extraction, conversion, resizing, compression, concatenation, or media inspection with FFmpeg and FFprobe.
---

# FFmpeg Media Preprocessing

Use FFmpeg as the local execution layer for deterministic media transforms. Keep creative interpretation in the downstream AIGC skill.

Commands below use PowerShell variables; FFmpeg arguments are cross-platform. On either OS install FFmpeg and FFprobe in PATH and check both. On macOS use shell variables such as `source_path="/absolute/source.mp4"` and call the same argument array. No bundled machine-specific binary is assumed.

## Core Rules

1. Inspect before transforming.
2. Skip preprocessing when the source already meets the downstream need.
3. Preserve the source. Use a new output path and `-n` unless overwrite is explicitly authorized.
4. Treat proxies, trims, extracted audio, and frames as analysis-only derivatives, not final masters.
5. Verify every output with FFprobe before handoff.
6. Do not perform visual analysis, transcription, emotional interpretation, or prompt writing here.

## Collaboration Contract

Use these fields when another skill requests or receives a transform:

```yaml
purpose: why the derivative is needed
source_path: absolute path to the original
output_path: absolute path to the derivative
operation: inspect | proxy | trim | extract_audio | normalize_audio | extract_frame | convert
preserve: properties that must not change
constraints: duration, resolution, codec, channels, sample rate, or size limits
verification: FFprobe evidence and any warnings
downstream_skill: intended consumer
```

Routing:

- `aigc-project-prompt-loop` orchestrates the workflow and receives verification.
- `aigc-manga-video-director` decides which visual ranges or proxies are useful.
- `aigc-output-qc` requests only the verified metadata, proxy, trim, frame, audio, crop, reframe, or supplied-material composite needed for a specified QC purpose and time range.
- `transcribe` owns speech recognition.
- `audio-to-prompt` owns emotion, delivery, pacing, and sound interpretation.
- This skill only creates and verifies deterministic derivatives.

For QC, do not assign a pass/fail verdict and do not claim that FFmpeg can invent missing visual content.

## Windows-First AIGC Recipes

Set explicit paths:

```powershell
$source = "D:\media\source.mp4"
$output = "D:\media\source_proxy.mp4"
```

### Inspect media

```powershell
ffprobe -v error -show_format -show_streams -of json "$source"
```

Check duration, streams, resolution, frame rate, audio channels, sample rate, and codecs. If these already satisfy the consumer, hand off the original without conversion.

### Create an analysis proxy

Use for long, high-resolution, or slow-to-decode video:

```powershell
ffmpeg -n -i "$source" -vf "scale='min(1280,iw)':-2,fps=24" -c:v libx264 -crf 28 -preset veryfast -c:a aac -b:a 96k "$output"
```

Do not use this proxy as a final render or delivery master.

### Trim a precise analysis range

```powershell
$output = "D:\media\source_0030_0045.mp4"
ffmpeg -n -i "$source" -ss 00:00:30 -t 00:00:15 -c:v libx264 -crf 20 -preset fast -c:a aac -b:a 160k "$output"
```

Re-encoding favors accurate boundaries. Use stream copy only when keyframe-level accuracy is acceptable.

### Extract transcription-ready audio

Start with an unnormalized mono WAV so vocal dynamics remain intact:

```powershell
$output = "D:\media\source_16k_mono.wav"
ffmpeg -n -i "$source" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$output"
```

### Normalize only when needed

Use normalization only when speech is too quiet, inconsistent, or otherwise difficult to recognize:

```powershell
$output = "D:\media\source_16k_mono_normalized.wav"
ffmpeg -n -i "$source" -vn -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ac 1 -ar 16000 -c:a pcm_s16le "$output"
```

Do not normalize intelligible audio merely for consistency. It can flatten meaningful delivery dynamics used by `audio-to-prompt`. Prefer the unnormalized extraction first, and retain both derivatives if normalization becomes necessary.

### Extract a representative frame

```powershell
$output = "D:\media\frame_0030.png"
ffmpeg -n -ss 00:00:30 -i "$source" -frames:v 1 "$output"
```

Use deliberate timestamps from the director or shot sampling workflow; do not claim that one frame represents a whole shot.

## Verification Gate

Probe the derivative:

```powershell
ffprobe -v error -show_format -show_streams -of json "$output"
```

Before handoff, confirm:

- the output exists and is readable;
- duration is plausible for the requested range;
- required video and audio streams exist;
- resolution, frame rate, channels, and sample rate match the request;
- the original remains unchanged;
- the derivative is labeled with its intended purpose.

Return a warning instead of silently accepting a mismatch.

## Decision Guide

| Situation | Action |
|---|---|
| Source is already usable | Skip conversion and report inspection |
| Long or high-resolution video slows analysis | Create an analysis proxy |
| Only one section matters | Trim that range |
| Speech recognition needs stable input | Extract 16 kHz mono PCM WAV |
| Speech remains difficult to recognize | Add conditional loudness normalization |
| QC needs deterministic evidence or a supported local transform | Create only the requested derivative and return FFprobe verification |
| Final delivery, Remotion, GIF, concat, fades, or complex filters | Load `reference.md` |

## Common Failures

- Paths with spaces: quote every path.
- Existing output: choose a new path; do not replace it implicitly.
- Odd scaled dimensions: use `-2` for the calculated dimension.
- Missing audio stream: inspect first and do not fabricate one.
- Variable-frame-rate timing issues: create a constant-frame-rate analysis derivative only when the consumer requires it.
- Hardware encoder differences: fall back to software `libx264` for portability.

## Reference Loading

Read `reference.md` only when the request needs codecs and containers, CRF and presets, filter graphs, speed changes, concat, fades, GIFs, Remotion preparation, or final delivery.

Platform upload specifications change. Verify the current official platform requirements before applying delivery limits from any reference or prior project.
