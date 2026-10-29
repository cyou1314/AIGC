#!/usr/bin/env python3
"""Deterministic checks for structured Seedance prompt-review ledgers.

This helper deliberately does not infer cinematic meaning from raw prose. A model or
human first extracts semantic facts into the JSON ledger; these checks then enforce
explicit speaker, staging, continuity, and minimal-difference invariants.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


DEFINITE = "确定冲突"
JUDGMENT = "需要人工判断"
SUGGESTION = "建议优化"
NOT_TRIGGERED = "未触发此检查器"
PASS = "通过"

FRONT_VIEWS = {"front", "three_quarter", "正脸", "四分之三正脸"}
BACK_VIEWS = {"back", "back_of_head", "shoulder", "背影", "后脑", "肩部"}
OFFSCREEN_MODES = {"OS", "VO", "telephone", "broadcast", "narration", "电话音", "广播", "旁白"}
REVERSE_TRANSITIONS = {"cut", "cut_to_reverse", "cut_to_new_angle", "切镜", "切至反打镜头"}
NO_DIALOGUE_KINDS = {"action", "product", "scenery", "vfx", "动作", "产品", "风景", "纯特效"}
AXIS_UNKNOWN = "需要人工判断：现有提示词不足以确定摄影机是否跨越180度轴线。"
AXIS_REBUILDS = {"camera_crossing", "character_reblocking", "on_axis_neutral", "wide_reestablish", "insert_reestablish", "intentional_cross"}


def axis_reset_is_valid(reset: dict[str, Any] | None) -> bool:
    """Validate an extracted bridge declaration, not the underlying film geometry."""
    reset = reset or {}
    return (reset.get("kind") in AXIS_REBUILDS
            and bool(reset.get("evidence"))
            and reset.get("spatial_relation_established") is True
            and (reset.get("kind") != "intentional_cross" or reset.get("user_requested") is True))


@dataclass(frozen=True)
class Issue:
    category: str
    code: str
    message: str
    time_range: str = "全局"


def _issue(category: str, code: str, message: str, segment: dict[str, Any] | None = None) -> Issue:
    return Issue(category, code, message, str((segment or {}).get("time_range", "全局")))


def dialogue_route(context: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return whether to load the full dialogue-staging module and why."""
    reasons: list[str] = []
    kind = str(context.get("prompt_kind", "")).lower()
    has_dialogue = bool(context.get("has_explicit_dialogue"))
    visible_count = int(context.get("visible_character_count", 0) or 0)

    if kind in NO_DIALOGUE_KINDS and not has_dialogue:
        return False, reasons
    if context.get("single_person_monologue") and visible_count <= 1:
        return False, reasons
    if context.get("only_offscreen_or_voiceover_dialogue"):
        return False, reasons
    if visible_count >= 2 and has_dialogue:
        reasons.append("同场两名或以上可见角色并有明确台词")
    if context.get("speaker_switches_between_segments"):
        reasons.append("相邻时间段说话者切换")
    if context.get("uses_shot_relation_staging"):
        reasons.append("出现越肩/反打/前景背影/对视等镜头关系")
    if context.get("user_reported_staging_error"):
        reasons.append("用户报告说话者、口型、正背面或站位错误")
    return bool(reasons), reasons


def legacy_15s_split_is_invalid(model_line: str, duration_seconds: float) -> bool:
    """Flag only the obsolete reasoning 'over 15 seconds must split' for 2.5.

    This does not assert that a particular account or surface exposes a duration.
    It only prevents a 2.0 ceiling from being used as the reason for splitting.
    """
    normalized = model_line.strip().lower().replace("seedance", "").replace(" ", "")
    return normalized in {"2.5", "25"} and 15 < duration_seconds <= 30


def _visible_non_speakers(segment: dict[str, Any], speaker: str) -> set[str]:
    return {str(name) for name in segment.get("visible_characters", []) if str(name) != speaker}


def _basic_offscreen_checks(segments: Iterable[dict[str, Any]]) -> list[Issue]:
    issues: list[Issue] = []
    for segment in segments:
        speaker = str(segment.get("speaker", ""))
        if not speaker:
            continue
        if segment.get("visible_characters") is None:
            issues.append(_issue(JUDGMENT, "VISIBILITY_UNSPECIFIED", f"{speaker} 的可见人物清单未提供，不能确认是否画外。", segment))
            continue
        visible = {str(name) for name in segment.get("visible_characters", [])}
        mode = str(segment.get("dialogue_mode", ""))
        if speaker not in visible and mode not in OFFSCREEN_MODES:
            issues.append(_issue(DEFINITE, "OFFSCREEN_WITHOUT_LABEL", f"{speaker} 不在画面内，但台词未标记 OS/VO/电话音/广播/旁白。", segment))
    return issues


