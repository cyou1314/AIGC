#!/usr/bin/env python3
"""Fast video frame sampler for AIGC manga/drama analysis.

Requires ffmpeg in PATH. Produces:
- sampled JPG frames
- manifest.csv with timestamps and frame paths
- contact_sheet.jpg for quick visual indexing
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample representative video frames quickly.")
    parser.add_argument("video", help="Input video path")
    parser.add_argument("--out", default=None, help="Output folder")
    parser.add_argument("--fps", type=float, default=0.25, help="Fixed sampling FPS for fallback mode")
    parser.add_argument("--width", type=int, default=640, help="Output frame width")
    parser.add_argument("--max-frames", type=int, default=24, help="Maximum frames kept in manifest/contact sheet")
    parser.add_argument("--scene-threshold", type=float, default=0.32, help="ffmpeg scene threshold")
    parser.add_argument("--mode", choices=["scene", "fixed"], default="scene", help="Sampling mode")
    return parser.parse_args()


def require_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        configured = os.environ.get('AIGC_FFMPEG')
        if configured and Path(configured).is_file():
            ffmpeg = configured
    if not ffmpeg:
        raise SystemExit(
            "ffmpeg was not found in PATH. Install ffmpeg or provide pre-extracted screenshots/keyframes."
        )
    return ffmpeg


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or "ffmpeg failed")


def sample_frames(ffmpeg: str, video: Path, frames_dir: Path, args: argparse.Namespace) -> None:
    frames_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(frames_dir / "frame_%05d.jpg")
    scale = f"scale={args.width}:-2"
    if args.mode == "scene":
        vf = f"select='gt(scene,{args.scene_threshold})',{scale},showinfo"
        cmd = [
            ffmpeg,
            "-hide_banner",
            "-y",
            "-i",
            str(video),
            "-vf",
            vf,
            "-vsync",
            "vfr",
            "-q:v",
            "3",
            pattern,
        ]
    else:
        vf = f"fps={args.fps},{scale}"
        cmd = [
            ffmpeg,
            "-hide_banner",
            "-y",
            "-i",
            str(video),
            "-vf",
            vf,
            "-q:v",
            "3",
            pattern,
        ]
    run(cmd)


def trim_frames(frames: list[Path], max_frames: int) -> list[Path]:
    if len(frames) <= max_frames:
        return frames
    keep_indexes = {
        round(i * (len(frames) - 1) / (max_frames - 1)) for i in range(max_frames)
    }
    keep = [frame for idx, frame in enumerate(frames) if idx in keep_indexes]
    for idx, frame in enumerate(frames):
        if idx not in keep_indexes:
            frame.unlink(missing_ok=True)
    return keep


def timestamp_for(index: int, fps: float) -> str:
    seconds = index / fps if fps > 0 else 0
    minutes = int(seconds // 60)
    secs = seconds - minutes * 60
    return f"{minutes:02d}:{secs:05.2f}"


def write_manifest(frames: list[Path], manifest: Path, fps: float, mode: str) -> None:
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["shot_hint", "timestamp_hint", "frame_path", "sampling_mode"])
        for idx, frame in enumerate(frames, start=1):
            writer.writerow([f"K{idx:02d}", timestamp_for(idx - 1, fps), str(frame), mode])


def make_contact_sheet(frames: list[Path], output: Path) -> None:
    if not frames:
        raise SystemExit("No frames were extracted. Try --mode fixed or lower --scene-threshold.")
    images = [Image.open(frame).convert("RGB") for frame in frames]
    thumb_w = 240
    thumb_h = 150
    label_h = 26
    cols = min(4, len(images))
    rows = math.ceil(len(images) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, (frame, image) in enumerate(zip(frames, images), start=1):
        image.thumbnail((thumb_w, thumb_h))
        x = ((idx - 1) % cols) * thumb_w
        y = ((idx - 1) // cols) * (thumb_h + label_h)
        paste_x = x + (thumb_w - image.width) // 2
        sheet.paste(image, (paste_x, y))
        draw.text((x + 6, y + thumb_h + 6), f"K{idx:02d}  {frame.name}", fill="black", font=font)
    sheet.save(output, quality=90)


def main() -> int:
    args = parse_args()
    ffmpeg = require_ffmpeg()
    video = Path(args.video).expanduser().resolve()
    if not video.exists():
        raise SystemExit(f"Video not found: {video}")
    out = Path(args.out).expanduser().resolve() if args.out else video.with_suffix("")
    frames_dir = out / "frames"
    out.mkdir(parents=True, exist_ok=True)
    sample_frames(ffmpeg, video, frames_dir, args)
    frames = sorted(frames_dir.glob("frame_*.jpg"))
    frames = trim_frames(frames, args.max_frames)
    write_manifest(frames, out / "manifest.csv", args.fps, args.mode)
    make_contact_sheet(frames, out / "contact_sheet.jpg")
    print(f"Frames: {len(frames)}")
    print(f"Manifest: {out / 'manifest.csv'}")
    print(f"Contact sheet: {out / 'contact_sheet.jpg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
