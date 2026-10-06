#!/usr/bin/env python3
"""Replace panels in storyboard board images."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

from storyboard_layout import LayoutResult, detect_layout

Rect = Tuple[int, int, int, int]
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif"}
PANEL_STEM = re.compile(r"^[1-9][0-9]*$")


def parse_replace(value: str) -> Tuple[int, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Use N=PATH, for example 2=new.png")
    index_text, path_text = value.split("=", 1)
    try:
        index = int(index_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Panel index must be an integer") from exc
    if index < 1:
        raise argparse.ArgumentTypeError("Panel index is 1-based and must be >= 1")
    path = Path(path_text.strip().strip('"'))
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Replacement image does not exist: {path}")
    return index, path


def parse_manual_panel(value: str) -> Tuple[int, Rect]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Use N=X,Y,W,H")
    index_text, rect_text = value.split("=", 1)
    try:
        index = int(index_text)
        x, y, w, h = [int(part.strip()) for part in rect_text.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use N=X,Y,W,H with integer values") from exc
    if index < 1 or w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("Panel index, width, and height must be positive")
    return index, (x, y, x + w, y + h)


def collect_replacements(
    explicit: List[Tuple[int, Path]], directory: Path | None
) -> dict[int, Path]:
    """Collect numeric replacement files, then apply explicit overrides."""
    replacements: dict[int, Path] = {}
    if directory is not None:
        if not directory.exists():
            raise ValueError(f"Replacement directory does not exist: {directory}")
        if not directory.is_dir():
            raise ValueError(f"Replacement directory is not a directory: {directory}")
        directory_mappings = sorted(
            (
                (int(path.stem), path)
                for path in directory.iterdir()
                if path.is_file()
                and path.suffix.lower() in IMAGE_SUFFIXES
                and PANEL_STEM.fullmatch(path.stem)
            ),
            key=lambda item: item[0],
        )
        replacements.update(directory_mappings)
    for index, path in explicit:
        if not path.exists():
            raise ValueError(f"Replacement image does not exist: {path}")
        replacements[index] = path
    return replacements


def detect_window(image: Image.Image, panel: Rect) -> Rect:
    rgb = image.convert("RGB")
    x1, y1, x2, y2 = panel
    min_w = max(40, int((x2 - x1) * 0.35))
    min_h = max(40, int((y2 - y1) * 0.25))

    row_hits = []
    for y in range(y1, y2):
        bright = 0
        total = 0
        for x in range(x1, x2, max(1, (x2 - x1) // 300)):
            r, g, b = rgb.getpixel((x, y))
            total += 1
            if (r + g + b) / 3 > 185:
                bright += 1
        if total and bright / total > 0.30:
            row_hits.append(y)
    col_hits = []
    for x in range(x1, x2):
        bright = 0
        total = 0
        for y in range(y1, y2, max(1, (y2 - y1) // 220)):
            r, g, b = rgb.getpixel((x, y))
            total += 1
            if (r + g + b) / 3 > 185:
                bright += 1
        if total and bright / total > 0.25:
            col_hits.append(x)

    def merge_runs(indices: List[int], max_gap: int) -> List[Tuple[int, int]]:
        runs = []
        start = previous = None
        for value in indices:
            if start is None:
                start = previous = value
            elif value - previous <= max_gap + 1:
                previous = value
            else:
                runs.append((start, previous + 1))
                start = previous = value
        if start is not None:
            runs.append((start, previous + 1))
        return runs

    row_runs = [run for run in merge_runs(row_hits, 5) if run[1] - run[0] >= min_h]
    col_runs = [run for run in merge_runs(col_hits, 5) if run[1] - run[0] >= min_w]
    if not row_runs or not col_runs:
        return panel
    yy = max(row_runs, key=lambda run: run[1] - run[0])
    xx = max(col_runs, key=lambda run: run[1] - run[0])
    return (xx[0], yy[0], xx[1], yy[1])


def fit_image(source: Image.Image, size: Tuple[int, int], fit: str, fill: Tuple[int, int, int]) -> Image.Image:
    target_w, target_h = size
    src = source.convert("RGB")
    if fit == "stretch":
        return src.resize(size, Image.Resampling.LANCZOS)

    src_w, src_h = src.size
    if fit == "cover":
        scale = max(target_w / src_w, target_h / src_h)
        resized = src.resize((round(src_w * scale), round(src_h * scale)), Image.Resampling.LANCZOS)
        left = (resized.width - target_w) // 2
        top = (resized.height - target_h) // 2
        return resized.crop((left, top, left + target_w, top + target_h))

    scale = min(target_w / src_w, target_h / src_h)
    resized = src.resize((round(src_w * scale), round(src_h * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, fill)
    left = (target_w - resized.width) // 2
    top = (target_h - resized.height) // 2
    canvas.paste(resized, (left, top))
    return canvas


def draw_debug(image: Image.Image, panels: List[Rect], output: Path) -> None:
    annotated = image.convert("RGB").copy()
    draw = ImageDraw.Draw(annotated)
    font = ImageFont.load_default()
    for idx, (x1, y1, x2, y2) in enumerate(panels, start=1):
        draw.rectangle((x1, y1, x2 - 1, y2 - 1), outline=(255, 0, 0), width=5)
        draw.rectangle((x1 + 4, y1 + 4, x1 + 70, y1 + 34), fill=(255, 0, 0))
        draw.text((x1 + 12, y1 + 10), str(idx), fill=(255, 255, 255), font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    annotated.save(output)


def default_output(board: Path) -> Path:
    return board.with_name(f"{board.stem}_已替换{board.suffix}")


def default_preview(board: Path) -> Path:
    return board.with_name(f"{board.stem}_布局确认.png")


def main() -> int:
    parser = argparse.ArgumentParser(description="Replace panels in storyboard board images.")
    parser.add_argument("--board", required=True, type=Path, help="Storyboard board image.")
    parser.add_argument("--replace", action="append", type=parse_replace, default=[], help="N=PATH replacement mapping. Repeatable.")
    parser.add_argument("--replace-dir", type=Path, help="Directory containing numeric replacement image names.")
    parser.add_argument("--output", type=Path, help="Output image path.")
    parser.add_argument("--mode", choices=["full", "window"], default="full", help="Replacement target mode.")
    parser.add_argument("--fit", choices=["cover", "contain", "stretch"], default="cover", help="How replacement images fit target rectangles.")
    parser.add_argument("--fill", default="#000000", help="Letterbox fill color for --fit contain.")
    parser.add_argument("--list-panels", action="store_true", help="Print detected panel rectangles and exit.")
    parser.add_argument("--debug-layout", type=Path, help="Write annotated panel detection preview.")
    parser.add_argument("--manual-panel", action="append", type=parse_manual_panel, default=[], help="Override panel rectangle as N=X,Y,W,H. Repeatable.")
    args = parser.parse_args()

    if not args.board.exists():
        parser.error(f"Board image does not exist: {args.board}")
    image = Image.open(args.board).convert("RGB")
    layout: LayoutResult = detect_layout(image)
    panels = list(layout.panels)
    manual: Dict[int, Rect] = dict(args.manual_panel)
    for index, rect in manual.items():
        while len(panels) < index:
            panels.append((0, 0, image.width, image.height))
        panels[index - 1] = rect
    panels = sorted(panels, key=lambda rect: (rect[1], rect[0]))

    if args.debug_layout:
        draw_debug(image, panels, args.debug_layout)

    try:
        replacements = collect_replacements(args.replace, args.replace_dir)
    except ValueError as exc:
        parser.error(str(exc))

    if args.list_panels:
        print(f"board={args.board} size={image.width}x{image.height} panels={len(panels)}")
        for idx, (x1, y1, x2, y2) in enumerate(panels, start=1):
            print(f"{idx}: x={x1} y={y1} w={x2 - x1} h={y2 - y1}")
        return 0

    if not replacements:
        parser.error(
            "Nothing to replace. Add --replace N=PATH, --replace-dir PATH, "
            "or use --list-panels."
        )

    fill_text = args.fill.lstrip("#")
    if len(fill_text) != 6:
        parser.error("--fill must be a six-digit RGB hex color")
    try:
        fill = tuple(int(fill_text[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        parser.error("--fill must be a six-digit RGB hex color")
    output = image.copy()
    for index, replacement_path in replacements.items():
        if index > len(panels):
            parser.error(
                f"Panel {index} requested, but only {len(panels)} panels were detected."
            )
        rect = panels[index - 1]
        if args.mode == "window":
            rect = detect_window(image, rect)
        x1, y1, x2, y2 = rect
        replacement = Image.open(replacement_path)
        fitted = fit_image(replacement, (x2 - x1, y2 - y1), args.fit, fill)
        output.paste(fitted, (x1, y1))
        print(f"replaced panel {index}: {replacement_path}")

    out_path = args.output or default_output(args.board)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output.save(out_path)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