def audit_dialogue_ledger(payload: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("context", {})
    segments = payload.get("segments", [])
    triggered, reasons = dialogue_route(context)
    issues = _basic_offscreen_checks(segments)

    if not triggered:
        status = DEFINITE if issues else NOT_TRIGGERED
        return {"status": status, "triggered": False, "trigger_reasons": reasons, "issues": [asdict(i) for i in issues]}

    fixed_wide = bool(context.get("fixed_wide_two_shot"))
    position_locks = {str(k): str(v) for k, v in context.get("position_locks", {}).items()}
    facing_locks = {str(k): str(v) for k, v in context.get("facing_locks", {}).items()}
    wardrobe_locks = {str(k): str(v) for k, v in context.get("wardrobe_locks", {}).items()}
    anchor_positions: dict[str, str] = {}
    anchor_facing: dict[str, str] = {}
    prior_onscreen_speaker = ""

    for segment in segments:
        visible = [str(name) for name in (segment.get("visible_characters") or [])]
        speaker = str(segment.get("speaker", ""))
        mode = str(segment.get("dialogue_mode", "onscreen"))
        onscreen = bool(speaker) and mode not in OFFSCREEN_MODES
        relation = str(segment.get("camera_relation", ""))
        positions = {str(k): str(v) for k, v in segment.get("positions", {}).items()}
        facing = {str(k): str(v) for k, v in segment.get("facing", {}).items()}
        wardrobe = {str(k): str(v) for k, v in segment.get("wardrobe", {}).items()}
        rebuilt = axis_reset_is_valid(segment.get("axis_reset"))

        for name, side in positions.items():
            if name in position_locks and position_locks[name] != side:
                issues.append(_issue(DEFINITE, "LOCKED_SCREEN_SIDE", f"{name} 应保持 {position_locks[name]} 侧，当前为 {side} 侧。", segment))
            if name in anchor_positions and anchor_positions[name] != side and not rebuilt:
                certain = segment.get("screen_mapping_preserved") is True or name in position_locks
                issues.append(_issue(DEFINITE if certain else JUDGMENT, "SCREEN_SIDE_FLIP", f"{name} 从 {anchor_positions[name]} 侧变为 {side} 侧，需结合机位确认是否人物换位。", segment))
            anchor_positions[name] = side
        for name, direction in facing.items():
            if name in facing_locks and facing_locks[name] != direction:
                issues.append(_issue(DEFINITE, "LOCKED_FACING", f"{name} 应保持面向 {facing_locks[name]}，当前为 {direction}。", segment))
            if name in anchor_facing and anchor_facing[name] != direction and not rebuilt:
                certain = segment.get("screen_mapping_preserved") is True or name in facing_locks
                issues.append(_issue(DEFINITE if certain else JUDGMENT, "FACING_FLIP", f"{name} 朝向从 {anchor_facing[name]} 变为 {direction}，需区分转身与机位变化。", segment))
            anchor_facing[name] = direction
        for name, expected_wardrobe in wardrobe_locks.items():
            if name in visible and wardrobe.get(name) != expected_wardrobe:
                issues.append(_issue(DEFINITE if wardrobe.get(name) else JUDGMENT, "WARDROBE_LOCK", f"{name} 的服装应保持 {expected_wardrobe}，当前为 {wardrobe.get(name, '未说明')}。", segment))

        if onscreen:
            if speaker not in visible:
                continue
            primary_face = str(segment.get("primary_face", ""))
            if not fixed_wide and primary_face and primary_face != speaker:
                issues.append(_issue(DEFINITE, "WRONG_PRIMARY_FACE", f"台词属于 {speaker}，但主要展示 {primary_face} 的正脸。", segment))
            if not fixed_wide and not primary_face:
                issues.append(_issue(JUDGMENT, "PRIMARY_FACE_UNSPECIFIED", f"{speaker} 说话时未说明主要可读正脸。", segment))

            face_view = str((segment.get("face_views") or {}).get(speaker) or "")
            if not fixed_wide and face_view not in FRONT_VIEWS:
                issues.append(_issue(DEFINITE if face_view else JUDGMENT, "SPEAKER_FACE_NOT_READABLE", f"{speaker} 说话时未锁定正脸或四分之三正脸。", segment))
            if not fixed_wide and segment.get("mouth_unobstructed") is not True:
                issues.append(_issue(DEFINITE if segment.get("mouth_unobstructed") is False else JUDGMENT, "MOUTH_VISIBILITY_UNCLEAR", f"{speaker} 的嘴部无遮挡状态未满足或未明确。", segment))

            if relation in {"over_shoulder", "reverse_over_shoulder", "越肩", "反打越肩"}:
                foreground = str(segment.get("foreground_character", ""))
                foreground_view = str(segment.get("foreground_view", ""))
                expected_listeners = _visible_non_speakers(segment, speaker)
                if not foreground or foreground not in expected_listeners:
                    issues.append(_issue(DEFINITE if foreground else JUDGMENT, "OTS_FOREGROUND_MISSING", "越肩/反打镜头未明确由非说话者占据前景。", segment))
                if foreground_view not in BACK_VIEWS:
                    issues.append(_issue(DEFINITE if foreground_view else JUDGMENT, "OTS_FOREGROUND_NOT_BACK", "越肩/反打镜头未明确前景人物为背影、后脑或肩部。", segment))

            lip_sync = {str(name) for name in (segment.get("lip_sync_allowed") or [])}
            if lip_sync != {speaker}:
                issues.append(_issue(DEFINITE if segment.get("lip_sync_allowed") is not None else JUDGMENT, "LIP_SYNC_OWNER", f"口型归属应且只能是 {speaker}，当前为 {sorted(lip_sync)}。", segment))
            silent = {str(name) for name in (segment.get("silent_characters") or [])}
            missing_silent = _visible_non_speakers(segment, speaker) - silent
            if missing_silent:
                issues.append(_issue(SUGGESTION, "LISTENER_SILENCE_MISSING", f"可见非说话者未明确保持沉默：{', '.join(sorted(missing_silent))}。", segment))

            readable_fronts = {str(name) for name in segment.get("readable_front_faces", [])}
            if len(readable_fronts) > 1 and lip_sync != {speaker}:
                issues.append(_issue(DEFINITE if "lip_sync_allowed" in segment else JUDGMENT, "TWO_FACES_AMBIGUOUS", "两人均露出可读正脸，但没有唯一口型归属。", segment))

            if segment.get("axis_180_maintained") is False and not rebuilt:
                issues.append(_issue(DEFINITE, "AXIS_BROKEN", "反打后未保持 180 度轴线。", segment))
            if relation in {"over_shoulder", "reverse_over_shoulder", "越肩", "反打越肩"} and segment.get("axis_180_maintained") is None and not rebuilt:
                issues.append(_issue(JUDGMENT, "AXIS_UNSPECIFIED", AXIS_UNKNOWN, segment))

            if prior_onscreen_speaker and prior_onscreen_speaker != speaker and not fixed_wide:
                transition = str(segment.get("camera_transition", ""))
                if transition not in REVERSE_TRANSITIONS:
                    issues.append(_issue(DEFINITE if transition == "focus_shift" else JUDGMENT, "SPEAKER_SWITCH_WITHOUT_CUT", f"说话者从 {prior_onscreen_speaker} 切换为 {speaker}，但未明确切镜或反打。", segment))
                elif relation in {"over_shoulder", "reverse_over_shoulder", "越肩", "反打越肩"} and transition not in {"cut_to_reverse", "切至反打镜头"}:
                    issues.append(_issue(JUDGMENT, "REVERSE_CUT_UNSPECIFIED", "过肩换人说话仅写切镜，未明确切至反打镜头。", segment))
            prior_onscreen_speaker = speaker

        turns = [str(name) for name in segment.get("speaker_turns", [])]
        if len(set(turns)) > 1 and not fixed_wide:
            transition = str(segment.get("camera_transition", ""))
            if transition not in REVERSE_TRANSITIONS:
                issues.append(_issue(DEFINITE, "MULTI_TURN_FOCUS_ONLY", "同一时间段换人说话，但只写焦点变化或未写切至反打机位。", segment))

    definite = any(i.category == DEFINITE for i in issues)
    judgment = any(i.category == JUDGMENT for i in issues)
    status = DEFINITE if definite else JUDGMENT if judgment else PASS
    return {"status": status, "triggered": True, "trigger_reasons": reasons, "issues": [asdict(i) for i in issues]}


def handoff_route(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    """Gate over extracted context; never scan prompt prose for cinematic meaning."""
    context = payload.get("context", {})
    previous = payload.get("previous_end") or {}
    following = payload.get("next_start") or {}
    if context.get("user_requested_spatial_check") or context.get("known_spatial_conflict"):
        return True, ["用户要求空间检查或已有空间冲突证据"]
    strong = [key for key in ("spatial_action", "continuous_action", "shot_relation", "explicit_screen_position") if context.get(key)]
    exemptions = ("independent_single", "pure_noncharacter", "unrelated_montage", "pure_audio",
                  "locked_fixed_wide_no_conflict", "clear_without_spatial_handoff")
    if any(context.get(key) for key in exemptions) and not strong:
        return False, []
    shared = set(previous.get("characters", {})) & set(following.get("characters", {}))
    reasons = strong + [key for key in ("live_dialogue", "speaker_change", "two_or_more_share_scene") if context.get(key)]
    if shared:
        reasons.append("相邻分镜具有共同人物")
    for state in (previous, following):
        if len(state.get("visible_characters", [])) >= 2:
            reasons.append("两名或以上人物共享画面")
            break
    if any(s.get("speaker") and s.get("dialogue_mode", "onscreen") not in OFFSCREEN_MODES for s in (previous, following)):
        reasons.append("存在现场对白")
    return bool(reasons), reasons


def _handoff_shape_error(payload: Any) -> str | None:
    """Reject malformed structured input without treating it as film evidence."""
    if not isinstance(payload, dict):
        return "ledger 必须是 JSON 对象。"
    for key in ("context", "previous_end", "next_start", "bridge", "handoff_out", "receiver_in"):
        if key in payload and not isinstance(payload[key], dict):
            return f"{key} 必须是对象；标量未知值可用 null。"
    for key in ("previous_end", "next_start"):
        state = payload.get(key, {})
        for field in ("characters", "props", "dialogue"):
            if field in state and not isinstance(state[field], dict):
                return f"{key}.{field} 必须是对象。"
        for field in ("visible_characters", "unknowns", "noncritical_unknowns"):
            if field in state and not isinstance(state[field], list):
                return f"{key}.{field} 必须是列表。"
        if state.get("axis") is not None and not isinstance(state["axis"], dict):
            return f"{key}.axis 必须是对象或 null。"
        for field in ("characters", "props"):
            if any(not isinstance(item, dict) for item in state.get(field, {}).values()):
                return f"{key}.{field} 中每个条目必须是状态对象。"
    bridge = payload.get("bridge", {})
    if not isinstance(bridge.get("events", []), list) or any(not isinstance(e, dict) for e in bridge.get("events", [])):
        return "bridge.events 必须是事件对象列表。"
    if bridge.get("axis_reset") is not None and not isinstance(bridge["axis_reset"], dict):
        return "bridge.axis_reset 必须是对象或 null。"
    for key in ("continuous_time", "screen_mapping_preserved", "camera_changed"):
        if bridge.get(key) is not None and not isinstance(bridge[key], bool):
            return f"bridge.{key} 必须是布尔值或 null。"
    return None


def audit_handoff_ledger(payload: dict[str, Any]) -> dict[str, Any]:
    """Compare manually extracted canonical boundary states and their evidence."""
    shape_error = _handoff_shape_error(payload)
    if shape_error:
        return {"checker": "相邻分镜空间连续性检查", "triggered": False, "status": JUDGMENT, "conclusion": "需要补充信息",
                "issues": [{"category": JUDGMENT, "code": "LEDGER_INVALID", "time_range": "全局", "message": shape_error,
                            "previous_evidence": "未检查", "next_evidence": "未检查", "reason": shape_error,
                            "suggestion": "修正提取的 ledger 结构后重跑，不能以程序输入错误判定电影空间冲突。"}]}
    triggered, reasons = handoff_route(payload)
    previous, following = payload.get("previous_end") or {}, payload.get("next_start") or {}
    issues: list[dict[str, Any]] = []
    result = {"checker": "相邻分镜空间连续性检查", "triggered": triggered, "trigger_reasons": reasons,
              "previous_end": previous, "next_start": following, "issues": issues}
    if not triggered:
        return dict(result, status=NOT_TRIGGERED, conclusion="未触发", message="未触发相邻分镜空间连续性检查。")
    bridge = payload.get("bridge") or {}
    continuous = bridge.get("continuous_time") is True
    rebuilt = axis_reset_is_valid(bridge.get("axis_reset"))

    def emit(category: str, code: str, reason: str, suggestion: str,
             old: dict[str, Any] | None = None, new: dict[str, Any] | None = None) -> None:
        old_evidence = (old or {}).get("evidence") or previous.get("evidence")
        new_evidence = (new or {}).get("evidence") or following.get("evidence")
        if category == DEFINITE and not (old_evidence and new_evidence):
            category = JUDGMENT
        issues.append({"category": category, "code": code, "time_range": "上一分镜末镜 → 下一分镜首镜",
                       "previous_evidence": old_evidence or "未说明", "next_evidence": new_evidence or "未说明",
                       "message": reason, "reason": reason, "suggestion": suggestion})

    def event_explains(subject: str, field: str, old: Any, new: Any) -> bool:
        return any(e.get("subject") == subject and e.get("field") == field
                   and e.get("from") == old and e.get("to") == new and e.get("evidence")
                   for e in bridge.get("events", []))

    for label, state in (("上一分镜结束", previous), ("下一分镜开场", following)):
        if not state or not state.get("evidence"):
            emit(JUDGMENT, "BOUNDARY_EVIDENCE_MISSING", f"{label}状态或原文证据缺失。", "提供该边界镜头原文，不推测缺失状态。")
        if state.get("unknowns"):
            emit(JUDGMENT, "BOUNDARY_UNKNOWNS", f"{label}未知信息：{state['unknowns']}。", "补充影响交接判断的信息，或保留人工判断。")
        if not state.get("characters") and not state.get("props") and not payload.get("handoff_out"):
            emit(JUDGMENT, "BOUNDARY_STATE_MISSING", f"{label}没有可比较的结构化状态。", "先提取人物、道具或交接状态再运行检查。")
        for name, character in state.get("characters", {}).items():
            if not any(v is not None for k, v in character.items() if k != "evidence"):
                emit(JUDGMENT, "CHARACTER_STATE_MISSING", f"{label}的{name}只有名称，没有已提取状态。", "填写影响当前交接的状态，不能只列角色名就判通过。")

    old_axis, new_axis = previous.get("axis") or {}, following.get("axis") or {}
    axis_relevant = bool(old_axis or new_axis or payload.get("context", {}).get("live_dialogue")
                         or len(set(previous.get("characters", {})) | set(following.get("characters", {}))) >= 2)
    if axis_relevant:
        if not all((old_axis.get("id"), new_axis.get("id"), old_axis.get("side"), new_axis.get("side"))):
            emit(JUDGMENT, "AXIS_UNSPECIFIED", AXIS_UNKNOWN, "说明关系轴所属人物及摄影机所在侧；不由平视、仰拍或景别猜测。")
        elif old_axis["id"] != new_axis["id"] and not rebuilt:
            emit(JUDGMENT, "AXIS_REBUILD_UNCLEAR", "人物关系轴改变，但未交代新轴线的建立。", "补充新关系轴的可见建立过程或空间依据。")
        elif old_axis["side"] != new_axis["side"] and not rebuilt:
            category = JUDGMENT if "on_axis" in (old_axis["side"], new_axis["side"]) else DEFINITE
            emit(category, "AXIS_CROSSING", "摄影机位于已记录关系轴的不同侧，未提供合法空间桥接。", "保持下一镜在原轴线侧，或在权限内明确合法轴线重建。")
    if bridge.get("axis_reset") and not rebuilt:
        emit(JUDGMENT, "AXIS_RESET_UNSUPPORTED", "轴线重建声明缺少可见空间依据或用户有意越轴要求。", "说明跨轴过程、新位置或插入镜头后的空间重建，不能只写重置。")

    fields = {"screen_position": "SCREEN_POSITION", "depth": "DEPTH", "body_orientation": "BODY_ORIENTATION",
              "screen_facing": "SCREEN_FACING", "pose": "POSE", "motion_vector": "MOTION_VECTOR", "face_view": "FACE_VIEW"}
    projected = {"screen_position", "depth", "screen_facing", "face_view", "motion_vector"}
    for name in sorted(set(previous.get("characters", {})) & set(following.get("characters", {}))):
        old, new = previous["characters"][name], following["characters"][name]
        for field, code in fields.items():
            a, b = old.get(field), new.get(field)
            if a is not None and b is None and field not in projected:
                emit(JUDGMENT, code + "_UNKNOWN", f"{name} 的 {field} 在下一镜未确认。", "注明该身体状态是否继续保留，避免凭空假定。", old, new)
            if a is None or b is None or a == b or event_explains(name, field, a, b):
                continue
            if field in projected and rebuilt:
                continue
            if field in {"face_view", "depth"} and bridge.get("camera_changed") is True:
                continue
            certain = continuous and (field not in projected or bridge.get("screen_mapping_preserved") is True)
            if field == "face_view":
                certain = continuous and bridge.get("camera_changed") is False
            emit(DEFINITE if certain else JUDGMENT, code + "_CHANGE",
                 f"{name} 的 {field} 从 {a} 变为 {b}，无对应交接过程。",
                 "先区分构图变化与人物移动；必要时只调整下一镜开场继承状态。", old, new)
        for state in (old, new):
            target, required = state.get("gaze_target"), state.get("required_gaze_target")
            if required is not None and target != required:
                emit(DEFINITE if target is not None else JUDGMENT, "EYELINE_TARGET",
                     f"{name} 的视线目标 {target} 未匹配明确要求的 {required}。",
                     "明确看向正确对话对象及其高度；保留有意移开视线的动作。", old, new)
        end, start = old.get("action_end"), new.get("action_start")
        if end is not None and start is None:
            emit(JUDGMENT, "ACTION_RECEIVER_MISSING", f"{name} 的动作结束状态 {end} 未在下一开场确认。", "明确下一镜在新动作之前继承的状态。", old, new)
        elif end is not None and start != end and not event_explains(name, "action", end, start):
            emit(DEFINITE if continuous else JUDGMENT, "ACTION_HANDOFF", f"{name} 动作由 {end} 跳为 {start}，可能重复、跳过或中断。", "让下一镜从上一镜动作结果开始，或补明已有交接过程。", old, new)
        exit_edge, entry_edge = old.get("exit_edge"), new.get("entry_edge")
        if exit_edge in {"left", "right"} and entry_edge == exit_edge and not rebuilt and not event_explains(name, "entry_edge", exit_edge, entry_edge):
            emit(DEFINITE if continuous and bridge.get("screen_mapping_preserved") is True else JUDGMENT,
                 "EXIT_ENTRY_DIRECTION", f"{name} 从 {exit_edge} 出画后又从同侧入画；需核对是否意外折返。",
                 "沿同一方向移动通常从另一侧入画；转身、路径或机位改变须有依据。", old, new)

    for tag, old in previous.get("props", {}).items():
        new = following.get("props", {}).get(tag)
        if new is None:
            emit(JUDGMENT, "PROP_RECEIVER_MISSING", f"{tag} 的持有状态在下一镜未确认，不能视为消失。", "保留画外持有状态，不必强制道具入镜。", old)
            continue
        for field in ("holder", "hand", "state"):
            a, b = old.get(field), new.get(field)
            if a is None:
                continue
            if b is None:
                emit(JUDGMENT, "PROP_STATE_UNKNOWN", f"{tag} 的 {field} 未在下一镜确认。", "补明持有人、解剖学左右手及必要道具状态。", old, new)
            elif a != b and not event_explains(tag, field, a, b):
                emit(DEFINITE if continuous else JUDGMENT, "PROP_" + field.upper(), f"{tag} 的 {field} 从 {a} 变为 {b}，未交接。", "继承原持有状态或明确已有交接；合法跨轴不能解释换手。", old, new)

    for key, value in payload.get("handoff_out", {}).items():
        receiver = payload.get("receiver_in", {}).get(key)
        if value is not None and value != receiver and not event_explains(key, "handoff", value, receiver):
            emit(DEFINITE if receiver is not None and continuous else JUDGMENT, "KEY_STATE_HANDOFF",
                 f"关键状态 {key} 交出 {value}，接收为 {receiver}。", "下一镜开场继承该结束状态；未说明与明确相反分开处理。")
    if payload.get("next_transition") and payload.get("prev_transition") and payload["next_transition"] != payload["prev_transition"]:
        emit(JUDGMENT, "TRANSITION_MISMATCH", "两侧声明的剪辑交接关系不一致。", "核对入镜与出镜过渡是否描述同一交接。")

    rows = []
    for state in (previous, following):
        row = dict(state.get("dialogue") or {})
        if state.get("speaker"):
            row.update(speaker=state["speaker"], dialogue_mode=state.get("dialogue_mode", "onscreen"))
            row.setdefault("visible_characters", state.get("visible_characters", []))
            if rebuilt:
                row["axis_reset"] = bridge.get("axis_reset")
            rows.append(row)
    if rows:
        context = payload.get("context", {})
        # Geometry is handled above. Legacy row anchors must not independently overrule a legal reframe.
        for row in rows:
            row.pop("positions", None)
            row.pop("facing", None)
        dialogue = audit_dialogue_ledger({"context": {"has_explicit_dialogue": True,
            "visible_character_count": max(len(r.get("visible_characters", [])) for r in rows),
            "speaker_switches_between_segments": len({r["speaker"] for r in rows if r.get("dialogue_mode") not in OFFSCREEN_MODES}) > 1,
            "uses_shot_relation_staging": bool(context.get("shot_relation")),
            "fixed_wide_two_shot": bool(context.get("locked_fixed_wide_no_conflict"))}, "segments": rows})
        result["dialogue_triggered"] = dialogue["triggered"]
        for issue in dialogue["issues"]:
            if issue["code"] in {"AXIS_UNSPECIFIED", "AXIS_BROKEN"}:
                continue  # Boundary geometry above has the two quoted sources and legal bridge.
            emit(issue["category"], issue["code"], issue["message"], "按每句台词校正可见面孔、前景背影、唯一口型归属和明确反打；不改锁定台词。")
    status = DEFINITE if any(i["category"] == DEFINITE for i in issues) else JUDGMENT if any(i["category"] == JUDGMENT for i in issues) else PASS
    return dict(result, status=status, conclusion={DEFINITE: "存在确定冲突", JUDGMENT: "需要补充信息", PASS: "通过"}[status])


def verify_visual_only_revision(payload: dict[str, Any]) -> dict[str, Any]:
    """Check an extracted edit partition, not semantic classification of raw prose."""
    issues: list[Issue] = []
    required = ("previous_original", "previous_revised", "next_original", "next_revised")
    if any(not isinstance(payload.get(key), str) for key in required):
        return {"status": DEFINITE, "issues": [asdict(_issue(DEFINITE, "EDIT_INPUT_MISSING", "必须提供两份提示词的修改前后完整文本。"))]}
    if payload["previous_original"] != payload["previous_revised"]:
        issues.append(_issue(DEFINITE, "PREVIOUS_PROMPT_CHANGED", "上一分镜被改动。"))
    mode = payload.get("mode", "review-only")
    if mode != "visual-only-next":
        if payload["next_original"] != payload["next_revised"]:
            issues.append(_issue(DEFINITE, "REVISION_NOT_AUTHORIZED", "未明确授权只修改下一分镜画面，默认只检查。"))
    else:
        parts = payload.get("parts", [])
        if (not isinstance(parts, list) or not parts or any(not isinstance(p, dict) or p.get("kind") not in {"locked", "visual"}
                            or not isinstance(p.get("original"), str) or not isinstance(p.get("revised"), str) for p in parts)):
            issues.append(_issue(DEFINITE, "EDIT_PARTITION_INVALID", "需要完整、按原文顺序提取的 locked/visual 分区。"))
        else:
            if "".join(p["original"] for p in parts) != payload["next_original"] or "".join(p["revised"] for p in parts) != payload["next_revised"]:
                issues.append(_issue(DEFINITE, "EDIT_PARTITION_MISMATCH", "分区不能逐字重建修改前后完整提示词。"))
            if any(p["kind"] == "locked" and p["original"] != p["revised"] for p in parts):
                issues.append(_issue(DEFINITE, "LOCKED_PART_CHANGED", "锁定的台词、时间、角色、场景、道具或参考标签发生变化。"))
        tags = payload.get("reference_tags")
        if not isinstance(tags, list) or any(not isinstance(tag, str) or not tag for tag in tags):
            issues.append(_issue(DEFINITE, "TAG_INVENTORY_MISSING", "必须提供已提取的完整参考标签清单，无标签时用空列表。"))
            tags = []
        for tag in tags:
            if not tag or payload["next_original"].count(tag) != payload["next_revised"].count(tag):
                issues.append(_issue(DEFINITE, "REFERENCE_TAG_CHANGED", f"参考标签 {tag!r} 的原文或出现次数发生变化。"))
    return {"status": DEFINITE if issues else PASS, "issues": [asdict(i) for i in issues]}


def verify_minimal_difference(payload: dict[str, Any]) -> dict[str, Any]:
    original = str(payload.get("original", ""))
    revised = str(payload.get("revised", ""))
    expected = original
    issues: list[Issue] = []

    for index, item in enumerate(payload.get("allowed_replacements", []), start=1):
        old = str(item.get("old", ""))
        new = str(item.get("new", ""))
        count = int(item.get("count", 1))
        actual = expected.count(old)
        if not old or actual != count:
            issues.append(_issue(DEFINITE, "REPLACEMENT_SCOPE_INVALID", f"允许修改项 {index} 的原片段应出现 {count} 次，实际为 {actual} 次。"))
            continue
        expected = expected.replace(old, new, count)

    if expected != revised:
        diff = "\n".join(difflib.unified_diff(expected.splitlines(), revised.splitlines(), fromfile="expected", tofile="revised", lineterm=""))
        issues.append(_issue(DEFINITE, "OUTSIDE_SCOPE_CHANGED", "最终稿包含允许替换之外的变化。\n" + diff))

    return {"status": DEFINITE if issues else PASS, "issues": [asdict(i) for i in issues]}


def verify_duration_line(payload: dict[str, Any]) -> dict[str, Any]:
    """Compare one prompt's original trailing duration field, not its timeline."""
    original, revised = payload.get("original"), payload.get("revised")
    if not isinstance(original, str) or not isinstance(revised, str):
        issue = _issue(JUDGMENT, "DURATION_INPUT_MISSING", "需要一板的原稿和替换稿正文。")
        return {"status": JUDGMENT, "issues": [asdict(issue)]}
    old_lines = original.splitlines()
    new_lines = revised.splitlines()
    while old_lines and not old_lines[-1].strip():
        old_lines.pop()
    while new_lines and not new_lines[-1].strip():
        new_lines.pop()
    if not old_lines:
        issue = _issue(JUDGMENT, "DURATION_SOURCE_UNKNOWN", "原稿为空，无法确认时长。")
        return {"status": JUDGMENT, "issues": [asdict(issue)]}
    old_last = old_lines[-1]
    pattern = r"\s*(?:总时长|时长)\s*[:：]\s*(约)?\s*\d+(?:\.\d+)?\s*秒\s*"
    match = re.fullmatch(pattern, old_last)
    if not match or match.group(1):
        issue = _issue(JUDGMENT, "DURATION_SOURCE_UNKNOWN", "原稿末行缺少可确认的精确时长，或原稿为估计值；核对同板权威来源。")
        return {"status": JUDGMENT, "issues": [asdict(issue)]}
    if not new_lines or new_lines[-1] != old_last:
        issue = _issue(DEFINITE, "TRAILING_DURATION_CHANGED", "替换稿末尾时长行与原稿不一致、被删除或移位；请核对授权。")
        return {"status": DEFINITE, "issues": [asdict(issue)]}
    return {"status": PASS, "issues": []}


def _print_result(result: dict[str, Any]) -> None:
    print(f"结果：{result['status']}")
    if result.get("message"):
        print(result["message"])
    if "triggered" in result:
        print(f"{result.get('checker', '对白站位完整检查')}：{'已触发' if result['triggered'] else '未触发'}")
        for reason in result.get("trigger_reasons", []):
            print(f"  - 触发原因：{reason}")
    if not result.get("issues"):
        print("问题：无")
        return
    print("问题：")
    for item in result["issues"]:
        print(f"  - [{item['category']}] {item['time_range']} {item['code']}: {item['message']}")
        if "previous_evidence" in item:
            print(f"    上一分镜证据：{item['previous_evidence']}")
            print(f"    下一分镜证据：{item['next_evidence']}")
            print(f"    最小修改建议：{item['suggestion']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("dialogue", "minimal-diff", "handoff", "visual-only", "duration-line"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--input", required=True, type=Path, help="UTF-8 JSON input")
        sub.add_argument("--json", action="store_true", help="print JSON instead of readable text")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    audits = {"dialogue": audit_dialogue_ledger, "minimal-diff": verify_minimal_difference,
              "handoff": audit_handoff_ledger, "visual-only": verify_visual_only_revision,
              "duration-line": verify_duration_line}
    result = audits[args.command](payload)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_result(result)
    return 1 if result["status"] == DEFINITE else 0


if __name__ == "__main__":
    raise SystemExit(main())
