import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from PIL import Image
import contextlib
import io
from types import SimpleNamespace
from unittest.mock import patch
import replace_storyboard_panels as replacer

from replace_storyboard_panels import (
    collect_replacements,
    default_output,
    default_preview,
)


class ReplacementMappingTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.panel_one = self.directory / "1.png"
        self.directory_panel_two = self.directory / "2.jpg"
        self.panel_five = self.directory / "5.png"
        self.notes = self.directory / "notes.png"
        self.explicit_panel_two = self.directory / "explicit-panel-2.png"
        for path in (
            self.panel_one,
            self.directory_panel_two,
            self.panel_five,
            self.notes,
            self.explicit_panel_two,
            self.directory / "0.png",
            self.directory / "01.png",
            self.directory / "1a.png",
            self.directory / "6.JPEG",
            self.directory / "7.WeBp",
            self.directory / "8.BMP",
            self.directory / "9.TIF",
        ):
            path.touch()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_collect_replacements_maps_numeric_files_in_integer_order(self):
        replacements = collect_replacements([], self.directory)

        self.assertEqual(list(replacements), [1, 2, 5, 6, 7, 8, 9])
        self.assertEqual(replacements[1], self.panel_one)
        self.assertEqual(replacements[2], self.directory_panel_two)
        self.assertEqual(replacements[5], self.panel_five)
        self.assertNotIn(0, replacements)

    def test_collect_replacements_ignores_non_numeric_and_invalid_numeric_stems(self):
        replacements = collect_replacements([], self.directory)

        self.assertNotIn(self.notes, replacements.values())
        self.assertEqual(list(replacements), [1, 2, 5, 6, 7, 8, 9])

    def test_collect_replacements_applies_explicit_mappings_last(self):
        replacements = collect_replacements([(2, self.explicit_panel_two)], self.directory)

        self.assertEqual(replacements[2], self.explicit_panel_two)

    def test_collect_replacements_rejects_missing_or_non_directory_sources(self):
        missing = self.directory / "missing"
        image_file = self.directory / "1.png"

        with self.assertRaisesRegex(ValueError, "does not exist"):
            collect_replacements([], missing)
        with self.assertRaisesRegex(ValueError, "not a directory"):
            collect_replacements([], image_file)
        with self.assertRaisesRegex(ValueError, "does not exist"):
            collect_replacements([(3, missing)], self.directory)

    def test_default_names_use_chinese_suffixes(self):
        board = Path("C:/boards/episode-01.png")

        self.assertEqual(default_output(board), Path("C:/boards/episode-01_已替换.png"))
        self.assertEqual(default_preview(board), Path("C:/boards/episode-01_布局确认.png"))


class SyntheticBoardSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.board = self.root / 'board.png'
        self.replacement = self.root / 'red.png'
        self.output = self.root / 'out.png'
        Image.new('RGB', (200, 100), (0, 0, 0)).save(self.board)
        Image.new('RGB', (20, 20), (255, 0, 0)).save(self.replacement)
        self.layout = SimpleNamespace(panels=((0, 0, 100, 100), (100, 0, 200, 100)), confidence=0.95)

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, *arguments):
        argv = ['replace_storyboard_panels.py', '--board', str(self.board),
                '--replace', '1=' + str(self.replacement), *arguments]
        with patch.object(sys, 'argv', argv), patch.object(replacer, 'detect_layout', return_value=self.layout), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return replacer.main()

    def test_uncertain_window_never_falls_back_to_full_panel(self):
        before = self.board.read_bytes()
        with self.assertRaises(SystemExit):
            self.invoke('--mode', 'window', '--output', str(self.output))
        self.assertFalse(self.output.exists())
        self.assertEqual(self.board.read_bytes(), before)

    def test_low_confidence_requires_manual_target(self):
        self.layout.confidence = 0.40
        with self.assertRaises(SystemExit):
            self.invoke('--output', str(self.output))
        self.assertFalse(self.output.exists())
        self.invoke('--manual-panel', '1=0,0,100,100', '--output', str(self.output))
        self.assertTrue(self.output.exists())

    def test_manual_window_preserves_border_and_other_panel(self):
        self.invoke('--mode', 'window', '--manual-window', '1=10,10,70,70', '--output', str(self.output))
        image = Image.open(self.output).convert('RGB')
        self.assertEqual(image.getpixel((20, 20)), (255, 0, 0))
        self.assertEqual(image.getpixel((5, 5)), (0, 0, 0))
        self.assertEqual(image.getpixel((150, 50)), (0, 0, 0))

    def test_out_of_bounds_window_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.invoke('--mode', 'window', '--manual-window', '1=90,10,20,20', '--output', str(self.output))
        self.assertFalse(self.output.exists())

    def test_cannot_overwrite_source_or_existing_result(self):
        before = self.board.read_bytes()
        with self.assertRaises(SystemExit):
            self.invoke('--output', str(self.board))
        self.assertEqual(self.board.read_bytes(), before)
        self.output.write_bytes(b'existing file')
        with self.assertRaises(SystemExit):
            self.invoke('--output', str(self.output))
        self.assertEqual(self.output.read_bytes(), b'existing file')

    def test_cannot_overwrite_replacement_or_source_with_debug(self):
        before = self.replacement.read_bytes()
        with self.assertRaises(SystemExit):
            self.invoke('--output', str(self.replacement))
        self.assertEqual(self.replacement.read_bytes(), before)
        with self.assertRaises(SystemExit):
            self.invoke('--debug-layout', str(self.board), '--output', str(self.output))
        self.assertFalse(self.output.exists())

    def test_manual_panel_mapping_does_not_reorder_explicit_indices(self):
        self.invoke('--manual-panel', '1=100,0,100,100', '--manual-panel', '2=0,0,100,100', '--output', str(self.output))
        image = Image.open(self.output).convert('RGB')
        self.assertEqual(image.getpixel((150, 50)), (255, 0, 0))
        self.assertEqual(image.getpixel((50, 50)), (0, 0, 0))

    def test_manual_panel_gap_and_invalid_coordinates_are_rejected(self):
        for argument in ('4=0,0,10,10', '1=195,0,10,10'):
            with self.subTest(argument=argument), self.assertRaises(SystemExit):
                self.invoke('--manual-panel', argument, '--output', str(self.output))
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
