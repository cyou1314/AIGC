#!/usr/bin/env python3
"""Build a structured prompt brief from transcript text and emotion notes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from textwrap import shorten


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def summarize(text: str, width: int = 420) -> str:
    compact = " ".join(text.split())
    return shorten(compact, width=width, placeholder="...")


def build_brief(args: argparse.Namespace) -> dict:
    transcript = read_text(args.transcript)
    medium = args.medium
    language = args.language
    emotion = args.emotion or "unspecified; infer cautiously from transcript and available audio cues"
    style = args.style or "match the user's requested style"

    zh = language == "zh"

    if medium == "video" and zh:
        final_prompt = (
            f"根据这段音频内容生成视频提示词：{summarize(transcript)} "
            f"情绪弧线是：{emotion}。将情绪融合进节奏、镜头运动、光线、人物表情、"
            f"肢体动作和声音氛围中。视觉风格：{style}。"
        )
    elif medium == "image" and zh:
        final_prompt = (
            f"根据这段音频内容生成图像提示词：{summarize(transcript)} "
            f"把情绪转化为可见的表情、姿态和环境氛围：{emotion}。"
            f"视觉风格：{style}。包含主体、场景、动作、光线、构图和避免项。"
        )
    elif zh:
        final_prompt = (
            f"将这段音频内容转化为生成提示词：{summarize(transcript)} "
            f"把情绪线索（{emotion}）融合进主体、场景、动作、氛围、节奏和风格。"
            f"视觉风格：{style}。"
        )
    elif medium == "video":
        final_prompt = (
            f"Create a video prompt based on this audio content: {summarize(transcript)} "
            f"The emotional arc is {emotion}. Use pacing, camera movement, lighting, "
            f"character expression, and sound atmosphere to make the emotion visible. "
            f"Style: {style}."
        )
    elif medium == "image":
        final_prompt = (
            f"Create an image prompt based on this audio content: {summarize(transcript)} "
            f"Show the emotion as visible behavior and atmosphere: {emotion}. "
            f"Style: {style}. Include subject, setting, expression, lighting, composition, "
            f"and negative constraints."
        )
    else:
        final_prompt = (
            f"Convert this audio content into a generation prompt: {summarize(transcript)} "
            f"Fuse the emotional cues ({emotion}) into subject, setting, action, atmosphere, "
            f"rhythm, and style. Style: {style}."
        )

    headings = {
        "zh": {
            "summary": "转录摘要",
            "emotion": "情绪与声音线索",
            "materials": "提示词素材",
            "prompt": "最终提示词",
        },
        "en": {
            "summary": "Transcript Summary",
            "emotion": "Emotion and Sound Cues",
            "materials": "Prompt Materials",
            "prompt": "Final Prompt",
        },
    }.get(language, {})

    return {
        "language": language,
        "medium": medium,
        "style": style,
        "transcript_summary": summarize(transcript),
        "emotion_notes": emotion,
        "prompt_materials": {
            "subject": "",
            "setting": "",
            "action": "",
            "emotion_expression": emotion,
            "visual_style": style,
            "camera_or_composition": "",
            "sound_atmosphere": "",
            "avoid": "",
        },
        "final_prompt": final_prompt,
        "_headings": headings,
    }


def to_markdown(brief: dict) -> str:
    h = brief["_headings"]
    materials = brief["prompt_materials"]
    zh = brief["language"] == "zh"
    labels = {
        "primary": "主要线索" if zh else "Primary notes",
        "confirmed": "可确认的声音线索" if zh else "Confirmed audio cues",
        "inferred": "仅从文本推断" if zh else "Transcript-only inference",
        "subject": "人物/主体" if zh else "Subject",
        "setting": "场景" if zh else "Setting",
        "action": "动作" if zh else "Action",
        "emotion": "情绪表现" if zh else "Emotion expression",
        "style": "视觉风格" if zh else "Visual style",
        "camera": "镜头/构图" if zh else "Camera/composition",
        "sound": "声音氛围" if zh else "Sound atmosphere",
        "avoid": "避免" if zh else "Avoid",
    }
    return "\n".join(
        [
            f"## {h['summary']}",
            brief["transcript_summary"],
            "",
            f"## {h['emotion']}",
            f"- {labels['primary']}: {brief['emotion_notes']}",
            f"- {labels['confirmed']}: ",
            f"- {labels['inferred']}: ",
            "",
            f"## {h['materials']}",
            f"- {labels['subject']}: {materials['subject']}",
            f"- {labels['setting']}: {materials['setting']}",
            f"- {labels['action']}: {materials['action']}",
            f"- {labels['emotion']}: {materials['emotion_expression']}",
            f"- {labels['style']}: {materials['visual_style']}",
            f"- {labels['camera']}: {materials['camera_or_composition']}",
            f"- {labels['sound']}: {materials['sound_atmosphere']}",
            f"- {labels['avoid']}: {materials['avoid']}",
            "",
            f"## {h['prompt']}",
            brief["final_prompt"],
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path, help="UTF-8 transcript text file")
    parser.add_argument("--medium", choices=["image", "video", "generic"], default="video")
    parser.add_argument("--emotion", default="", help="Emotion/prosody notes to fuse into the prompt")
    parser.add_argument("--style", default="", help="Visual or generation style")
    parser.add_argument("--language", choices=["zh", "en"], default="zh")
    parser.add_argument("--json", action="store_true", help="Write JSON instead of Markdown")
    parser.add_argument("--out", type=Path, help="Output path; prints to stdout when omitted")
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    brief = build_brief(args)
    output_brief = dict(brief)
    output_brief.pop("_headings", None)

    if args.json:
        output = json.dumps(output_brief, ensure_ascii=False, indent=2) + "\n"
    else:
        output = to_markdown(brief)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
