"""Design route, evidence and scoped-adapter regressions; not aesthetic ratings."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/aigc-production-router/scripts'))
from workflow_plan import plan

spec = importlib.util.spec_from_file_location('review_gate', ROOT / 'skills/aigc-design-review/scripts/review_gate.py')
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)


class DesignWorkflowTests(unittest.TestCase):
    def review(self, level='brief', **updates):
        value = {'domain': 'poster', 'evidence_level': level, 'findings': [], 'decision': 'needs-review'}
        value.update(updates); return value

    def test_poster_and_ui_have_direct_specialist_leads(self):
        self.assertEqual(plan('image', 'canvas-design', {})['selected_lead'], 'canvas-design')
        self.assertEqual(plan('digital', 'frontend-design', {})['selected_lead'], 'frontend-design')
        self.assertEqual(plan('image', discovered={})['selected_lead'], 'aigc-image-director')
        self.assertEqual(plan('narrative', discovered={})['selected_lead'], 'aigc-project-prompt-loop')

    def test_review_routes_do_not_claim_execution(self):
        for domain in ['image', 'digital']:
            self.assertEqual(plan(domain, 'aigc-design-review', {})['execution'], 'not-executed')
        with self.assertRaises(ValueError):
            plan('audio', 'canvas-design', {})

    def test_brief_cannot_be_accepted_as_render(self):
        with self.assertRaises(ValueError):
            G.evaluate(self.review(decision='accepted'))

    def test_missing_render_evidence_blocks(self):
        with self.assertRaises(ValueError):
            G.evaluate(self.review('render', artifacts=['missing.png']))

    def test_blocker_cannot_be_offset_by_good_findings(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder).resolve() / 'artifact.svg'; file.write_text('<svg/>')
            finding = dict(severity='blocker', evidence='wrong confirmed date', impact='incorrect information',
                           fix='restore approved date', preserve='illustration', verify='compare copy')
            review = self.review('render', artifacts=[str(file)], findings=[finding], decision='accepted')
            with self.assertRaises(ValueError):
                G.evaluate(review)
            review['decision'] = 'repair'
            self.assertEqual(G.evaluate(review)['gate'], 'blocked')

    def test_ui_interaction_needs_checks_and_is_only_bookkeeping(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder).resolve() / 'ui.html'; file.write_text('<button>筛选</button>')
            value = self.review('interaction', domain='ui', artifacts=[str(file)])
            with self.assertRaises(ValueError):
                G.evaluate(value)
            value['interaction_checks'] = ['Observed filter changes visible item count']
            self.assertIn('bookkeeping-only', G.evaluate(value)['proof'])


if __name__ == '__main__':
    unittest.main()
