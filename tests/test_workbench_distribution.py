"""Real archive and bounded-helper regressions, not an LLM/filmmaking evaluation."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_workbench_pack as builder
import workbench_runtime as runtime


class WorkbenchDistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='aigc-pack-test-')
        cls.stage=Path(cls.temp.name)/'pack'
        builder.build(cls.stage)
        cls.plugin=cls.stage/'aigc-production-workbench'
        cls.integrity=json.loads((cls.plugin/'docs/source-integrity.json').read_text())

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_all_twenty_original_source_trees_are_direct_and_byte_identical(self):
        self.assertEqual(self.integrity['original_skill_count'],20)
        self.assertEqual(len({x['source'] for x in self.integrity['files']}),len(self.integrity['files']))
        for item in self.integrity['files']:
            with self.subTest(source=item['source']):
                original=(ROOT/item['source']).read_bytes()
                packed=(self.plugin/item['packaged']).read_bytes()
                self.assertEqual(original,packed)
                self.assertEqual(hashlib.sha256(packed).hexdigest(),item['sha256'])

    def test_eight_portable_entrypoints_not_twenty_eight(self):
        entries=list((self.plugin/'skills').glob('*/SKILL.md'))
        self.assertEqual(len(entries),8)
        self.assertEqual(sum(len(list((p.parent/'source-skills').glob('*/SKILL.md'))) for p in entries),20)

    def test_complete_dossiers_include_original_text_and_code(self):
        mapping=json.loads((self.plugin/'docs/module-map.json').read_text())
        for n,module in enumerate(mapping['modules']):
            dossier=(self.stage/'AIGC-GPT-compatible/knowledge'/f'{10+n:02d}_完整资料_{module["title"]}.md').read_text()
            for name in module['source_skills']:
                self.assertIn((ROOT/'skills'/name/'SKILL.md').read_bytes().decode('utf-8'),dossier)
                for source in (ROOT/'skills'/name).rglob('*'):
                    if source.is_file() and source.suffix in {'.py','.json','.md'} and not any(p in builder.SKIP for p in source.parts):
                        try:text=source.read_bytes().decode('utf-8')
                        except UnicodeDecodeError:continue
                        self.assertIn(text,dossier,source.as_posix())

    def test_shared_knowledge_has_no_dependency_on_a_personal_vault(self):
        self.assertTrue(self.integrity['shared_files'])
        for item in self.integrity['shared_files']:
            self.assertEqual((ROOT/item['source']).read_bytes(),(self.plugin/item['packaged']).read_bytes())
        self.assertIn('个人vault',(self.plugin/'skills/aigc-workbench/references/execution-contract.md').read_text())

    def test_knowledge_has_eighteen_files_with_explicit_music_limits(self):
        k=self.stage/'AIGC-GPT-compatible/knowledge'
        self.assertEqual(len(list(k.glob('*.md'))),18)
        self.assertIn('不是原Markdown字节副本',(k/'18_音乐候选目录.md').read_text())
        self.assertIn('未逐首试听',(k/'18_音乐候选目录.md').read_text())

    def test_existing_plugin_presentation_preserved_except_version(self):
        previous=ROOT/('.local/workbench-before-'+(ROOT/'VERSION').read_text().strip()+'.json')
        if not previous.is_file():previous=ROOT/'.local/workbench-before-1.3.0.json'
        if not previous.is_file():self.skipTest('No existing private plugin metadata in this test environment')
        old=json.loads(json.loads(previous.read_text())['contents']['plugin.json'])
        new=json.loads((self.plugin/'plugin.json').read_text());old['version']=new['version']
        mapping=json.loads((ROOT/'docs/workbench/module-map.json').read_text())
        old['extensions']['com.openai']['interface']['displayName']=mapping['display_name']
        if mapping.get('branding'):
            old['extensions']['com.openai']['interface']['logo']='./'+mapping['branding']['logo']
            old['extensions']['com.openai']['interface']['composerIcon']='./'+mapping['branding']['composer_icon']
        self.assertEqual(old,new)

    def run_helper(self,*args,success=True):
        result=subprocess.run([sys.executable,str(ROOT/'scripts/workbench_runtime.py'),*map(str,args)],capture_output=True,text=True)
        self.assertEqual(result.returncode==0,success,result.stderr)
        return json.loads(result.stdout if result.returncode==0 else result.stderr)

    def test_text_route_does_not_require_external_runtime(self):
        with patch('workbench_runtime.shutil.which',return_value=None):
            for task in ['script','video-prompt','poster-prompt','music-prompt','prompt-review','commercial-script']:
                self.assertEqual(runtime.preflight(task)['state'],'ready-for-text-work')

    def test_unavailable_source_is_not_reported_ready(self):
        result=runtime.preflight('script','/aigc-test/nonexistent-source.txt')
        self.assertEqual(result['state'],'preparation-available')
        self.assertIn('source-unavailable',result['blockers'])

    def test_manual_editor_handoff_needs_no_editor_cli_and_provider_stays_unverified(self):
        with patch('workbench_runtime.shutil.which',return_value=None):
            result=runtime.preflight('editor-project')
        self.assertEqual(result['state'],'ready-for-manual-editor-handoff')
        self.assertEqual(result['dependencies'],[])
        self.assertEqual(result['blockers'],[])
        self.assertIn('Do not install, probe or invoke',result['continue_now'])
        self.assertTrue(result['continue_now'])
        provider=runtime.preflight('video-generate')
        self.assertIn('provider-not-probed',provider['blockers'])
        self.assertNotIn('ready',provider['state'])

    def test_end_to_end_raw_xlsx_preserves_episodes_duplicates_accents_source(self):
        try:import openpyxl
        except ImportError:self.skipTest('XLSX optional dependency unavailable')
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);source=d/'source.xlsx';wb=openpyxl.Workbook();ws=wb.active
            ws.append(['章节','故事板','对应台词']);ws.append([1,1,'Mabel: Mãe...']);ws.append([None,2,'Mabel: Mãe...']);ws.append([2,1,'Celeste: She go home.']);ws.merge_cells('A2:A3');wb.save(source);wb.close()
            before=source.read_bytes();review=d/'review.json'
            self.run_helper('lines-check','--plugin-root',self.plugin,'--input',source,'--language','pt-BR','--output',review)
            plan=json.loads(review.read_text());self.assertEqual(len(plan['items']),3)
            self.assertTrue(all(not i['approve_numbers'] and not i['approve_punctuation'] for i in plan['items']))
            target=d/'result.xml'
            self.run_helper('lines-export','--plugin-root',self.plugin,'--input',source,'--language','pt-BR','--review',review,'--confirmed','--output',target)
            text=target.with_suffix('.txt').read_text();self.assertEqual(text.count('Mãe...'),2);self.assertIn('She go home.',text)
            self.assertIn('第1集',text);self.assertIn('第2集',text);self.assertEqual(source.read_bytes(),before)

    def test_end_to_end_only_approved_punctuation_changes(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);source=d/'input.txt';source.write_text('“Wait.”\nI have 21 cards.\n')
            review=d/'review.json';self.run_helper('lines-check','--plugin-root',self.plugin,'--input',source,'--language','en','--output',review)
            plan=json.loads(review.read_text());plan['items'][0]['approve_punctuation']=True;approved=d/'approved.json';approved.write_text(json.dumps(plan))
            target=d/'lines.xml';self.run_helper('lines-export','--plugin-root',self.plugin,'--input',source,'--language','en','--review',approved,'--confirmed','--output',target)
            text=target.with_suffix('.txt').read_text();self.assertIn('Wait.',text);self.assertNotIn('“',text);self.assertIn('I have 21 cards.',text)

    def test_changed_source_and_missing_confirmation_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);source=d/'input.txt';source.write_text('Wait.\n');review=d/'review.json'
            self.run_helper('lines-check','--plugin-root',self.plugin,'--input',source,'--output',review)
            args=['lines-export','--plugin-root',self.plugin,'--input',source,'--review',review,'--output',d/'out.xml']
            self.run_helper(*args,success=False)
            source.write_text('Changed.\n');self.run_helper(*args,'--confirmed',success=False)
            self.assertFalse((d/'out.xml').exists())

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);source=d/'input.txt';source.write_text('Wait.\n');target=d/'review.json';target.write_text('KEEP')
            self.run_helper('lines-check','--plugin-root',self.plugin,'--input',source,'--output',target,success=False)
            self.assertEqual(target.read_text(),'KEEP')

    def test_packaged_prompt_trim_preserves_source_and_non_target_cells(self):
        try:import openpyxl
        except ImportError:self.skipTest('XLSX optional dependency unavailable')
        with tempfile.TemporaryDirectory() as td:
            d=Path(td);source=d/'source.xlsx';target=d/'trimmed.xlsx'
            b=openpyxl.Workbook();s=b.active;s.append(['章节','提示词','对应台词'])
            s.append([1,'站位：A在左\n画面：\n0秒~5秒：A听着。\n时长：5秒','Wait...']);b.save(source);b.close();original=source.read_bytes()
            result=self.run_helper('trim-prompt-sections','--plugin-root',self.plugin,'--input',source,'--label','站位：','--write','--output',target)
            self.assertEqual(result['result']['changed'],1);self.assertTrue(result['result']['disk_verified'])
            b=openpyxl.load_workbook(target);self.assertEqual(b.active['B2'].value,'画面：\n0秒~5秒：A听着。\n时长：5秒');self.assertEqual(b.active['C2'].value,'Wait...');b.close()
            self.assertEqual(source.read_bytes(),original)

    def test_zero_exit_ledger_judgment_is_not_a_media_pass(self):
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/'ledger.json'
            for ledger,status in [({},'未触发此检查器'),({'context':{'user_requested_spatial_check':True}},'需要人工判断')]:
                source.write_text(json.dumps(ledger))
                result=self.run_helper('review-ledger','--plugin-root',self.plugin,'--input',source,'--mode','handoff')
                self.assertEqual(result['helper_exit_code'],0)
                self.assertEqual(result['result']['status'],status)
                self.assertIn('not raw-text',result['scope'])

    def test_real_synthetic_media_probe_only_claims_technical_metadata(self):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):self.skipTest('Optional media runtime unavailable')
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/'synthetic.mp4'
            subprocess.run(['ffmpeg','-v','error','-n','-f','lavfi','-i','color=c=black:s=32x32:r=10','-t','0.3','-an','-c:v','mpeg4',str(source)],check=True)
            result=self.run_helper('probe-media','--plugin-root',self.plugin,'--input',source)
            self.assertEqual(result['metadata']['streams'][0]['width'],32)
            self.assertIn('no perceptual QC',result['scope'])


if __name__=='__main__':unittest.main()
