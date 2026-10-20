import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_prompt_review_checks import CHECKS, SCRIPT, correct_segment, dialogue_payload


def pair():
    state = {
        "evidence": "0-4秒：Draven左、Raven右，两人站定相向，摄影机在Draven→Raven轴南侧。",
        "visible_characters": ["Draven", "Raven"],
        "characters": {
            "Draven": {"screen_position": "left", "depth": "midground", "body_orientation": "toward_Raven",
                       "screen_facing": "right", "gaze_target": "Raven", "required_gaze_target": "Raven", "pose": "standing"},
            "Raven": {"screen_position": "right", "depth": "midground", "body_orientation": "toward_Draven",
                      "screen_facing": "left", "gaze_target": "Draven", "required_gaze_target": "Draven", "pose": "standing"},
        },
        "props": {}, "axis": {"id": "Draven->Raven", "side": "south"}, "unknowns": [],
    }
    return {"context": {}, "previous_end": copy.deepcopy(state), "next_start": copy.deepcopy(state),
            "bridge": {"continuous_time": True, "screen_mapping_preserved": True, "camera_changed": False, "events": []}}


def reset(kind="camera_crossing"):
    return {"kind": kind, "evidence": "镜头明确交代越过关系轴并建立新位置。", "spatial_relation_established": True}


def prop_pair():
    data = pair()
    for key in ("previous_end", "next_start"):
        data[key]["props"] = {"@家族徽记": {"holder": "Draven", "hand": "right", "state": "intact", "evidence": "Draven右手持@家族徽记。"}}
    return data


def reverse_pair():
    data = pair()
    data["context"].update(live_dialogue=True, shot_relation=True)
    data["bridge"]["camera_changed"] = True
    for key, speaker, listener, ss, ls, sf, lf in [
        ("previous_end", "Raven", "Draven", "right", "left", "left", "right"),
        ("next_start", "Draven", "Raven", "left", "right", "right", "left"),
    ]:
        state = data[key]
        state["speaker"], state["dialogue_mode"] = speaker, "onscreen"
        state["dialogue"] = correct_segment(speaker, listener, ss, ls, sf, lf)
        state["dialogue"]["camera_transition"] = "cut_to_reverse"
        state["characters"][speaker].update(depth="midground", face_view="three_quarter")
        state["characters"][listener].update(depth="foreground", face_view="back")
    return data


