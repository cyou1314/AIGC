import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('workflow_paths', ROOT / 'skills/aigc-production-router/scripts/workflow_paths.py')
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

class PortabilityTests(unittest.TestCase):
    def test_repository_command_loads_installed_codex_config(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            (root / 'aigc-workflow.json').write_text(json.dumps({
                'workspace': str(root / 'workspace'), 'vault': str(root / 'vault'),
                'outputs': str(root / 'outputs')}), encoding='utf-8')
            with patch.dict(P.os.environ, {'CODEX_HOME': str(root)}, clear=True):
                workspace, vault, outputs = P.runtime_paths()
            self.assertEqual(vault, root / 'vault')
            self.assertEqual(workspace, root / 'workspace')
            self.assertEqual(outputs, root / 'outputs')

    def test_windows_without_iana_timezone_database_has_correct_offset(self):
        with patch.object(P, 'ZoneInfo', side_effect=ZoneInfoNotFoundError('not installed')):
            tz = P.shanghai_timezone()
        self.assertEqual(dt.datetime(2026, 10, 7, tzinfo=tz).utcoffset(), dt.timedelta(hours=8))

    def test_environment_overrides_vault_and_outputs_independently(self):
        with patch.dict(P.os.environ, {'AIGC_WORKSPACE': str(ROOT / '.local/test-workspace'),
                                     'AIGC_VAULT': str(ROOT / '.local/记忆库'),
                                     'AIGC_OUTPUT_ROOT': str(ROOT / '.local/媒体')}):
            workspace, vault, outputs = P.runtime_paths()
        self.assertEqual(vault, ROOT / '.local/记忆库')
        self.assertEqual(outputs, ROOT / '.local/媒体')
        self.assertEqual(workspace, ROOT / '.local/test-workspace')

if __name__ == '__main__':
    unittest.main()
