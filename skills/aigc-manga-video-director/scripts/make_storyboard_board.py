#!/usr/bin/env python3
"""Create a simple HTML storyboard board from a CSV shot list."""

from __future__ import annotations

import argparse
import csv
import html
import re
from pathlib import Path


FIELDS = [
    "shot",
    "image",
    "ratio",
    "duration",
    "visual",
    "action",
    "dialogue",
    "camera",
    "composition",
    "lighting",
    "image_prompt",
    "video_prompt",
    "continuity",
    "production_note",
]

MAX_ASPECT_RATIO = 2.5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an HTML storyboard board from CSV.")
    parser.add_argument("csv_path", help="Storyboard CSV path")
    parser.add_argument("--out", default=None, help="Output HTML path")
    parser.add_argument("--title", default="Storyboard Board", help="Board title")
    return parser.parse_args()


def esc(value: str | None) -> str:
    return html.escape(value or "")


def parse_ratio(value: str | None, shot: str) -> tuple[str, str]:
    raw = (value or "9:16").strip()
    normalized = raw.lower().replace(" ", "")
    parts = re.split(r"[:/x]", normalized)
    try:
        if len(parts) == 2:
            width = float(parts[0])
            height = float(parts[1])
        elif len(parts) == 1:
            width = float(parts[0])
            height = 1.0
        else:
            raise ValueError
    except ValueError as exc:
        raise SystemExit(f"Invalid ratio for {shot or 'unknown shot'}: {raw}") from exc

    if width <= 0 or height <= 0:
        raise SystemExit(f"Invalid ratio for {shot or 'unknown shot'}: {raw}")

    long_short = max(width / height, height / width)
    if long_short > MAX_ASPECT_RATIO:
        raise SystemExit(
            f"Aspect ratio too extreme for {shot or 'unknown shot'}: {raw}. "
            f"Use long side / short side <= {MAX_ASPECT_RATIO}."
        )

    return f"{width:g} / {height:g}", raw


def normalize_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for raw in reader:
            row = {field: (raw.get(field) or "").strip() for field in FIELDS}
            rows.append(row)
        return rows


def image_html(row: dict[str, str], base: Path) -> str:
    image = row.get("image", "")
    ratio_css, _ = parse_ratio(row.get("ratio"), row.get("shot", ""))
    if image:
        path = Path(image)
        src = path if path.is_absolute() else base / path
        return f'<div class="frame" style="aspect-ratio:{ratio_css}"><img src="{esc(src.as_posix())}" alt="{esc(row.get("shot"))}"></div>'
    return f'<div class="frame placeholder" style="aspect-ratio:{ratio_css}">IMAGE</div>'


def render(rows: list[dict[str, str]], title: str, base: Path) -> str:
    cards = []
    for row in rows:
        _, ratio_label = parse_ratio(row.get("ratio"), row.get("shot", ""))
        image_prompt_html = ""
        if row.get("image_prompt"):
            image_prompt_html = f'  <section><h3>生图提示词</h3><p>{esc(row["image_prompt"])}</p></section>\n'
        cards.append(
            f"""
<article class="card">
  <header><strong>{esc(row['shot'])}</strong><span>{esc(row['duration'])}</span><em>{esc(ratio_label)}</em></header>
  {image_html(row, base)}
  <section><h3>画面</h3><p>{esc(row['visual'])}</p></section>
  <section><h3>动作/台词</h3><p>{esc(row['action'])}</p><p class="dialogue">{esc(row['dialogue'])}</p></section>
  <section><h3>镜头/构图</h3><p>{esc(row['camera'])}</p><p>{esc(row['composition'])}</p></section>
  <section><h3>光影</h3><p>{esc(row['lighting'])}</p></section>
{image_prompt_html.rstrip()}
  <section><h3>视频提示词</h3><p>{esc(row['video_prompt'])}</p></section>
  <section><h3>连续性/制作</h3><p>{esc(row['continuity'])}</p><p>{esc(row['production_note'])}</p></section>
</article>"""
        )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>
body {{ margin: 0; font-family: Arial, "Microsoft YaHei", sans-serif; background: #f4f2ee; color: #1f2328; }}
main {{ max-width: 1440px; margin: 0 auto; padding: 28px; }}
h1 {{ margin: 0 0 20px; font-size: 28px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }}
.card {{ background: #fff; border: 1px solid #d8d4cc; border-radius: 8px; overflow: hidden; }}
header {{ display: flex; gap: 10px; align-items: center; justify-content: space-between; padding: 10px 12px; background: #20242a; color: #fff; }}
header strong {{ font-size: 16px; }}
header span, header em {{ font-size: 12px; opacity: .85; font-style: normal; }}
.frame {{ display: grid; place-items: center; background: #d9d9d9; overflow: hidden; }}
.frame img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.placeholder {{ color: #777; font-size: 22px; letter-spacing: 2px; }}
section {{ padding: 10px 12px; border-top: 1px solid #eee; }}
h3 {{ margin: 0 0 6px; font-size: 13px; color: #5b5f66; }}
p {{ margin: 0 0 6px; font-size: 13px; line-height: 1.45; white-space: pre-wrap; }}
.dialogue {{ color: #8a3d20; }}
</style>
</head>
<body>
<main>
<h1>{esc(title)}</h1>
<div class="grid">
{''.join(cards)}
</div>
</main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv_path).expanduser().resolve()
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")
    out = Path(args.out).expanduser().resolve() if args.out else csv_path.with_suffix(".html")
    rows = normalize_rows(csv_path)
    out.write_text(render(rows, args.title, csv_path.parent), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
