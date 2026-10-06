# FFmpeg Reference

Load this file only for operations beyond the common AIGC preprocessing recipes in `SKILL.md`.

## Table of Contents

- [Shell and path notes](#shell-and-path-notes)
- [Filter syntax](#filter-syntax)
- [Codecs and containers](#codecs-and-containers)
- [Quality settings](#quality-settings)
- [Input and output options](#input-and-output-options)
- [Advanced recipes](#advanced-recipes)
- [Remotion preparation](#remotion-preparation)
- [Delivery and platform export](#delivery-and-platform-export)

## Shell and Path Notes

The commands are FFmpeg commands, but line continuation differs by shell:

- PowerShell: prefer one-line commands; quote variables as `"$source"`.
- Bash: use `\` for line continuation and quote paths.
- Windows paths: use absolute paths when handing artifacts between skills.

Use `-n` for non-destructive work. Use `-y` only when the user explicitly authorizes replacement.

## Filter Syntax

### Video filters

Chain simple filters with commas:

```text
-vf "scale=1920:1080,fps=30,crop=1280:720"
```

Use labels for complex graphs:

```text
-filter_complex "[0:v]scale=1920:1080[scaled];[scaled]fps=30[out]" -map "[out]"
```

| Filter | Syntax | Typical use |
|---|---|---|
| scale | `scale=w:h` | Resize; use `-2` to keep an even calculated dimension |
| crop | `crop=w:h:x:y` | Reframe |
| fps | `fps=N` | Create a constant-frame-rate derivative |
| pad | `pad=w:h:x:y:color` | Fit a target canvas |
| fade | `fade=t=in/out:st=N:d=N` | Video fade |
| setpts | `setpts=N*PTS` | Video speed |
| drawtext | `drawtext=...` | Burn in text |
| overlay | `overlay=x:y` | Composite video |

### Audio filters

| Filter | Syntax | Typical use |
|---|---|---|
| volume | `volume=N` | Simple gain |
| afade | `afade=t=in/out:st=N:d=N` | Audio fade |
| atempo | `atempo=N` | Audio speed; each stage supports 0.5 to 2.0 |
| loudnorm | `loudnorm=I=-16:TP=-1.5:LRA=11` | Conditional speech normalization |

For AIGC transcription, first extract unnormalized `pcm_s16le`, mono, 16 kHz audio. Apply `loudnorm` only if intelligibility requires it; normalization can reduce useful performance dynamics.

## Codecs and Containers

### Video codecs

| Codec | Use case | Notes |
|---|---|---|
| `libx264` | Universal H.264 | Stable compatibility default |
| `libx265` | H.265/HEVC | Smaller files, less universal decoding |
| `libvpx-vp9` | WebM | Web delivery |
| `prores` | Editing intermediate | Large files |
| `copy` | Stream copy | Fast, no filtering, keyframe-bound cuts |

### Audio codecs

| Codec | Use case | Notes |
|---|---|---|
| `aac` | MP4 | Compatible delivery |
| `libmp3lame` | MP3 | Broad playback support |
| `libvorbis` | WebM/OGG | Open format |
| `pcm_s16le` | WAV | Stable transcription input |
| `copy` | Stream copy | No filtering or resampling |

| Container | Extension | Best for |
|---|---|---|
| MP4 | `.mp4` | General playback and web |
| MOV | `.mov` | Editing and ProRes |
| WebM | `.webm` | Web |
| MKV | `.mkv` | Archive and multiple streams |
| GIF | `.gif` | Short silent loops |

## Quality Settings

For x264/x265 CRF, lower values mean higher quality and larger files:

| CRF | Typical role |
|---|---|
| 0 | Lossless |
| 17-18 | Visually lossless intermediate |
| 19-22 | High-quality production |
| 23 | General default |
| 24-27 | Web delivery |
| 28+ | Analysis proxy or draft |

Encoder presets trade encoding time for compression efficiency:

`ultrafast` → `superfast` → `veryfast` → `faster` → `fast` → `medium` → `slow` → `slower` → `veryslow`

Choose a faster preset for temporary derivatives and a slower preset only when file size or final quality justifies the time.

## Input and Output Options

| Option | Position | Purpose |
|---|---|---|
| `-ss` | before or after `-i` | Fast seek before input; more accurate seek after input |
| `-t` | output | Duration limit |
| `-n` | output | Never overwrite |
| `-y` | output | Overwrite |
| `-movflags +faststart` | output | Move MP4 metadata for web playback |
| `-pix_fmt yuv420p` | output | Broad H.264 playback compatibility |
| `-an` | output | Remove audio |
| `-vn` | output | Remove video |

Useful probes:

```powershell
ffprobe -v error -show_entries format=duration -of csv=p=0 "$source"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of json "$source"
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,channels,sample_rate -of json "$source"
```

## Advanced Recipes

### Stream-copy trim

Use only when keyframe-aligned boundaries are acceptable:

```powershell
ffmpeg -n -ss 00:01:30 -i "$source" -t 00:00:30 -c copy "$output"
```

### Concatenate matching files

Create a UTF-8 text file:

```text
file 'D:\media\part1.mp4'
file 'D:\media\part2.mp4'
```

Then:

```powershell
ffmpeg -n -f concat -safe 0 -i "D:\media\files.txt" -c copy "$output"
```

If stream properties differ, normalize them first or use a filter graph and re-encode.

### Change speed

Two-times video and audio:

```powershell
ffmpeg -n -i "$source" -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" -map "[v]" -map "[a]" -c:v libx264 -c:a aac "$output"
```

For audio factors outside 0.5 to 2.0, chain multiple `atempo` stages.

### Add fades

```powershell
ffmpeg -n -i "$source" -vf "fade=t=in:st=0:d=1,fade=t=out:st=9:d=1" -af "afade=t=in:st=0:d=1,afade=t=out:st=9:d=1" -c:v libx264 -c:a aac "$output"
```

Adjust the second fade start to the actual duration.

### Create a quality GIF

```powershell
ffmpeg -n -i "$source" -vf "fps=10,scale=480:-2:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" "$output"
```

### Picture in picture

```powershell
ffmpeg -n -i "$main" -i "$overlay" -filter_complex "[1:v]scale=320:-2[pip];[0:v][pip]overlay=W-w-20:H-h-20[v]" -map "[v]" -map 0:a? -c:v libx264 -c:a aac "$output"
```

## Remotion Preparation

- Prefer H.264 in MP4 for broadly compatible source playback.
- Use `-pix_fmt yuv420p` when the input pixel format causes browser decoding issues.
- Use `-movflags +faststart` for web-oriented playback.
- Match the composition frame rate and dimensions only when required; avoid needless re-encoding.
- Keep preprocessing separate from the final Remotion render.

Example compatibility conversion:

```powershell
ffmpeg -n -i "$source" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$output"
```

## Delivery and Platform Export

Use a delivery derivative, never an analysis proxy. A conservative MP4 starting point is:

```powershell
ffmpeg -n -i "$source" -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$output"
```

Before export, verify the destination platform's current official requirements for:

- aspect ratio and resolution;
- maximum duration and file size;
- accepted codecs and containers;
- frame-rate and audio requirements;
- HDR, color space, captions, and transparency.

Do not preserve hard-coded platform limits in the skill because they drift. Record the verified requirements in the task handoff, then adapt scale, frame rate, bitrate, and container deliberately.
