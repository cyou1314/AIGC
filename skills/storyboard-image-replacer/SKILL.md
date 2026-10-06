---
name: storyboard-image-replacer
description: Use when replacing one or more images in a PNG/JPG storyboard board, shot board, keyframe board, 分镜板, or 分镜版. Supports direct panel mapping and numbered replacement folders.
---

# Storyboard Image Replacer

Replace images inside an existing storyboard board.

The default mode is `full`. It covers the whole detected panel, including numbering, timecodes, captions, and bottom strips. Use `window` only when the user explicitly asks to preserve those elements.

## Workflow

1. Find the source board and replacement images.
2. Number panels from top to bottom, then left to right, starting at `1`.
3. Run one of the two replacement commands below.
4. Open the output image and verify the replaced panels.

## Replace Selected Panels

Use repeatable `--replace N=PATH` mappings:

```powershell
& "<python>" "<skill>/scripts/replace_storyboard_panels.py" `
  --board "<board.png>" `
  --replace "1=<new-image-1.png>" `
  --replace "3=<new-image-3.png>"
```

## Replace From A Numbered Folder

Put replacement images in one folder and name them `1.png`, `2.jpg`, `3.webp`, and so on. Only present numbers are replaced.

```powershell
& "<python>" "<skill>/scripts/replace_storyboard_panels.py" `
  --board "<board.png>" `
  --replace-dir "<replacement-folder>"
```

An explicit `--replace` mapping overrides the same number found in `--replace-dir`.

## Check Panel Numbers

When the layout is unclear:

```powershell
& "<python>" "<skill>/scripts/replace_storyboard_panels.py" --board "<board.png>" --list-panels
```

If auto-detection misses a panel, use `--debug-layout` to inspect numbering, then use `--manual-panel` only when necessary.

## Options

- `--board`: source storyboard board image.
- `--replace N=PATH`: replace panel `N`; repeat for multiple panels.
- `--replace-dir PATH`: load replacements from numeric filenames in a folder.
- `--output`: destination path. If omitted, write `<原名>_已替换.<扩展名>` beside the source.
- `--mode full`: replace the whole panel. This is the default.
- `--mode window`: replace only the picture window.
- `--fit cover`: fill the panel while preserving aspect ratio. This is the default.
- `--fit contain`: show the full image with letterboxing.
- `--fit stretch`: resize without preserving aspect ratio.
- `--list-panels`: print detected panel rectangles.
- `--debug-layout PATH`: save an image showing detected panel numbers.
- `--manual-panel N=X,Y,W,H`: manually define a panel rectangle.
