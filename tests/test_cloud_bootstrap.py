"""Offline runtime configuration, conflict protection, rendering and cache-repair checks."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import cloud_bootstrap as C
import manage as M


class CloudBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve(); self.repo = self.base / 'repo'
        self.skills = self.base / '用户 空间/.agents/skills'; self.workspace = self.base / '工作区'
        self.vault = self.workspace / 'Codex'; self.vault.mkdir(parents=True)
        self.instructions = self.base / 'AGENTS.md'; self.instructions.write_text('Existing unrelated rules.\n')
        for i in range(17):
            q = self.repo / 'skills' / f'skill-{i:02d}'; q.mkdir(parents=True)
            (q / 'SKILL.md').write_text(f'---\nname: skill-{i:02d}\ndescription: Fixture\n---\nVault: {{{{AIGC_VAULT}}}}\n')
            (q / 'references').mkdir(); (q / 'references/test.md').write_text('Keep reference.\n')
        (self.repo / 'VERSION').write_text('1.1.1\n')
        (self.repo / 'knowledge').mkdir(); (self.repo / 'templates').mkdir()
        (self.repo / 'knowledge/AGENTS.md').write_text('Vault: {{AIGC_VAULT}}\n')
        for name in ['project-quick.md', 'project-full.md']:
            (self.repo / 'templates' / name).write_text('Output: {{AIGC_OUTPUT_ROOT}}\n')
        (self.vault / 'AGENTS.md').write_text('My notes remain.\nVault: {{AIGC_VAULT}}\nSkill: {{SKILL_ROOT}}\nPlatform: {{PLATFORM}}\n')
        self.addCleanup(patch.stopall)
        patch.object(C, 'ROOT', self.repo).start(); patch.object(M, 'ROOT', self.repo).start()

    def args(self):
        return argparse.Namespace(skills_dir=str(self.skills), workspace=str(self.workspace),
                                  vault=None, outputs=None, instructions_file=str(self.instructions))

    def test_first_install_and_repeat_preserve_content_and_mtimes(self):
        original = (self.vault / 'AGENTS.md').read_bytes()
        first = C.bootstrap(self.args())
        text = (self.vault / 'AGENTS.md').read_text()
        self.assertIn('My notes remain.', text); self.assertNotIn('{{', text)
        self.assertTrue(any(p.is_file() and p.read_bytes() == original
                            for p in Path(first['runtime_backup']).iterdir()))
        self.assertTrue(self.instructions.read_text().startswith('Existing unrelated rules.'))
        before = {p: p.stat().st_mtime_ns for p in self.skills.rglob('*') if p.is_file()}
        second = C.bootstrap(self.args())
        self.assertEqual(second['runtime_files_changed'], [])
        self.assertEqual(second['installation']['changed_targets'], 0)
        self.assertEqual(before, {p: p.stat().st_mtime_ns for p in before})

    def test_unmanaged_skill_conflict_blocks_all_runtime_changes(self):
        q = self.skills / 'skill-00'; q.mkdir(parents=True); f = q / 'SKILL.md'; f.write_text('User-owned Skill')
        before = self.instructions.read_bytes()
        with self.assertRaisesRegex(ValueError, 'different_files'):
            C.bootstrap(self.args())
        self.assertEqual(f.read_text(), 'User-owned Skill')
        self.assertEqual(before, self.instructions.read_bytes())
        self.assertFalse((self.skills / 'skill-01').exists())

    def test_managed_local_skill_edit_is_protected(self):
        C.bootstrap(self.args()); q = self.skills / 'skill-00/SKILL.md'; q.write_text('Local correction')
        with self.assertRaisesRegex(ValueError, 'Protected existing'):
            C.bootstrap(self.args())
        self.assertEqual(q.read_text(), 'Local correction')

    def test_edited_instructions_block_is_protected(self):
        C.bootstrap(self.args()); self.instructions.write_text(self.instructions.read_text().replace('New or mixed', 'User change'))
        before = self.instructions.read_bytes()
        with self.assertRaisesRegex(ValueError, 'instructions were edited'):
            C.bootstrap(self.args())
        self.assertEqual(before, self.instructions.read_bytes())

    def test_cached_missing_skill_is_restored_without_touching_others(self):
        C.bootstrap(self.args()); q = self.skills / 'skill-01/SKILL.md'; time = q.stat().st_mtime_ns
        import shutil
        shutil.rmtree(self.skills / 'skill-00')
        C.bootstrap(self.args())
        self.assertTrue((self.skills / 'skill-00/references/test.md').is_file())
        self.assertEqual(time, q.stat().st_mtime_ns)

    def test_source_templates_keep_placeholders(self):
        before = (self.repo / 'knowledge/AGENTS.md').read_bytes(); C.bootstrap(self.args())
        self.assertEqual(before, (self.repo / 'knowledge/AGENTS.md').read_bytes())

    def test_symlinked_runtime_destination_is_rejected(self):
        target = self.base / 'other'; target.mkdir()
        self.skills.parent.mkdir(parents=True)
        try:
            self.skills.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('Symlink creation privileges unavailable on this platform')
        with self.assertRaisesRegex(ValueError, 'Symlink runtime'):
            C.bootstrap(self.args())
        self.assertEqual(list(target.iterdir()), [])

    def test_unregistered_config_is_protected(self):
        config = self.skills.parent / 'aigc-workflow.json'; config.parent.mkdir(parents=True)
        config.write_text('{"workspace":"user-selected"}')
        with self.assertRaisesRegex(ValueError, 'unregistered AIGC configuration'):
            C.bootstrap(self.args())
        self.assertEqual(config.read_text(), '{"workspace":"user-selected"}')
        self.assertFalse(self.skills.exists())

    def test_workspace_override_is_not_silently_shadowed(self):
        override = self.instructions.with_name('AGENTS.override.md'); override.write_text('User override')
        with self.assertRaisesRegex(ValueError, 'takes precedence'):
            C.bootstrap(self.args())
        self.assertEqual(override.read_text(), 'User override')
        self.assertFalse(self.skills.exists())


if __name__ == '__main__':
    unittest.main()
