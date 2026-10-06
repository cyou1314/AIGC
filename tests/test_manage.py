"""Installation/upgrade regressions in isolated workspaces, with no network calls."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('manage', ROOT / 'scripts/manage.py')
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)

class ManagementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aigc-managed-test-')
        self.base = Path(self.tmp.name).resolve(); self.repo = self.base / 'repo'
        self.skills = self.base / '配置 空间' / 'skills'; self.workspace = self.base / '工作区 测试'
        for name in ['alpha-skill', 'beta-skill']:
            source = self.repo / 'skills' / name; source.mkdir(parents=True)
            (source / 'SKILL.md').write_text('---\nname: ' + name + '\ndescription: Test\n---\nVault: {{AIGC_VAULT}}\n', encoding='utf-8')
        (self.repo / 'knowledge').mkdir(); (self.repo / 'templates').mkdir()
        (self.repo / 'knowledge/AGENTS.md').write_text('Vault: {{AIGC_VAULT}}\n', encoding='utf-8')
        (self.repo / 'knowledge/TODO.md').write_text('Default todo\n', encoding='utf-8')
        for name in ['project-quick.md', 'project-full.md']:
            (self.repo / 'templates' / name).write_text('# Project template\n', encoding='utf-8')
        (self.repo / 'VERSION').write_text('1.0.0\n', encoding='utf-8')
        self.root_patch = patch.object(M, 'ROOT', self.repo); self.root_patch.start()
        self.addCleanup(self.root_patch.stop); self.addCleanup(self.tmp.cleanup)

    def args(self, **kwargs):
        defaults = dict(skills_dir=str(self.skills), workspace=str(self.workspace), vault=None, outputs=None,
                        adopt_existing=False, replace_local=False)
        defaults.update(kwargs)
        return type('Args', (), defaults)()

    def install(self, **kwargs):
        result = io.StringIO()
        with contextlib.redirect_stdout(result):
            M.install(self.args(**kwargs))
        return json.loads(result.getvalue())

    def rollback(self, result, **kwargs):
        args = self.args(transaction=result['transaction'], backup_root=str(self.workspace / '.aigc-backups'), **kwargs)
        with contextlib.redirect_stdout(io.StringIO()):
            M.rollback(args)

    def test_install_renders_unicode_paths_without_unresolved_tokens(self):
        result = self.install()
        text = (self.skills / 'alpha-skill/SKILL.md').read_text(encoding='utf-8')
        self.assertIn(str(self.workspace / 'Codex'), text)
        self.assertNotIn('{{AIGC_VAULT}}', text)
        self.assertEqual(result['skills'], 2)
        self.assertEqual(M.load(M.config_for(self.skills))['vault'], str(self.workspace / 'Codex'))

    def test_existing_unmanaged_skill_conflict_changes_nothing(self):
        target = self.skills / 'alpha-skill'; target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('User local work', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.install()
        self.assertEqual((target / 'SKILL.md').read_text(), 'User local work')
        self.assertFalse((self.workspace / 'Codex').exists())

    def test_adoption_and_rollback_preserve_original(self):
        target = self.skills / 'alpha-skill'; target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('User local work', encoding='utf-8')
        result = self.install(adopt_existing=True)
        self.rollback(result)
        self.assertEqual((target / 'SKILL.md').read_text(), 'User local work')
        self.assertFalse((self.skills / 'beta-skill').exists())

    def test_repeat_install_does_not_rewrite_identical_skills_or_knowledge(self):
        self.install()
        target = self.skills / 'alpha-skill/SKILL.md'; time = target.stat().st_mtime_ns
        result = self.install()
        self.assertEqual(target.stat().st_mtime_ns, time)
        self.assertEqual(result['incoming'], [])
        self.assertEqual(result['changed_targets'], 1)  # transaction registry only

    def test_upgrade_preserves_personal_todo_with_incoming(self):
        self.install()
        todo = self.workspace / 'Codex/TODO.md'; todo.write_text('My unresolved task', encoding='utf-8')
        (self.repo / 'knowledge/TODO.md').write_text('New upstream template', encoding='utf-8')
        result = self.install()
        self.assertEqual(todo.read_text(), 'My unresolved task')
        self.assertEqual((self.workspace / 'Codex/.incoming/TODO.md').read_text(), 'New upstream template')
        self.assertTrue(result['incoming'])

    def test_local_skill_modification_blocks_upgrade_and_can_be_restored(self):
        self.install()
        target = self.skills / 'alpha-skill/SKILL.md'; target.write_text('Local correction', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.install()
        result = self.install(replace_local=True)
        self.rollback(result)
        self.assertEqual(target.read_text(), 'Local correction')

    def test_rollback_refuses_new_changes_until_explicit_recovery(self):
        result = self.install()
        target = self.skills / 'alpha-skill/SKILL.md'; target.write_text('New changes after install', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.rollback(result)
        self.rollback(result, replace_local=True)
        self.assertFalse(target.exists())
        self.assertTrue(any('New changes after install' in p.read_text(encoding='utf-8') for p in Path(result['backup']).rglob('SKILL.md')))

    def test_install_failure_recovers_all_started_changes(self):
        self.install()
        before = M.digest(self.skills)
        (self.repo / 'skills/alpha-skill/SKILL.md').write_text('New alpha', encoding='utf-8')
        (self.repo / 'skills/beta-skill/SKILL.md').write_text('New beta', encoding='utf-8')
        original = shutil.move; calls = 0
        def fail_once(source, destination, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError('Simulated interrupted update')
            return original(source, destination, *args, **kwargs)
        with patch.object(M.shutil, 'move', side_effect=fail_once), self.assertRaises(OSError):
            self.install()
        self.assertEqual(M.digest(self.skills), before)

if __name__ == '__main__':
    unittest.main()
