"""Observable route/state regressions. Fixtures prove bookkeeping, not generation quality."""
import argparse
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

PLAN = module('workflow_plan', ROOT / 'aigc-production-router/scripts/workflow_plan.py')
STATE = module('project_state', ROOT / 'obsidian-codex-knowledge-loop/scripts/project_state.py')

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='aigc-workflow-test-')
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_state(self, *args):
        parsed = STATE.build_parser().parse_args(args)
        with contextlib.redirect_stdout(io.StringIO()):
            parsed.func(parsed)

    def project(self, domain='image', name='项目甲'):
        self.run_state('init', '--name', name, '--domain', domain, '--goal', '用户实际交付目标',
                       '--next', '制作小样', '--vault', str(self.base / 'vault'), '--output-root', str(self.base / 'outputs'))
        return self.base / 'vault/projects' / f'{name}.md'

    def artifact(self, name='asset.png'):
        # Nonempty placeholder for a file-existence test; not actual generated media.
        path = self.base / name
        path.write_text('FILE EXISTENCE FIXTURE ONLY', encoding='utf-8')
        return path

    def add_receipt(self, project, asset, status='候选'):
        self.run_state('receipt', '--project', str(project), '--block', 'A01', '--prompt-version', 'v1',
                       '--file', str(asset), '--status', status)

    def test_non_narrative_routes_do_not_activate_story_conductor(self):
        for domain in ['image', 'marketing', 'presenter', 'post', 'audio', 'three-d', 'knowledge', 'digital']:
            with self.subTest(domain=domain):
                plan = PLAN.plan(domain, discovered={})
                self.assertNotEqual(plan['selected_lead'], 'aigc-project-prompt-loop')
                self.assertEqual(plan['execution'], 'not-executed')
                self.assertTrue(plan['acceptance'])

    def test_explicit_faceless_and_raw_footage_leads(self):
        self.assertEqual(PLAN.plan('presenter', lead='faceless-video', discovered={})['selected_lead'], 'faceless-video')
        self.assertEqual(PLAN.plan('post', lead='auto-edit-video', discovered={})['selected_lead'], 'auto-edit-video')
        with self.assertRaises(ValueError):
            PLAN.plan('image', lead='aigc-project-prompt-loop', discovered={})

    def test_new_narrative_project_keeps_project_conductor(self):
        self.assertEqual(PLAN.plan('narrative', discovered={})['selected_lead'], 'aigc-project-prompt-loop')

    def test_seedance_shot_handoff_can_select_video_director(self):
        result = PLAN.plan('narrative', lead='aigc-manga-video-director', discovered={})
        self.assertEqual(result['selected_lead'], 'aigc-manga-video-director')
        self.assertEqual(result['execution'], 'not-executed')

    def test_still_image_edit_uses_image_director(self):
        self.assertEqual(PLAN.plan('image', discovered={})['selected_lead'], 'aigc-image-director')

    def test_existing_jianying_project_uses_postproduction_specialist(self):
        result = PLAN.plan('post', discovered={})
        self.assertEqual(result['selected_lead'], 'jianying-editing')
        self.assertNotEqual(result['selected_lead'], 'aigc-manga-video-director')

    def test_discovery_does_not_imply_execution_or_login(self):
        result = PLAN.plan('image', discovered={'aigc-image-director': ['/local/SKILL.md']})
        self.assertEqual(result['candidates'][0]['discovery'], 'skill-discovered')
        self.assertEqual(result['execution'], 'not-executed')
        self.assertIn('checks required', result['readiness'])

    def test_nine_profiles_initialize_and_validate(self):
        for domain in PLAN.profiles():
            with self.subTest(domain=domain):
                page = self.project(domain, name=domain)
                self.run_state('validate', '--project', str(page), '--check-files')
                text = page.read_text(encoding='utf-8')
                self.assertIn('- 已确认预算：未知', text)
                self.assertNotIn('| A01 |', text)

    def test_unspecified_project_stays_pending(self):
        page = self.project('pending')
        text = page.read_text(encoding='utf-8')
        self.assertIn('domain: pending', text)
        self.assertIn('- 主导Skill：aigc-production-router', text)
        self.assertNotIn('- 主导Skill：aigc-project-prompt-loop', text)

    def test_missing_asset_does_not_mutate_page(self):
        page = self.project()
        before = page.read_bytes()
        with self.assertRaises(ValueError):
            self.add_receipt(page, self.base / 'missing.mp4')
        self.assertEqual(page.read_bytes(), before)

    def test_receipt_retries_and_status_transitions_are_idempotent(self):
        page = self.project(); asset = self.artifact()
        self.add_receipt(page, asset)
        self.add_receipt(page, asset)
        self.add_receipt(page, asset, status='采用')
        rows = STATE.rows(page.read_text(encoding='utf-8'), '生成回执', 5)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][3], '采用')
        self.run_state('validate', '--project', str(page), '--check-files')

    def test_invalid_status_and_nonvideo_final_are_rejected(self):
        page = self.project(); asset = self.artifact()
        for status in ['已通过', '成片']:
            with self.subTest(status=status), self.assertRaises(ValueError):
                self.add_receipt(page, asset, status=status)

    def test_snapshot_synchronizes_resume_and_keeps_literal_backslashes(self):
        page = self.project()
        next_step = r'读取 C:\source\take1，并保持原声'
        self.run_state('snapshot', '--project', str(page), '--next', next_step, '--stage', '制作')
        text = page.read_text(encoding='utf-8')
        self.assertIn('- 唯一下一步：' + next_step, text)
        self.assertIn('- 下次从这里继续：' + next_step, text)

    def test_passed_delivery_requires_evidence_and_preserves_generation_state(self):
        page = self.project('knowledge'); asset = self.artifact('draft.md')
        args = ['delivery', '--project', str(page), '--item', '研究草稿', '--version', 'v1',
                '--file', str(asset), '--kind', '文本', '--qc', '通过']
        with self.assertRaises(ValueError):
            self.run_state(*args)
        evidence = self.artifact('check.md')
        self.run_state(*args, '--evidence', str(evidence))
        text = page.read_text(encoding='utf-8')
        self.assertEqual(STATE.rows(text, '生成回执', 5), [])
        self.assertIn('- 项目状态：进行中', text)
        self.run_state('validate', '--project', str(page), '--check-files')

    def test_force_init_keeps_a_recoverable_backup(self):
        page = self.project()
        original = page.read_bytes()
        self.run_state('init', '--name', '项目甲', '--domain', 'audio', '--goal', '音频', '--next', '试听',
                       '--vault', str(self.base / 'vault'), '--force')
        backups = list(page.parent.glob('项目甲.md.backup-*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)

    def test_legacy_project_can_receive_receipts_without_reinitialization(self):
        page = self.base / 'legacy.md'
        page.write_text('# 旧项目\n\n## 当前快照\n\n- 唯一下一步：继续\n- 最近生成文件：无\n\n'
                        '## 当前知识胶囊\n\n- 主导Skill：aigc-project-prompt-loop\n\n'
                        '## 生成回执\n\n' + STATE.RH + '\n|---|---|---|---|---|\n', encoding='utf-8')
        self.add_receipt(page, self.artifact())
        self.run_state('validate', '--project', str(page), '--check-files')
        self.assertIn('# 旧项目', page.read_text(encoding='utf-8'))

    def test_empty_relative_assets_and_multiline_fields_are_rejected(self):
        page = self.project()
        empty = self.base / 'empty.wav'; empty.touch()
        for asset in [empty, Path('relative.mp4')]:
            with self.subTest(asset=asset), self.assertRaises(ValueError):
                self.add_receipt(page, asset)
        with self.assertRaises(ValueError):
            self.run_state('snapshot', '--project', str(page), '--next', '正常\n## 注入')

    def test_table_path_with_pipe_survives_validation(self):
        page = self.project(); asset = self.artifact('product|alternate.png')
        self.add_receipt(page, asset)
        self.run_state('validate', '--project', str(page), '--check-files')

if __name__ == '__main__':
    unittest.main(verbosity=2)
