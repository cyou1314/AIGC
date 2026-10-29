import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sync_github', ROOT / 'scripts/sync_github.py')
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)

class MergeTests(unittest.TestCase):
    def test_disjoint_edit_preserves_portable_adaptation(self):
        base = 'title\npath=old-machine\n\nrule=old\n'
        local = base.replace('rule=old', 'rule=new')
        portable = base.replace('path=old-machine', 'path=runtime-config')
        self.assertEqual(S.merge_text(base, local, portable), portable.replace('rule=old', 'rule=new'))

    def test_overlapping_change_is_not_overwritten(self):
        with self.assertRaises(S.SyncError):
            S.merge_text('rule=old\n', 'rule=local\n', 'rule=portable\n')

    def test_identical_edit_is_idempotent(self):
        self.assertEqual(S.merge_text('old\n', 'new\n', 'new\n'), 'new\n')

    def test_delete_against_modified_repository_stops(self):
        with self.assertRaises(S.SyncError):
            S.merge_text('old\n', None, 'new\n')

    def test_scopes_exclude_credentials_media_and_private_fixtures(self):
        for name in ['.local/state.json', 'projects/private.md', 'skills/x/auth.json',
                     'skills/x/.env.local', 'skills/x/video.mp4',
                     'skills/auto-edit-video/tests/fixtures/collapsed_asr/file.json']:
            self.assertFalse(S.allowed(name), name)
        self.assertTrue(S.allowed('skills/x/references/new.md'))

    def test_reserved_domain_fixture_is_distinct_from_real_credential_url(self):
        S.guarded(b'https://user:secret@example.com/file', 'skills/demo/tests/test_url.py')
        S.guarded(b'https://user:secret@cdn.example.test/file', 'skills/demo/tests/test_url.py')
        with self.assertRaises(S.SyncError):
            S.guarded(b'https://user' + b':secret@service.example/file', 'skills/demo/tests/test_url.py')

