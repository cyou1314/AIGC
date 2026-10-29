---
name: storyboard-image-replacer
description: Use when replacing one or more images in a PNG/JPG storyboard board, shot board, keyframe board, 分镜板, or 分镜版. Supports direct panel mapping and numbered replacement folders.
---

# Storyboard Image Replacer

Replace images inside an existing storyboard board.

The CLI defaults to `full`, which replaces the entire panel including numbering, timecodes and captions. When the user asks to preserve these elements or asks only to replace the picture, use `--mode window`, inspect the detected picture-window bounds, and verify the actual output. If the window is uncertain, do not fall back to replacing the whole panel: use `--manual-window N=X,Y,W,H` for the verified image-only rectangle. Use `full` when replacement of the whole panel is actually intended.

## Workflow

1. Find the source board and replacement images.
2. Number panels from top to bottom, then left to right, starting at `1`.
3. Run one of the two replacement commands below.
4. Use an explicit new output path appropriate to the current workspace; in the Desktop project use the configured Codex-generated-files folder unless a project path is specified. Never overwrite the original, replacements or an existing output. Open the result and verify selected panels and protected labels.

## Replace Selected Panels

Use repeatable `--replace N=PATH` mappings:

```powershell
& "<python>" "<skill>/scripts/replace_storyboard_panels.py" `
  --board "<board.png>" `
  --replace "1=<new-image-1.png>" `
  --replace "3=<new-image-3.png>" `
  --mode window `
  --output "<new-output.png>"
```

## Replace From A Numbered Folder

Put replacement images in one folder and name them `1.png`, `2.jpg`, `3.webp`, and so on. Only present numbers are replaced.

```powershell
& "<python>" "<skill>/scripts/replace_storyboard_panels.py" `
  --board "<board.png>" `
  --replace-dir "<replacement-folder>" `
  --mode window `
  --output "<new-output.png>"
```

An explicit `--replace` mapping overrides the same number found in `--replace-dir`.

## Check Panel Numbers

When the layout is unclear:

```powershell
& "<python>" "<skill>/scripts/replace_storyboard_panels.py" --board "<board.png>" --list-panels
```

Inspect the detected order and panel boundaries. If confidence is low or detection misses a panel, use `--debug-layout` to inspect the board, then supply verified `--manual-panel` bounds for each target; low-confidence replacement without manual target bounds is rejected. A high score is still not proof of correct numbering or preserved labels.

## Options

- `--board`: source storyboard board image.
- `--replace N=PATH`: replace panel `N`; repeat for multiple panels.
- `--replace-dir PATH`: load replacements from numeric filenames in a folder.
- `--output`: a new destination path. The CLI otherwise proposes `<原名>_已替换.<扩展名>` beside the source, but workspace output rules take priority. Existing destinations and input-image aliases are refused.
- `--mode full`: replace the whole panel. This is the default.
- `--mode window`: replace only the picture window; an unidentifiable or full-panel window is rejected instead of silently replacing the full panel. Inspect the output because automatic detection cannot prove every label was preserved.
- `--manual-window N=X,Y,W,H`: manually specify a verified picture-only rectangle within panel N in source-image pixels; requires `--mode window`.
- `--fit cover`: fill the panel while preserving aspect ratio. This is the default.
- `--fit contain`: show the full image with letterboxing.
- `--fit stretch`: resize without preserving aspect ratio.
- `--list-panels`: print detected panel rectangles.
- `--debug-layout PATH`: save an image showing detected panel numbers.
- `--manual-panel N=X,Y,W,H`: manually define a panel rectangle.
