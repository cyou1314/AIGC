"""Regression checks for confirmed extraction and desktop rule equivalence."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from build_lines_doc import apply_review, digit_tags, read_records
from dialogue_rules import clean_punctuation, convert_numbers, number_to_words

SCRIPT = Path(__file__).with_name('build_lines_doc.py')


class WorkflowTests(unittest.TestCase):
    def test_desktop_punctuation_fixtures_keep_words_and_case(self):
        examples = {
            'Mãe...': 'Mãe...', 'E o aluguel,...': 'E o aluguel,',
            'Como ele fez isso...?': 'Como ele fez isso?', 'all-in...-': 'all in',
            'bem-vinda—...': 'bem vinda', '¿No puedo perder？': 'No puedo perder?',
            'A BILLION DOLLAR LOSS?!': 'A BILLION DOLLAR LOSS?', 'Really!?': 'Really?',
            'No!!': 'No!', 'Mr.Blackwoodg, please wait.': 'Mr. Blackwoodg, please wait.',
            'I called Dr.Smith.': 'I called Dr. Smith.',
            'Dona Célia… muito obrigada.': 'Dona Célia... muito obrigada.',
            'Quinhentos mil……': 'Quinhentos mil...',
            '「It\'s not that Ethan can\'t understand you. You\'re just blind.」.': "It's not that Ethan can't understand you. You're just blind.",
            '“Wait.”': 'Wait.', '「Wait」!': 'Wait!', 'He said 「Wait」.': 'He said "Wait".',
            "She go home.": "She go home.",
        }
        for before, after in examples.items():
            with self.subTest(before=before):
                self.assertEqual(clean_punctuation(before), after)

    def test_desktop_number_fixtures_and_amount_priority(self):
        examples = [('21', 'pt-BR', '', 'vinte e um'), ('21', 'es-MX', '', 'veintiuno'),
            ('21', 'en', '', 'twenty one'), ('Par de 7', 'pt-BR', '', 'Par de setes'),
            ('9 de copas', 'pt-BR', '', 'nove de copas'), ('3 ou 8', 'pt-BR', '', 'três ou oito'),
            ('661', 'pt-BR', 'dados', 'seis, seis, um'), ('666', 'es-MX', 'dados', 'seis, seis, seis'),
            ('Pair of 7s', 'en', '', 'Pair of sevens'), ('661', 'en', 'dice', 'six, six, one'),
            ('$661', 'en', 'dice price', '$six hundred and sixty one')]
        for before, lang, context, after in examples:
            self.assertEqual(convert_numbers(before, lang, context), (after, ''))
        self.assertEqual(number_to_words(100, 'pt-BR'), 'cem')
        self.assertEqual(number_to_words(100, 'es-MX'), 'cien')
        self.assertEqual(number_to_words(1001, 'pt-BR'), 'mil e um')

    def test_ambiguous_numbers_stay_unchanged(self):
        for text in ['3.5', '1,000', '12:30', '2026-10-10', '50%', '-3', '007',
                     '3-5', 'A123', '661', '1000000', 'Call 12345678901', 'In year 2026']:
            converted, reason = convert_numbers(text, 'en')
            self.assertEqual(converted, text)
            self.assertTrue(reason, text)
        for text in ['2026-10-10', '-3', '2-3-5']:
            self.assertEqual(clean_punctuation(text), text)

    def run_cli(self, *args, success=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stderr)
        return result

    def test_check_outputs_summary_not_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, review = root / 'input.txt', root / 'review.json'
            source.write_text('“I have 21 cards!”\nShe go home.\n“Wait.”\n', encoding='utf-8')
            self.run_cli(source, '--language', 'en', '--output', review)
            self.assertFalse((root / 'review.md').exists())
            plan = json.loads(review.read_text())
            summary = plan['summary']
            self.assertEqual(summary['total'], 3)
            self.assertEqual(summary['punctuation_suggestions'], 2)
            self.assertEqual(summary['digit_count'], 1)
            self.assertEqual(summary['digit_tags'], ['普通数字'])
            self.assertEqual(summary['digit_label'], '1条（普通数字）')

    def test_digit_tags_classification(self):
        self.assertEqual(digit_tags('January 2016 too!'), ['年份'])
        self.assertEqual(digit_tags('In March 2017, they paid 5,000 dollars cash.'),
                         ['年份', '金额'])
        self.assertEqual(digit_tags('until 3 a.m.'), ['时间'])
        self.assertEqual(digit_tags('Case 0914. Conviction finalized.'), ['编号'])
        self.assertEqual(digit_tags('I have 21 cards'), ['普通数字'])

    def test_check_confirm_export_partial_and_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, review, approved = root / 'input.txt', root / 'review.json', root / 'approved.json'
            source.write_text('“I have 21 cards!”\nShe go home.\n“Wait.”\n“Wait.”\n', encoding='utf-8')
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            self.run_cli(source, '--language', 'en', '--output', review)
            plan = json.loads(review.read_text())
            self.assertEqual(len(plan['items']), 4)
            self.assertFalse(any(i['approve_punctuation'] or i['approve_numbers'] for i in plan['items']))
            self.assertFalse((root / 'draft.xml').exists())
            # Export without real confirmation marker is rejected.
            self.run_cli(source, '--mode', 'extract', '--language', 'en', '--review', review,
                         '--output', root / 'draft.xml', success=False)
            plan['items'][0]['approve_punctuation'] = True
            plan['items'][0]['approve_numbers'] = True
            approved.write_text(json.dumps(plan))
            self.run_cli(source, '--mode', 'extract', '--language', 'en', '--review', approved,
                         '--confirmed', '--output', root / 'draft.xml')
            self.assertEqual((root / 'draft.txt').read_text(), '台词\nI have twenty one cards!\nShe go home.\n“Wait.”\n“Wait.”\n')
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), digest)
            # Approved data cannot be repurposed to rewrite dialogue.
            expected = json.loads(review.read_text())
            tampered = copy.deepcopy(plan)
            tampered['items'][1]['original'] = 'She goes home.'
            with self.assertRaises(ValueError):
                apply_review(expected, tampered)
            changed = copy.deepcopy(plan)
            changed['items'][0]['number_text'] = 'I have forty cards!'
            with self.assertRaises(ValueError):
                apply_review(expected, changed)
            # Source drift invalidates previous approval.
            source.write_text('Different line.\n')
            self.run_cli(source, '--mode', 'extract', '--language', 'en', '--review', approved,
                         '--confirmed', '--output', root / 'other.xml', success=False)

    def test_numbers_only_retains_original_quotes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, review = root / 'input.txt', root / 'review.json'
            source.write_text('“I have 21 cards!”\n')
            self.run_cli(source, '--language', 'en', '--output', review)
            expected = json.loads(review.read_text())
            plan = copy.deepcopy(expected)
            plan['items'][0]['approve_numbers'] = True
            self.assertEqual(apply_review(expected, plan)['台词'], ['“I have twenty one cards!”'])

    def test_manual_numbers_cannot_be_approved_by_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, review = root / 'input.txt', root / 'review.json'
            source.write_text('I paid 3.5 dollars.\n')
            self.run_cli(source, '--language', 'en', '--output', review)
            expected = json.loads(review.read_text())
            plan = copy.deepcopy(expected)
            plan['items'][0]['approve_numbers'] = True
            with self.assertRaises(ValueError):
                apply_review(expected, plan)

    def test_workbook_merged_chapters_order_duplicates_and_no_writeback(self):
        try:
            import openpyxl
        except ImportError:
            self.skipTest('openpyxl not installed')
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'input.xlsx'
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(['章节', '故事板', '对应台词', '提示词'])
            ws.append([1, 's1', 'Aki: “I have 21 cards.”\nAki: She go home.', 'cards'])
            ws.append([None, 's2', 'Aki: Wait.\nAki: Wait.', ''])
            ws.append([2, 's3', 'Aki: Different.', ''])
            ws.merge_cells('A2:A3')
            wb.save(source)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            records, _ = read_records(source, episodes='1')
            self.assertEqual([i['original'] for i in records], ['“I have 21 cards.”', 'She go home.', 'Wait.', 'Wait.'])
            self.assertEqual([i['row'] for i in records], [2, 2, 3, 3])
            self.assertEqual([i['shot'] for i in records], ['s1', 's1', 's2', 's2'])
            read_records(source, episodes='2')
            again, _ = read_records(source, episodes='1')
            self.assertEqual(records, again)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), digest)

    def test_existing_review_and_export_companion_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, review = root / 'input.txt', root / 'review.json'
            source.write_text('Keep me.', encoding='utf-8')
            review.write_text('previous review', encoding='utf-8')
            self.run_cli(source, '--output', review, success=False)
            self.assertEqual(review.read_text(), 'previous review')
            review.unlink()
            self.run_cli(source, '--output', review)
            companion = root / 'draft.txt'
            companion.write_text('prior transcript', encoding='utf-8')
            self.run_cli(source, '--mode', 'extract', '--review', review, '--confirmed',
                         '--output', root / 'draft.xml', success=False)
            self.assertFalse((root / 'draft.xml').exists())
            self.assertEqual(companion.read_text(), 'prior transcript')

    def test_source_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'input.txt'
            source.write_text('Keep me.')
            self.run_cli(source, '--output', source, success=False)
            self.assertEqual(source.read_text(), 'Keep me.')


if __name__ == '__main__':
    unittest.main()
