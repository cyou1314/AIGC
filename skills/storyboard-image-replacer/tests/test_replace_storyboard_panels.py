import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

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


if __name__ == "__main__":
    unittest.main()