class HandoffTests(unittest.TestCase):
    def codes(self, data):
        return {i["code"] for i in CHECKS.audit_handoff_ledger(data)["issues"]}

    def test_shared_characters_trigger_and_matching_states_pass(self):
        result = CHECKS.audit_handoff_ledger(pair())
        self.assertTrue(result["triggered"])
        self.assertEqual(result["conclusion"], "通过")

    def test_each_context_trigger_works(self):
        for key in ("user_requested_spatial_check", "known_spatial_conflict", "live_dialogue", "speaker_change",
                    "shot_relation", "spatial_action", "continuous_action", "explicit_screen_position", "two_or_more_share_scene"):
            with self.subTest(key=key):
                self.assertTrue(CHECKS.handoff_route({"context": {key: True}})[0])

    def test_exemptions_do_not_force_handoff(self):
        for key in ("independent_single", "pure_noncharacter", "unrelated_montage", "pure_audio",
                    "locked_fixed_wide_no_conflict", "clear_without_spatial_handoff"):
            with self.subTest(key=key):
                data = pair()
                data["context"][key] = True
                result = CHECKS.audit_handoff_ledger(data)
                self.assertFalse(result["triggered"])
                self.assertEqual(result["message"], "未触发相邻分镜空间连续性检查。")

    def test_visual_action_overrides_audio_exemption(self):
        self.assertTrue(CHECKS.handoff_route({"context": {"pure_audio": True, "continuous_action": True}})[0])

    def test_user_question_overrides_fixed_wide_exemption(self):
        self.assertTrue(CHECKS.handoff_route({"context": {"locked_fixed_wide_no_conflict": True, "user_requested_spatial_check": True}})[0])

    def test_missing_pair_cannot_pass(self):
        result = CHECKS.audit_handoff_ledger({"context": {"user_requested_spatial_check": True}})
        self.assertEqual(result["status"], CHECKS.JUDGMENT)
        self.assertIn("BOUNDARY_EVIDENCE_MISSING", {i["code"] for i in result["issues"]})

    def test_sparse_or_malformed_state_never_silently_passes(self):
        for bad in ({"characters": {"Draven": {}}}, {"characters": []}, {"characters": {"Draven": "left"}}, {"axis": "south"}):
            data = pair()
            data["next_start"].update(bad)
            self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.JUDGMENT)
        self.assertEqual(CHECKS.audit_handoff_ledger([])["status"], CHECKS.JUDGMENT)

    def test_unknown_material_pose_is_not_assumed_unchanged(self):
        data = pair()
        data["next_start"]["characters"]["Draven"]["pose"] = None
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.JUDGMENT)

    def test_noncritical_unknowns_do_not_block_pass(self):
        data = pair()
        data["next_start"]["noncritical_unknowns"] = ["无身高冲突时，眼睛的精确高度未说明。"]
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.PASS)

    def test_back_to_front_with_explicitly_fixed_camera_is_flagged(self):
        data = pair()
        data["previous_end"]["characters"]["Draven"]["face_view"] = "back"
        data["next_start"]["characters"]["Draven"]["face_view"] = "front"
        self.assertIn("FACE_VIEW_CHANGE", self.codes(data))
        data["bridge"]["camera_changed"] = True
        self.assertNotIn("FACE_VIEW_CHANGE", self.codes(data))

    def test_normalized_end_state_is_used_instead_of_earlier_position(self):
        data = pair()
        data["previous_end"]["evidence"] = "0-3秒先在左侧，3-4秒已走到右侧；此处记录末镜结束。"
        data["previous_end"]["characters"]["Draven"]["screen_position"] = "right"
        data["next_start"]["characters"]["Draven"]["screen_position"] = "right"
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.PASS)

    def test_swap_without_movement_is_conflict(self):
        data = pair()
        data["next_start"]["characters"]["Draven"]["screen_position"] = "right"
        result = CHECKS.audit_handoff_ledger(data)
        self.assertEqual(result["status"], CHECKS.DEFINITE)
        issue = next(i for i in result["issues"] if i["code"] == "SCREEN_POSITION_CHANGE")
        for key in ("category", "previous_evidence", "next_evidence", "reason", "suggestion"):
            self.assertTrue(issue[key])

    def test_reframing_is_not_definite_teleport(self):
        data = pair()
        data["bridge"].update(screen_mapping_preserved=None, camera_changed=True)
        data["next_start"]["characters"]["Draven"]["screen_position"] = "center"
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.JUDGMENT)

    def test_body_turn_requires_its_own_event(self):
        data = pair()
        data["next_start"]["characters"]["Draven"]["body_orientation"] = "toward_door"
        self.assertIn("BODY_ORIENTATION_CHANGE", self.codes(data))
        data["bridge"]["events"] = [{"subject": "Draven", "field": "body_orientation", "from": "toward_Raven", "to": "toward_door", "evidence": "上一末镜转身面向门。"}]
        self.assertNotIn("BODY_ORIENTATION_CHANGE", self.codes(data))

    def test_eyeline_only_conflicts_with_explicit_target(self):
        data = pair()
        data["next_start"]["characters"]["Draven"]["gaze_target"] = "door"
        self.assertIn("EYELINE_TARGET", self.codes(data))
        data["next_start"]["characters"]["Draven"].pop("required_gaze_target")
        self.assertNotIn("EYELINE_TARGET", self.codes(data))

    def test_matching_action_end_start_passes(self):
        data = pair()
        data["previous_end"]["characters"]["Draven"]["action_end"] = "hand_raised"
        data["next_start"]["characters"]["Draven"]["action_start"] = "hand_raised"
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.PASS)

    def test_repeated_or_skipped_action_is_detected(self):
        for start in ("pre_strike", "walking_away"):
            with self.subTest(start=start):
                data = pair()
                data["previous_end"]["characters"]["Draven"]["action_end"] = "strike_landed"
                data["next_start"]["characters"]["Draven"]["action_start"] = start
                self.assertIn("ACTION_HANDOFF", self.codes(data))

    def test_unknown_receiver_is_judgment(self):
        data = pair()
        data["previous_end"]["characters"]["Draven"]["action_end"] = "hand_raised"
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.JUDGMENT)

    def test_right_exit_left_entrance_continues_screen_right(self):
        data = pair()
        data["previous_end"]["characters"]["Draven"].update(exit_edge="right", motion_vector="right")
        data["next_start"]["characters"]["Draven"].update(entry_edge="left", motion_vector="right")
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.PASS)

    def test_same_edge_entry_under_locked_mapping_is_flagged(self):
        data = pair()
        data["previous_end"]["characters"]["Draven"]["exit_edge"] = "right"
        data["next_start"]["characters"]["Draven"]["entry_edge"] = "right"
        self.assertIn("EXIT_ENTRY_DIRECTION", self.codes(data))

    def test_anatomical_hand_swap_is_not_excused_by_crossing(self):
        data = prop_pair()
        data["bridge"]["axis_reset"] = reset()
        data["next_start"]["axis"]["side"] = "north"
        data["next_start"]["props"]["@家族徽记"]["hand"] = "left"
        self.assertEqual(self.codes(data), {"PROP_HAND"})

    def test_owner_and_hand_can_transfer_with_matching_evidence(self):
        data = prop_pair()
        data["next_start"]["props"]["@家族徽记"].update(holder="Raven", hand="left")
        self.assertEqual(self.codes(data), {"PROP_HOLDER", "PROP_HAND"})
        data["bridge"]["events"] = [
            {"subject": "@家族徽记", "field": "holder", "from": "Draven", "to": "Raven", "evidence": "交到Raven左手。"},
            {"subject": "@家族徽记", "field": "hand", "from": "right", "to": "left", "evidence": "由Draven右手交到Raven左手。"}]
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.PASS)

    def test_prop_out_of_frame_is_not_a_proven_disappearance(self):
        data = prop_pair()
        data["next_start"]["props"] = {}
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.JUDGMENT)

    def test_known_axis_crossing_without_bridge_conflicts(self):
        data = pair()
        data["next_start"]["axis"]["side"] = "north"
        self.assertIn("AXIS_CROSSING", self.codes(data))

    def test_unknown_camera_side_is_not_called_crossing(self):
        data = pair()
        data["next_start"]["axis"]["side"] = None
        result = CHECKS.audit_handoff_ledger(data)
        self.assertEqual(result["status"], CHECKS.JUDGMENT)
        self.assertIn(CHECKS.AXIS_UNKNOWN, [i["message"] for i in result["issues"]])
        self.assertNotIn("AXIS_CROSSING", self.codes(data))

    def test_each_evidenced_legal_axis_bridge_passes(self):
        for kind in CHECKS.AXIS_REBUILDS:
            with self.subTest(kind=kind):
                data = pair()
                data["next_start"]["axis"]["side"] = "north"
                data["next_start"]["characters"]["Draven"]["screen_position"] = "right"
                data["bridge"]["axis_reset"] = dict(reset(kind), user_requested=True)
                self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.PASS)

    def test_bare_insert_is_not_axis_reestablishment(self):
        data = pair()
        data["next_start"]["axis"]["side"] = "north"
        data["bridge"]["axis_reset"] = {"kind": "insert_reestablish", "evidence": "切到花瓶。"}
        self.assertIn("AXIS_CROSSING", self.codes(data))

    def test_intentional_cross_requires_user_request(self):
        self.assertFalse(CHECKS.axis_reset_is_valid(reset("intentional_cross")))

    def test_new_dominant_pair_requires_axis_rebuild(self):
        data = pair()
        data["next_start"]["axis"]["id"] = "Raven->Ethan"
        self.assertIn("AXIS_REBUILD_UNCLEAR", self.codes(data))
        data["bridge"]["axis_reset"] = reset("wide_reestablish")
        self.assertNotIn("AXIS_REBUILD_UNCLEAR", self.codes(data))

    def test_reverse_changes_depth_and_face_without_body_turn(self):
        self.assertEqual(CHECKS.audit_handoff_ledger(reverse_pair())["status"], CHECKS.PASS)

    def test_wrong_speaking_face_and_lips_are_detected(self):
        data = reverse_pair()
        data["next_start"]["dialogue"].update(primary_face="Raven", lip_sync_allowed=["Raven"])
        self.assertTrue({"WRONG_PRIMARY_FACE", "LIP_SYNC_OWNER"}.issubset(self.codes(data)))

    def test_foreground_front_is_conflict_but_missing_is_uncertain(self):
        data = reverse_pair()
        data["next_start"]["dialogue"]["foreground_view"] = "front"
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.DEFINITE)
        data["next_start"]["dialogue"].pop("foreground_view")
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.JUDGMENT)

    def test_focus_shift_does_not_replace_reverse(self):
        data = reverse_pair()
        data["next_start"]["dialogue"]["camera_transition"] = "focus_shift"
        self.assertIn("SPEAKER_SWITCH_WITHOUT_CUT", self.codes(data))

    def test_generic_cut_does_not_specify_ots_reverse(self):
        data = reverse_pair()
        data["next_start"]["dialogue"]["camera_transition"] = "cut"
        self.assertIn("REVERSE_CUT_UNSPECIFIED", self.codes(data))

    def test_null_face_and_lip_fields_mean_uncertainty(self):
        data = reverse_pair()
        data["next_start"]["dialogue"].update(face_views=None, lip_sync_allowed=None, silent_characters=None)
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.JUDGMENT)

    def test_two_simultaneous_lip_owners_fail(self):
        data = reverse_pair()
        data["next_start"]["dialogue"]["lip_sync_allowed"] = ["Draven", "Raven"]
        self.assertIn("LIP_SYNC_OWNER", self.codes(data))

    def test_offscreen_radio_does_not_need_a_face(self):
        data = pair()
        data["previous_end"].update(speaker="radio", dialogue_mode="telephone")
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.PASS)

    def test_key_handoff_missing_or_contradictory(self):
        data = pair()
        data["handoff_out"] = {"door": "open"}
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.JUDGMENT)
        data["receiver_in"] = {"door": "closed"}
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.DEFINITE)
        data["receiver_in"] = {"door": "open"}
        self.assertEqual(CHECKS.audit_handoff_ledger(data)["status"], CHECKS.PASS)

    def test_crossing_never_excuses_action_repetition(self):
        data = pair()
        data["bridge"]["axis_reset"] = reset()
        data["previous_end"]["characters"]["Draven"]["action_end"] = "strike_landed"
        data["next_start"]["characters"]["Draven"]["action_start"] = "pre_strike"
        self.assertIn("ACTION_HANDOFF", self.codes(data))

    def test_legacy_dialogue_accepts_evidenced_rebuild_but_honors_user_locks(self):
        data = dialogue_payload(position_locks={}, facing_locks={})
        a = correct_segment("Raven", "Draven", "right", "left", "left", "right")
        b = correct_segment("Draven", "Raven", "right", "left", "left", "right")
        b.update(axis_reset=reset(), camera_transition="cut_to_reverse", axis_180_maintained=False)
        data["segments"] = [a, b]
        self.assertEqual(CHECKS.audit_dialogue_ledger(data)["status"], CHECKS.PASS)
        data["context"]["position_locks"] = {"Draven": "left"}
        self.assertEqual(CHECKS.audit_dialogue_ledger(data)["status"], CHECKS.DEFINITE)

    def test_missing_silence_is_suggestion_not_a_definite_error(self):
        data = reverse_pair()
        data["next_start"]["dialogue"].pop("silent_characters")
        result = CHECKS.audit_handoff_ledger(data)
        self.assertEqual(result["status"], CHECKS.PASS)
        self.assertEqual(result["issues"][0]["category"], CHECKS.SUGGESTION)

    def test_cli_json_and_exit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pair.json"
            for conflict in (False, True):
                data = pair()
                if conflict:
                    data["next_start"]["axis"]["side"] = "north"
                path.write_text(json.dumps(data), encoding="utf-8")
                run = subprocess.run([sys.executable, str(SCRIPT), "handoff", "--input", str(path), "--json"], capture_output=True, text=True)
                self.assertEqual(run.returncode, int(conflict), run.stderr)
                self.assertEqual(json.loads(run.stdout)["conclusion"], "存在确定冲突" if conflict else "通过")


