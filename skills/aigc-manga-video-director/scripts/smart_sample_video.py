#!/usr/bin/env python3
"""OpenCV smart sampler for AIGC video analysis.

Samples frames at a fixed interval, skips near-duplicates using frame difference,
and creates a contact sheet plus manifest. Uses OpenCV and Pillow.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smart sample non-duplicate video frames.")
    parser.add_argument("video", help="Input video path")
    parser.add_argument("--out", default=None, help="Output folder")
    parser.add_argument("--every-sec", type=float, default=1.0, help="Candidate frame interval")
    parser.add_argument("--max-frames", type=int, default=32, help="Maximum frames to keep")
    parser.add_argument("--width", type=int, default=640, help="Output frame width")
    parser.add_argument("--diff-threshold", type=float, default=7.0, help="Mean grayscale diff threshold")
    return parser.parse_args()


def timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = seconds - minutes * 60
    return f"{minutes:02d}:{secs:05.2f}"


def resize_keep_aspect(frame, width: int):
    h, w = frame.shape[:2]
    scale = width / float(w)
    return cv2.resize(frame, (width, max(1, int(h * scale))), interpolation=cv2.INTER_AREA)


def save_contact_sheet(rows: list[dict], output: Path) -> None:
    images = [Image.open(row["path"]).convert("RGB") for row in rows]
    thumb_w = 240
    thumb_h = 150
    label_h = 28
    cols = min(4, len(images))
    sheet_rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, sheet_rows * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, (row, image) in enumerate(zip(rows, images), start=1):
        image.thumbnail((thumb_w, thumb_h))
        x = ((idx - 1) % cols) * thumb_w
        y = ((idx - 1) // cols) * (thumb_h + label_h)
        sheet.paste(image, (x + (thumb_w - image.width) // 2, y))
        draw.text((x + 6, y + thumb_h + 6), f"K{idx:02d} {row['time']}", fill="black", font=font)
    sheet.save(output, quality=90)


def main() -> int:
    args = parse_args()
    video = Path(args.video).expanduser().resolve()
    if not video.exists():
        raise SystemExit(f"Video not found: {video}")

    out = Path(args.out).expanduser().resolve() if args.out else video.with_suffix("")
    frames_dir = out / "smart_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {video}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = frame_count / fps if fps else 0
    step = max(1, int(args.every_sec * fps))

    rows: list[dict] = []
    prev_small = None
    frame_idx = 0
    candidate_idx = 0

    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if not ok:
            break

        small = cv2.resize(frame, (96, 54), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        diff = 999.0 if prev_small is None else float(cv2.absdiff(gray, prev_small).mean())

        if diff >= args.diff_threshold:
            candidate_idx += 1
            seconds = frame_idx / fps
            resized = resize_keep_aspect(frame, args.width)
            path = frames_dir / f"frame_{candidate_idx:03d}_{seconds:07.2f}s.jpg"
            cv2.imwrite(str(path), resized, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
            rows.append({"id": f"K{candidate_idx:02d}", "time": timestamp(seconds), "seconds": f"{seconds:.2f}", "path": str(path), "diff": f"{diff:.2f}"})
            prev_small = gray

        if len(rows) >= args.max_frames:
            break
        frame_idx += step
        if duration and frame_idx / fps > duration:
            break

    cap.release()

    if not rows:
        raise SystemExit("No frames kept. Lower --diff-threshold or --every-sec.")

    manifest = out / "smart_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "time", "seconds", "path", "diff"])
        writer.writeheader()
        writer.writerows(rows)

    contact_sheet = out / "smart_contact_sheet.jpg"
    save_contact_sheet(rows, contact_sheet)

    print(f"Frames: {len(rows)}")
    print(f"Manifest: {manifest}")
    print(f"Contact sheet: {contact_sheet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
