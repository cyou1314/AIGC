import builtins
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import storyboard_layout as layout_module
from storyboard_layout import (
    LayoutResult,
    detect_layout,
    make_analysis_image,
    scale_rect,
    sort_panels,
)


class StoryboardLayoutTests(unittest.TestCase):
    @staticmethod
    def _black_framed_board(rows, panel_size=(100, 70), gutter=8, margin=10):
        """Build an intentionally plain black-frame storyboard for detector tests."""
        panel_height = panel_size[1]
        width = margin * 2 + max(sum(row) + gutter * (len(row) - 1) for row in rows)
        height = margin * 2 + len(rows) * panel_height + gutter * (len(rows) - 1)
        image = Image.new("RGB", (width, height), "#d8d8d8")
        expected = []
        y = margin
        for row in rows:
            x = margin
            for width in row:
                image.paste("#ffffff", (x, y, x + width, y + panel_height))
                for offset in range(3):
                    x1, y1 = x + offset, y + offset
                    x2, y2 = x + width - 1 - offset, y + panel_height - 1 - offset
                    for px in range(x1, x2 + 1):
                        image.putpixel((px, y1), (0, 0, 0))
                        image.putpixel((px, y2), (0, 0, 0))
                    for py in range(y1, y2 + 1):
                        image.putpixel((x1, py), (0, 0, 0))
                        image.putpixel((x2, py), (0, 0, 0))
                expected.append((x, y, x + width, y + panel_height))
                x += width + gutter
            y += panel_height + gutter
        return image, expected

    def test_detect_layout_finds_black_framed_three_by_three_grid(self):
        image, expected = self._black_framed_board([[100, 100, 100]] * 3)

        result = detect_layout(image)

        self.assertEqual(len(result.panels), 9)
        self.assertEqual(result.panels, tuple(expected))
        self.assertGreaterEqual(result.confidence, 0.72)
        self.assertTrue(result.reasons)

    def test_detect_layout_keeps_incomplete_final_row_in_reading_order(self):
        image, expected = self._black_framed_board(
            [[90, 120, 90], [100, 100, 100], [145, 155]]
        )

        result = detect_layout(image)

        self.assertEqual(len(result.panels), 8)
        self.assertEqual(result.panels, tuple(expected))
        self.assertGreaterEqual(result.confidence, 0.72)

    def test_detect_layout_ignores_long_content_lines_inside_framed_panels(self):
        image, expected = self._black_framed_board(
            [[180, 180], [180, 180]], panel_size=(180, 120)
        )
        draw = ImageDraw.Draw(image)
        for x1, y1, x2, y2 in expected:
            width = x2 - x1
            draw.line(
                (x1 + width // 3, y1 + 8, x1 + width // 3, y2 - 8),
                fill="black",
                width=4,
            )
            draw.line(
                (x1 + 2 * width // 3, y1 + 8, x1 + 2 * width // 3, y2 - 8),
                fill="black",
                width=4,
            )
            draw.line(
                (x1 + 8, y1 + 2 * (y2 - y1) // 3, x2 - 8, y1 + 12),
                fill="black",
                width=3,
            )

        result = detect_layout(image)

        self.assertEqual(result.panels, tuple(expected))
        self.assertGreaterEqual(result.confidence, 0.72)

    def test_projection_candidates_ignore_internal_vertical_content_lines(self):
        image, expected = self._black_framed_board(
            [[180, 180]], panel_size=(180, 120)
        )
        draw = ImageDraw.Draw(image)
        for x1, y1, x2, y2 in expected:
            width = x2 - x1
            draw.line(
                (x1 + width // 3, y1 + 8, x1 + width // 3, y2 - 8),
                fill="black",
                width=4,
            )
            draw.line(
                (x1 + 2 * width // 3, y1 + 8, x1 + 2 * width // 3, y2 - 8),
                fill="black",
                width=4,
            )
        gray = np.asarray(image.convert("L"))
        dark = gray < 72

        columns = layout_module._column_candidates(
            dark, (expected[0][1], expected[0][3])
        )

        self.assertEqual(columns, [(expected[0][0], expected[0][2]), (expected[1][0], expected[1][2])])

    def test_edge_background_signal_finds_panels_without_dark_frame_bars(self):
        image = Image.new("RGB", (228, 168), "#d8d8d8")
        expected = (
            (10, 10, 110, 80),
            (118, 10, 218, 80),
            (10, 88, 110, 158),
            (118, 88, 218, 158),
        )
        for index, rect in enumerate(expected):
            image.paste(("#f8f8f8", "#eeeeee")[index % 2], rect)
        gray = np.asarray(image.convert("L"))
        self.assertFalse(np.any(gray < 72))

        candidates = layout_module._edge_background_candidates(gray)

        self.assertEqual(candidates, expected)

    def test_regular_layout_without_meaningful_signal_agreement_stays_below_threshold(self):
        panels = tuple(
            (10 + column * 108, 10 + row * 78, 110 + column * 108, 80 + row * 78)
            for row in range(3)
            for column in range(3)
        )

        confidence = layout_module._confidence(
            panels, (336, 254), independent=(panels[0],)
        )

        self.assertLess(confidence, 0.72)

    def test_one_selected_against_nine_independent_stays_below_threshold(self):
        panels = tuple(
            (10 + column * 108, 10 + row * 78, 110 + column * 108, 80 + row * 78)
            for row in range(3)
            for column in range(3)
        )

        confidence = layout_module._confidence(
            panels[:1], (336, 254), independent=panels
        )

        self.assertLess(confidence, 0.72)

    def test_four_selected_against_nine_independent_stays_below_threshold(self):
        panels = tuple(
            (10 + column * 108, 10 + row * 78, 110 + column * 108, 80 + row * 78)
            for row in range(3)
            for column in range(3)
        )

        confidence = layout_module._confidence(
            panels[:4], (336, 254), independent=panels
        )

        self.assertLess(confidence, 0.72)

    def test_opencv_primary_can_accept_strong_closed_layout_without_projection_agreement(self):
        panels = tuple(
            (10 + column * 108, 10 + row * 78, 110 + column * 108, 80 + row * 78)
            for row in range(3)
            for column in range(3)
        )

        confidence = layout_module._opencv_confidence(
            panels, (336, 254), independent=()
        )

        self.assertGreaterEqual(confidence, 0.72)

    def test_frame_winner_uses_conservative_confidence_when_cv2_is_available(self):
        image, expected = self._black_framed_board([[100, 100, 100]] * 3)

        with (
            patch.object(layout_module, "cv2", object()),
            patch.object(layout_module, "_contour_candidates", return_value=()),
        ):
            result = detect_layout(image)

        self.assertEqual(result.panels, tuple(expected))
        self.assertLess(result.confidence, 0.72)
        self.assertTrue(any("dark frame bars" in reason for reason in result.reasons))
        self.assertTrue(any("conservative" in reason for reason in result.reasons))

    def test_normalize_candidates_rejects_materially_overlapping_rectangles(self):
        candidates = ((10, 10, 110, 110), (30, 30, 120, 120))

        normalized = layout_module._normalize_candidates(candidates, 200, 200)

        self.assertEqual(normalized, ((10, 10, 110, 110),))

    def test_module_import_and_detection_work_when_cv2_import_fails(self):
        module_path = Path(layout_module.__file__)
        module_name = "storyboard_layout_without_cv2"
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        original_import = builtins.__import__

        def import_without_cv2(name, *args, **kwargs):
            if name == "cv2":
                raise ImportError("cv2 unavailable for fallback test")
            return original_import(name, *args, **kwargs)

        sys.modules[module_name] = module
        try:
            with patch("builtins.__import__", side_effect=import_without_cv2):
                spec.loader.exec_module(module)
            image, _ = self._black_framed_board([[100, 100], [100, 100]])

            result = module.detect_layout(image)

            self.assertIsInstance(result, module.LayoutResult)
            self.assertEqual(result.analysis_size, image.size)
            self.assertTrue(any("Pillow/NumPy fallback" in reason for reason in result.reasons))
        finally:
            sys.modules.pop(module_name, None)

    def test_detect_layout_reports_which_detector_was_used(self):
        image, _ = self._black_framed_board([[100, 100], [100, 100]])

        result = detect_layout(image)

        expected = (
            "OpenCV closed contours"
            if layout_module.cv2 is not None
            else "Pillow/NumPy fallback"
        )
        self.assertTrue(any(expected in reason for reason in result.reasons))

    def test_sort_panels_groups_nearby_row_centers_before_sorting_by_x(self):
        panels = ((110, 81, 180, 151), (10, 10, 80, 80), (10, 82, 80, 152), (110, 9, 180, 79))

        self.assertEqual(
            sort_panels(panels),
            ((10, 10, 80, 80), (110, 9, 180, 79), (10, 82, 80, 152), (110, 81, 180, 151)),
        )

    def test_analysis_image_reduces_large_image_and_returns_scale_factors(self):
        image = Image.new("RGBA", (2400, 1600), (10, 20, 30, 255))

        analysis, scale_x, scale_y = make_analysis_image(image)

        self.assertEqual(analysis.mode, "RGB")
        self.assertEqual(analysis.size, (1200, 800))
        self.assertEqual((scale_x, scale_y), (2.0, 2.0))

    def test_analysis_image_caps_caller_max_side_at_1200(self):
        image = Image.new("RGB", (2400, 1600), (10, 20, 30))

        analysis, scale_x, scale_y = make_analysis_image(image, max_side=2400)

        self.assertEqual(analysis.size, (1200, 800))
        self.assertEqual((scale_x, scale_y), (2.0, 2.0))

    def test_analysis_image_keeps_extreme_aspect_ratio_dimension_at_least_one(self):
        image = Image.new("RGB", (100000, 1), (10, 20, 30))

        analysis, scale_x, scale_y = make_analysis_image(image)

        self.assertEqual(analysis.size, (1200, 1))
        self.assertEqual((scale_x, scale_y), (100000 / 1200, 1.0))

    def test_analysis_image_leaves_small_image_at_source_size(self):
        image = Image.new("L", (600, 400), 128)

        analysis, scale_x, scale_y = make_analysis_image(image)

        self.assertEqual(analysis.mode, "RGB")
        self.assertEqual(analysis.size, (600, 400))
        self.assertEqual((scale_x, scale_y), (1.0, 1.0))

    def test_scale_rect_rounds_and_clamps_to_source_bounds(self):
        self.assertEqual(
            scale_rect((10, 20, 610, 420), 2.0, 2.0, (1200, 800)),
            (20, 40, 1200, 800),
        )

    def test_layout_result_is_immutable(self):
        result = LayoutResult(((1, 2, 3, 4),), 0.9, ("ok",), (1200, 800))

        with self.assertRaises(AttributeError):
            result.confidence = 0.5


if __name__ == "__main__":
    unittest.main()
