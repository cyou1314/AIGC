#!/usr/bin/env python3
"""Shot-oriented sampler for AIGC manga/drama video analysis.

Uses OpenCV to find visual change points, exports start/mid/end frames for each
shot, and creates a contact sheet plus CSV manifest. It is intentionally fast
and conservative: the output is a working index for deeper visual reasoning,
not a perfect editorial EDL.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class Segment:
    start_frame: int
    end_frame: int
    score: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect rough shots and export keyframes.")
    parser.add_argument("video", help="Input video path")
    parser.add_argument("--out", default=None, help="Output folder")
    parser.add_argument("--scan-fps", type=float, default=2.0, help="Frames per second used for cut scanning")
    parser.add_argument("--threshold", type=float, default=0.38, help="Histogram distance threshold for cuts")
    parser.add_argument("--min-shot-sec", type=float, default=0.7, help="Minimum shot duration")
    parser.add_argument("--max-shots", type=int, default=24, help="Maximum detected shots to keep")
    parser.add_argument("--width", type=int, default=768, help="Exported keyframe width")
    return parser.parse_args()


def timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = seconds - minutes * 60
    return f"{minutes:02d}:{secs:05.2f}"


def read_frame(cap: cv2.VideoCapture, frame_index: int):
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, int(frame_index)))
    ok, frame = cap.read()
    if not ok:
        return None
    return frame


def frame_hist(frame) -> np.ndarray:
    small = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
    cv2.normalize(hist, hist)
    return hist


def resize_keep_aspect(frame, width: int):
    h, w = frame.shape[:2]
    scale = width / float(w)
    return cv2.resize(frame, (width, max(1, int(h * scale))), interpolation=cv2.INTER_AREA)


def detect_segments(cap: cv2.VideoCapture, fps: float, frame_count: int, args: argparse.Namespace) -> list[Segment]:
    step = max(1, int(fps / args.scan_fps))
    min_len = max(1, int(args.min_shot_sec * fps))
    cuts: list[tuple[int, float]] = []
    prev_hist = None

    for frame_idx in range(0, frame_count, step):
        frame = read_frame(cap, frame_idx)
        if frame is None:
            continue
        hist = frame_hist(frame)
        if prev_hist is not None:
            score = float(cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA))
            if score >= args.threshold:
                if not cuts or frame_idx - cuts[-1][0] >= min_len:
                    cuts.append((frame_idx, score))
        prev_hist = hist

    boundaries = [0] + [idx for idx, _ in cuts] + [max(0, frame_count - 1)]
    segments: list[Segment] = []
    for i in range(len(boundaries) - 1):
        start = boundaries[i]
        end = max(start, boundaries[i + 1] - 1)
        if end - start < min_len and segments:
            segments[-1].end_frame = end
            continue
        score = cuts[i - 1][1] if i > 0 and i - 1 < len(cuts) else 0.0
        segments.append(Segment(start, end, score))

    if len(segments) > args.max_shots:
        # Keep evenly spaced segments so the first pass covers the whole video.
        indexes = sorted({round(i * (len(segments) - 1) / (args.max_shots - 1)) for i in range(args.max_shots)})
        segments = [segments[i] for i in indexes]
    return segments


def export_frame(cap: cv2.VideoCapture, frame_idx: int, output: Path, width: int) -> bool:
    frame = read_frame(cap, frame_idx)
    if frame is None:
        return False
    resized = resize_keep_aspect(frame, width)
    return bool(cv2.imwrite(str(output), resized, [int(cv2.IMWRITE_JPEG_QUALITY), 90]))


def make_contact_sheet(image_paths: list[Path], labels: list[str], output: Path) -> None:
    images = [Image.open(path).convert("RGB") for path in image_paths]
    thumb_w = 220
    thumb_h = 140
    label_h = 30
    cols = min(3, len(images))
    rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, (image, label) in enumerate(zip(images, labels)):
        image.thumbnail((thumb_w, thumb_h))
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(image, (x + (thumb_w - image.width) // 2, y))
        draw.text((x + 6, y + thumb_h + 6), label[:36], fill="black", font=font)
    sheet.save(output, quality=90)


def main() -> int:
    args = parse_args()
    video = Path(args.video).expanduser().resolve()
    if not video.exists():
        raise SystemExit(f"Video not found: {video}")

    out = Path(args.out).expanduser().absolute() if args.out else video.with_suffix("")
    if out.exists() or out.is_symlink():
        raise SystemExit("Output folder already exists; select a new folder to preserve prior files.")
    out.mkdir(parents=True, exist_ok=False)
    frames_dir = out / "shot_frames"
    frames_dir.mkdir()

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {video}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if frame_count <= 0:
        raise SystemExit("Video has no readable frames.")

    segments = detect_segments(cap, fps, frame_count, args)
    rows: list[dict[str, str]] = []
    sheet_paths: list[Path] = []
    sheet_labels: list[str] = []

    for shot_idx, segment in enumerate(segments, start=1):
        points = {
            "start": segment.start_frame,
            "mid": (segment.start_frame + segment.end_frame) // 2,
            "end": segment.end_frame,
        }
        for phase, frame_idx in points.items():
            seconds = frame_idx / fps
            frame_path = frames_dir / f"S{shot_idx:02d}_{phase}_{seconds:07.2f}s.jpg"
            if export_frame(cap, frame_idx, frame_path, args.width):
                rows.append(
                    {
                        "shot": f"S{shot_idx:02d}",
                        "phase": phase,
                        "time": timestamp(seconds),
                        "seconds": f"{seconds:.2f}",
                        "frame": str(frame_path),
                        "change_score": f"{segment.score:.3f}",
                    }
                )
                sheet_paths.append(frame_path)
                sheet_labels.append(f"S{shot_idx:02d} {phase} {timestamp(seconds)}")

    cap.release()

    manifest = out / "shot_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["shot", "phase", "time", "seconds", "frame", "change_score"])
        writer.writeheader()
        writer.writerows(rows)

    if sheet_paths:
        make_contact_sheet(sheet_paths, sheet_labels, out / "shot_contact_sheet.jpg")

    print(f"Shots: {len(segments)}")
    print(f"Frames: {len(rows)}")
    print(f"Manifest: {manifest}")
    print(f"Contact sheet: {out / 'shot_contact_sheet.jpg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