@unittest.skipUnless(shutil.which('git'), 'git is required for local transport integration')
class SyncIntegrationTests(unittest.TestCase):
    def git(self, *args, cwd=None):
        result = subprocess.run(['git', *args], cwd=cwd or self.repo,
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.base = Path(self.tmp.name).resolve()
        self.repo = self.base / 'repo'; self.repo.mkdir()
        self.remote = self.base / 'remote.git'
        self.git('init', '--bare', str(self.remote))
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'AIGC-test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'core.autocrlf', 'false')
        self.skills = self.base / 'installed'; (self.skills / 'demo').mkdir(parents=True)
        self.vault = self.base / 'vault'; self.vault.mkdir()
        (self.repo / 'skills/demo').mkdir(parents=True)
        (self.repo / 'knowledge/agent').mkdir(parents=True)
        (self.repo / 'templates').mkdir()
        (self.repo / 'scripts').mkdir()
        (self.repo / '.gitignore').write_text('.local/\n', encoding='utf-8')
        (self.repo / 'VERSION').write_text('1.0.0\n')
        (self.repo / 'CHANGELOG.md').write_text('# Changelog\n\n## 1.0.0\n')
        (self.repo / 'sources.json').write_text(json.dumps({'skills': [{'name': 'demo'}]}))
        (self.skills / 'demo/SKILL.md').write_text('title\npath=old-machine\n\nrule=old\n')
        (self.repo / 'skills/demo/SKILL.md').write_text('title\npath=runtime-config\n\nrule=old\n')
        (self.repo / 'scripts/source_manifest.py').write_text("import json; print(json.dumps({'skills':[{'name':'demo'}]}))\n")
        (self.repo / 'scripts/validate.py').write_text(
            "from pathlib import Path\nimport sys\nsys.exit('INVALID' in Path('skills/demo/SKILL.md').read_text())\n")
        self.git('add', '.'); self.git('commit', '-m', 'initial')
        self.git('remote', 'add', 'origin', str(self.remote)); self.git('push', '-u', 'origin', 'main')
        self.sync = S.Sync(self.repo)
        self.args = SimpleNamespace(skills_dir=str(self.skills), vault=str(self.vault),
                                    workspace=str(self.base), outputs=str(self.base / 'outputs'),
                                    repository='test/AIGC')
        self.sync.setup(self.args)
        # Local bare Git supplies real commit/push verification. Only GitHub account
        # discovery is mocked; production has no flag that bypasses that check.
        self.auth = patch.object(self.sync, 'verify_remote'); self.auth.start()

    def tearDown(self):
        self.auth.stop(); self.tmp.cleanup()

    def edit(self, word='new'):
        path = self.skills / 'demo/SKILL.md'
        path.write_text(path.read_text().replace('rule=old', 'rule=' + word))

    def remote_sha(self):
        return self.git('rev-parse', 'refs/heads/main', cwd=self.remote)

    def test_public_setup_excludes_personal_vault_and_unreviewed_skill(self):
        self.sync.state.unlink()
        self.args.visibility = 'public'
        self.args.exclude_skill = ['demo']
        result = self.sync.setup(self.args)
        config = self.sync.load()
        self.assertEqual(result['excluded_skills'], ['demo'])
        self.assertEqual(config['visibility'], 'public')
        self.assertEqual(config['units'], [])
        self.assertEqual(config['records'], {})
        with self.assertRaises(S.SyncError):
            self.sync.register(SimpleNamespace(skill=None, knowledge='agent/example.md'))

    def test_remote_visibility_must_match_explicit_configuration(self):
        self.auth.stop()
        try:
            with patch.object(self.sync, 'git', return_value='https://github.com/test/AIGC.git'):
                with patch.object(S, 'command', return_value='false'):
                    self.sync.verify_remote({'repository': 'test/AIGC', 'visibility': 'public'})
                    with self.assertRaises(S.SyncError):
                        self.sync.verify_remote({'repository': 'test/AIGC'})
                with patch.object(S, 'command', return_value='true'):
                    with self.assertRaises(S.SyncError):
                        self.sync.verify_remote({'repository': 'test/AIGC', 'visibility': 'public'})
        finally:
            self.auth.start()

    def test_setup_does_not_replace_historical_platform_differences(self):
        updates, _, _ = self.sync.plan(self.sync.load())
        self.assertEqual(updates, {})
        self.assertIn('runtime-config', (self.repo / 'skills/demo/SKILL.md').read_text())

    def test_publish_imports_delta_and_proves_remote_then_is_idempotent(self):
        self.edit(); first = self.sync.run()
        self.assertEqual(first['status'], 'synced')
        self.assertEqual(first['sha'], self.remote_sha())
        self.assertIn('path=runtime-config', (self.repo / 'skills/demo/SKILL.md').read_text())
        self.assertIn('rule=new', (self.repo / 'skills/demo/SKILL.md').read_text())
        self.assertEqual((self.repo / 'VERSION').read_text().strip(), '1.0.1')
        second = self.sync.run()
        self.assertEqual(second['status'], 'unchanged')
        self.assertEqual(second['sha'], first['sha'])

    def test_conflict_makes_no_candidate_write(self):
        self.edit()
        page = self.repo / 'skills/demo/SKILL.md'
        page.write_text(page.read_text().replace('rule=old', 'rule=other'))
        before = page.read_bytes()
        with self.assertRaises(S.SyncError): self.sync.run()
        self.assertEqual(page.read_bytes(), before)

    def test_failed_validation_does_not_commit_or_push_and_keeps_backup(self):
        before = self.remote_sha(); self.edit('INVALID')
        with self.assertRaises(S.SyncError): self.sync.run()
        self.assertEqual(self.remote_sha(), before)
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
        self.assertTrue(list((self.repo / '.local/sync-backups').glob('*/skills/demo/SKILL.md')))

    def test_push_failure_can_retry_without_duplicate_commit_or_version(self):
        self.edit(); real_git = self.sync.git
        def fail_push(*args):
            if args[0] == 'push': raise S.SyncError('Simulated offline')
            return real_git(*args)
        with patch.object(self.sync, 'git', side_effect=fail_push):
            with self.assertRaises(S.SyncError): self.sync.run()
        pending = self.git('rev-parse', 'HEAD')
        self.assertNotEqual(pending, self.remote_sha())
        result = self.sync.run()
        self.assertEqual(result['sha'], pending)
        self.assertEqual(self.remote_sha(), pending)
        self.assertEqual((self.repo / 'VERSION').read_text().strip(), '1.0.1')

    def test_existing_staging_is_preserved(self):
        self.edit(); (self.repo / 'README.md').write_text('user staging')
        self.git('add', 'README.md')
        with self.assertRaises(S.SyncError): self.sync.run()
        self.assertEqual(self.git('diff', '--cached', '--name-only'), 'README.md')

    def test_chinese_paths_are_published_without_git_quote_confusion(self):
        page = self.skills / 'demo/中文规则.md'; page.write_text('新增工作流规则', encoding='utf-8')
        result = self.sync.run()
        self.assertEqual(result['sha'], self.remote_sha())
        self.assertEqual((self.repo / 'skills/demo/中文规则.md').read_text(encoding='utf-8'), '新增工作流规则')

    def test_credential_in_source_stops_before_repository_write(self):
        before = self.remote_sha(); self.edit('ghp_' + 'A' * 40)
        with self.assertRaises(S.SyncError): self.sync.run()
        self.assertEqual(self.remote_sha(), before)
        self.assertIn('rule=old', (self.repo / 'skills/demo/SKILL.md').read_text())

    def test_out_of_scope_outgoing_commit_is_not_pushed(self):
        before = self.remote_sha(); (self.repo / 'private.txt').write_text('private data')
        self.git('add', 'private.txt'); self.git('commit', '-m', 'not workflow')
        with self.assertRaises(S.SyncError): self.sync.run()
        self.assertEqual(self.remote_sha(), before)

    def test_source_edit_after_publish_is_not_silently_acknowledged(self):
        self.edit(); real_checkpoint = self.sync.checkpoint
        def late_edit(config, observed=None):
            page = self.skills / 'demo/SKILL.md'
            page.write_text(page.read_text().replace('rule=new', 'rule=later'))
            return real_checkpoint(config, observed)
        with patch.object(self.sync, 'checkpoint', side_effect=late_edit): self.sync.run()
        updates, _, _ = self.sync.plan(self.sync.load())
        self.assertIn('rule=later', updates['skills/demo/SKILL.md'].decode())

    def advance_remote(self):
        other = self.base / 'other'
        self.git('clone', '--branch', 'main', str(self.remote), str(other))
        self.git('config', 'user.name', 'AIGC-other-test', cwd=other)
        self.git('config', 'user.email', 'other@example.invalid', cwd=other)
        self.git('config', 'commit.gpgsign', 'false', cwd=other)
        (other / 'README.md').write_text('remote update', encoding='utf-8')
        self.git('add', 'README.md', cwd=other); self.git('commit', '-m', 'remote update', cwd=other)
        self.git('push', 'origin', 'main', cwd=other)

    def test_remote_ahead_clean_checkout_fast_forwards_and_imports_local_skill(self):
        self.advance_remote(); self.edit(); result = self.sync.run()
        self.assertEqual(result['sha'], self.remote_sha())
        self.assertEqual((self.repo / 'README.md').read_text(), 'remote update')
        self.assertIn('rule=new', (self.repo / 'skills/demo/SKILL.md').read_text())

    def test_remote_ahead_with_dirty_checkout_stops_without_overwrite(self):
        self.advance_remote(); (self.repo / 'README.md').write_text('local unfinished')
        before = self.git('rev-parse', 'HEAD')
        with self.assertRaises(S.SyncError): self.sync.run()
        self.assertEqual(self.git('rev-parse', 'HEAD'), before)
        self.assertEqual((self.repo / 'README.md').read_text(), 'local unfinished')

    def test_diverged_branches_do_not_force_push(self):
        self.advance_remote(); (self.repo / 'README.md').write_text('local branch')
        self.git('add', 'README.md'); self.git('commit', '-m', 'local branch')
        before = self.remote_sha()
        with self.assertRaises(S.SyncError): self.sync.run()
        self.assertEqual(self.remote_sha(), before)

    def test_intentional_version_is_preserved(self):
        self.edit(); (self.repo / 'VERSION').write_text('1.1.0\n')
        self.sync.run()
        self.assertEqual((self.repo / 'VERSION').read_text().strip(), '1.1.0')

    def test_new_source_registration_preserves_existing_unsynced_changes(self):
        self.edit(); old = self.sync.load()['records']['skills/demo/SKILL.md']['sha']
        (self.skills / 'second').mkdir(); (self.repo / 'skills/second').mkdir()
        for path in [self.skills / 'second/SKILL.md', self.repo / 'skills/second/SKILL.md']:
            path.write_text('new Skill\n')
        (self.repo / 'sources.json').write_text(json.dumps({'skills': [{'name': 'demo'}, {'name': 'second'}]}))
        self.sync.register(SimpleNamespace(skill='second', knowledge=None))
        config = self.sync.load()
        self.assertEqual(config['records']['skills/demo/SKILL.md']['sha'], old)
        updates, _, _ = self.sync.plan(config)
        self.assertIn('rule=new', updates['skills/demo/SKILL.md'].decode())

    def test_resetting_existing_source_registration_is_refused(self):
        self.edit(); before = self.sync.state.read_bytes()
        with self.assertRaises(S.SyncError):
            self.sync.register(SimpleNamespace(skill='demo', knowledge=None))
        self.assertEqual(self.sync.state.read_bytes(), before)

if __name__ == '__main__':
    unittest.main()