def edit_payload():
    parts = [{"kind": "locked", "original": "角色：@Raven常服\n画面：0秒～3秒：", "revised": "角色：@Raven常服\n画面：0秒～3秒："},
             {"kind": "visual", "original": "背影。", "revised": "切至反打镜头，清晰正脸。"},
             {"kind": "locked", "original": "\n台词 Raven常服：Stop!\n时长：3秒", "revised": "\n台词 Raven常服：Stop!\n时长：3秒"}]
    return {"previous_original": "上一分镜完整原文", "previous_revised": "上一分镜完整原文",
            "next_original": "".join(p["original"] for p in parts), "next_revised": "".join(p["revised"] for p in parts),
            "mode": "visual-only-next", "parts": parts, "reference_tags": ["@Raven常服"]}


class VisualPermissionTests(unittest.TestCase):
    def test_authorized_partition_passes(self):
        self.assertEqual(CHECKS.verify_visual_only_revision(edit_payload())["status"], CHECKS.PASS)

    def test_default_review_only_rejects_modification(self):
        data = edit_payload()
        data.pop("mode")
        self.assertEqual(CHECKS.verify_visual_only_revision(data)["status"], CHECKS.DEFINITE)

    def test_review_only_with_unchanged_text_passes(self):
        data = edit_payload()
        data.update(mode="review-only", next_revised=data["next_original"])
        self.assertEqual(CHECKS.verify_visual_only_revision(data)["status"], CHECKS.PASS)

    def test_previous_prompt_is_immutable(self):
        data = edit_payload()
        data["previous_revised"] += "改动"
        self.assertEqual(CHECKS.verify_visual_only_revision(data)["issues"][0]["code"], "PREVIOUS_PROMPT_CHANGED")

    def test_embedded_dialogue_time_tag_are_locked(self):
        for old, new in [("Stop!", "Go!"), ("0秒～3秒", "0秒～4秒"), ("@Raven常服", "@Raven红裙"), ("时长：3秒", "时长：4秒")]:
            with self.subTest(old=old):
                data = edit_payload()
                for part in data["parts"]:
                    part["revised"] = part["revised"].replace(old, new)
                data["next_revised"] = "".join(p["revised"] for p in data["parts"])
                self.assertEqual(CHECKS.verify_visual_only_revision(data)["status"], CHECKS.DEFINITE)

    def test_partition_cannot_omit_extra_edits(self):
        data = edit_payload()
        data["next_revised"] += "\n新增台词"
        self.assertEqual(CHECKS.verify_visual_only_revision(data)["issues"][0]["code"], "EDIT_PARTITION_MISMATCH")

    def test_tag_inside_visual_partition_still_protected_by_inventory(self):
        data = edit_payload()
        data["parts"][1].update(original="@Raven常服背影。", revised="@Raven红裙正脸。")
        data.update(next_original="".join(p["original"] for p in data["parts"]), next_revised="".join(p["revised"] for p in data["parts"]))
        self.assertIn("REFERENCE_TAG_CHANGED", {i["code"] for i in CHECKS.verify_visual_only_revision(data)["issues"]})

    def test_missing_or_malformed_partition_fails(self):
        for parts in ([], None, ["bad"], [{"kind": "anything", "original": "x", "revised": "y"}]):
            data = edit_payload()
            data["parts"] = parts
            self.assertEqual(CHECKS.verify_visual_only_revision(data)["status"], CHECKS.DEFINITE)


if __name__ == "__main__":
    unittest.main()
