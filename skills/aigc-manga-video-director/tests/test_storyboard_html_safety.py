import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/make_storyboard_board.py"

class StoryboardHtmlSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "board.csv"
        self.source.write_text("shot,ratio,visual\n1,16:9,test scene\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def run_tool(self, output):
        return subprocess.run([sys.executable, str(SCRIPT), str(self.source), "--out", str(output)], capture_output=True, text=True)

    def test_source_and_existing_outputs_are_not_overwritten(self):
        original = self.source.read_bytes()
        self.assertNotEqual(self.run_tool(self.source).returncode, 0)
        self.assertEqual(self.source.read_bytes(), original)
        existing = self.root / "existing.html"
        existing.write_text("prior work", encoding="utf-8")
        self.assertNotEqual(self.run_tool(existing).returncode, 0)
        self.assertEqual(existing.read_text(), "prior work")

    def test_new_html_contains_source_scene(self):
        output = self.root / "fresh.html"
        result = self.run_tool(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("test scene", output.read_text(encoding="utf-8"))

    def test_output_symlink_is_rejected(self):
        link = self.root / "link.html"
        try:
            link.symlink_to(self.source)
        except OSError:
            self.skipTest("symlinks unavailable")
        original = self.source.read_bytes()
        self.assertNotEqual(self.run_tool(link).returncode, 0)
        self.assertEqual(self.source.read_bytes(), original)

if __name__ == "__main__":
    unittest.main()
