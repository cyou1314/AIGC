#!/usr/bin/env python3
"""Enhance sketch/storyboard frames for easier visual analysis.

Creates high-contrast grayscale, adaptive-threshold, and edge-enhanced versions
of each input image. Use on extracted frames from pencil sketches, animatics,
storyboard videos, or low-contrast line drawings.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enhance sketch frames for analysis.")
    parser.add_argument("input", help="Input image file or folder")
    parser.add_argument("--out", default=None, help="Output folder")
    parser.add_argument("--width", type=int, default=900, help="Output width")
    parser.add_argument("--contact-sheet", action="store_true", help="Create contact sheet")
    return parser.parse_args()


def iter_images(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*") if p.suffix.lower() in IMAGE_EXTS)


def resize_keep_aspect(image: np.ndarray, width: int) -> np.ndarray:
    h, w = image.shape[:2]
    if w <= width:
        return image
    scale = width / float(w)
    return cv2.resize(image, (width, max(1, int(h * scale))), interpolation=cv2.INTER_AREA)


def enhance(path: Path, out_dir: Path, width: int) -> list[Path]:
    image = cv2.imread(str(path))
    if image is None:
        return []
    image = resize_keep_aspect(image, width)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    contrast = clahe.apply(denoised)
    blur = cv2.GaussianBlur(contrast, (0, 0), 1.1)
    sharpen = cv2.addWeighted(contrast, 1.7, blur, -0.7, 0)
    thresh = cv2.adaptiveThreshold(
        sharpen,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        9,
    )
    edges = cv2.Canny(sharpen, 60, 160)
    edge_overlay = cv2.cvtColor(sharpen, cv2.COLOR_GRAY2BGR)
    edge_overlay[edges > 0] = (0, 0, 255)

    stem = path.stem
    outputs = [
        (out_dir / f"{stem}_contrast.jpg", sharpen),
        (out_dir / f"{stem}_threshold.jpg", thresh),
        (out_dir / f"{stem}_edges.jpg", edge_overlay),
    ]
    saved = []
    for output, frame in outputs:
        cv2.imwrite(str(output), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        saved.append(output)
    return saved


def make_contact_sheet(paths: list[Path], output: Path) -> None:
    if not paths:
        return
    thumbs = [Image.open(path).convert("RGB") for path in paths]
    thumb_w = 240
    thumb_h = 160
    label_h = 26
    cols = min(3, len(thumbs))
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, (path, image) in enumerate(zip(paths, thumbs)):
        image.thumbnail((thumb_w, thumb_h))
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(image, (x + (thumb_w - image.width) // 2, y))
        draw.text((x + 6, y + thumb_h + 6), path.name[:34], fill="black", font=font)
    sheet.save(output, quality=90)


def main() -> int:
    args = parse_args()
    source = Path(args.input).expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"Input not found: {source}")
    inputs = iter_images(source)
    stems = [p.stem.casefold() for p in inputs]
    if len(set(stems)) != len(stems):
        raise SystemExit("Input images have duplicate basenames; select distinct names to avoid overwriting outputs.")
    out_dir = Path(args.out).expanduser().absolute() if args.out else source.with_name(source.stem + "_enhanced")
    if out_dir.exists() or out_dir.is_symlink():
        raise SystemExit("Output folder already exists; select a new folder to preserve prior files.")
    out_dir.mkdir(parents=True, exist_ok=False)
    all_outputs: list[Path] = []
    for image_path in inputs:
        all_outputs.extend(enhance(image_path, out_dir, args.width))
    if args.contact_sheet:
        make_contact_sheet(all_outputs, out_dir / "sketch_enhancement_contact_sheet.jpg")
    print(f"Input frames: {len(inputs)}")
    print(f"Enhanced files: {len(all_outputs)}")
    print(f"Output: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
