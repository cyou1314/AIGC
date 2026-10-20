#!/usr/bin/env python3
"""Build private eight-module plugin, GPT compatibility files and original Codex snapshot.

No account writes, network, installation, publishing or generation. Output is a new
staging directory; validate manifests, exact 20-Skill coverage, archive paths and
contained references before any upload. Run from a source checkout.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile

from workbench_distribution import enrich

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs/workbench'
SKIP = {'.git', '.local', '__pycache__', '.venv', 'node_modules', '.aigc-backups'}
GUIDES = ['使用手册.md', '安装指南.md', '常用指令速查.md', '项目快照模板.md', 'Preview_验收清单.md', '最简单使用方式.md', '执行合同.md', '验收说明.md']
# Runtime-free reference material, preserved as background under each module.
REFERENCES = {
 'aigc-writing': [('aigc-screenwriter', 'references/scene-and-dialogue.md'), ('aigc-screenwriter', 'references/script-duration-planning.md')],
 'aigc-directing': [('aigc-manga-video-director', 'references/company-directing-standard.md'), ('aigc-manga-video-director', 'references/shot-language.md'), ('aigc-manga-video-director', 'references/seedance-preflight-and-bilingual.md')],
 'aigc-visuals': [('aigc-image-director', 'references/company-short-drama-poster.md'), ('aigc-image-director', 'references/company-poster-prototypes.md')],
 'aigc-sound': [('aigc-audio-production', 'references/company-scoring-standard.md'), ('aigc-audio-production', 'references/gemini-short-drama-music.md'), ('aigc-audio-production', 'references/storyboard-lines.md'), ('aigc-audio-production', 'references/dialogue-cleanup-rules.md')],
 'aigc-review': [('aigc-manga-video-director', 'references/company-prompt-review.md'), ('aigc-manga-video-director', 'references/reviewer-handoff.md')],
}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def zip_directory(directory, output):
    files = sorted(p for p in directory.rglob('*') if p.is_file())
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:
            if p.is_symlink():
                raise ValueError('Symlinks are not allowed in distribution')
            z.write(p, (Path(directory.name) / p.relative_to(directory)).as_posix())
    verify_archive(output)


def verify_archive(path):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError('Corrupt archive')
        for info in z.infolist():
            p = Path(info.filename)
            if p.is_absolute() or '..' in p.parts:
                raise ValueError('Unsafe archive path')
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Archive contains a symlink')


def source_snapshot(output):
    names = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT,
                           capture_output=True, check=True).stdout.decode().split('\0')
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for relative in sorted(set(filter(None, names))):
            p = ROOT / relative
            if any(part in SKIP for part in Path(relative).parts):
                continue
            if p.name in {'aigc-workflow.json', 'aigc-installed.json', '.env', 'credentials.json', 'token.json'} or p.name.startswith('.env.'):
                continue
            if p.is_symlink():
                resolved = p.resolve()
                if not resolved.is_relative_to(ROOT):
                    raise ValueError('Source symlink escapes repository')
                if resolved.is_dir():
                    for child in sorted(resolved.rglob('*')):
                        if child.is_file() and not child.is_symlink() and not any(x in SKIP for x in child.relative_to(resolved).parts):
                            z.write(child, (Path('AIGC') / relative / child.relative_to(resolved)).as_posix())
                    continue
            if p.is_file():
                z.write(p, (Path('AIGC') / relative).as_posix())
    verify_archive(output)


def adapt_reference(text):
    # Supporting documents are background methods, not mandatory host paths or
    # separately installed source Skills. Keep wording and source attribution.
    text = re.sub(r'\[([^\]]+)\]\((?!https?://)([^)]+)\)', r'\1（原参考：\2）', text)
    return ('> 来源方法参考。当前工作台指令、实际用户权限和本模块流程优先。原路径/原Skill名只是来源定位；'
            '需要时参阅随包Codex源快照，不声称当前宿主已安装该工具。\n\n' + text)


def build(output):
    if output.exists():
        raise ValueError('Output already exists; choose a new directory to preserve prior artifacts')
    output.mkdir(parents=True)
    mapping = json.loads((DOCS / 'module-map.json').read_text())
    version = (ROOT / 'VERSION').read_text().strip()
    if mapping['version'] != version:
        raise ValueError('Pack version differs from repository version')
    modules = mapping['modules']
    expected = {p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md')}
    flattened = [name for m in modules for name in m['source_skills']]
    if len(flattened) != len(set(flattened)) or set(flattened) != expected or len(modules) != 8:
        raise ValueError('Module coverage must map every source Skill exactly once')
    knowledge = sorted((DOCS / 'knowledge').glob('*.md'))
    if len(knowledge) != 9:
        raise ValueError('Expected one index plus eight knowledge modules')
    master = (DOCS / 'GPT_主指令.txt').read_text()
    if len(master) > 7500 or not master.strip():
        raise ValueError('Master instructions empty or too long for intended compact configuration')
    plugin = output / mapping['pack_name']
    plugin.mkdir()
    manifest = {
      '$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
      'name': mapping['pack_name'], 'version': version,
      'description': 'Private AIGC workflow: eight organized entrypoints covering twenty source Skills and company extensions. No bundled remote services.',
      'author': {'name': 'AIGC Workflow'},
      'extensions': {'com.openai': {'interface': {
        'displayName': mapping['display_name'],
        'shortDescription': '剧本、分镜、海报、声音与返修的一站式工作台',
        'longDescription': '按任务选择八个专业入口，保留Seedance 2.5公司标准、原文与素材保护、实际证据及工具能力边界。附中文手册、GPT兼容文件和原20技能Codex源快照。',
        'developerName': 'AIGC Workflow', 'category': 'Productivity', 'capabilities': [],
        'defaultPrompt': ['按我的材料和目标选择一个主模块，直接完成所需结果。', '根据确认剧情写30秒Seedance 2.5完整版提示词。', '只检查这两条分镜的空间、道具和口型连续性。']
      }}}
    }
    previous = ROOT / ('.local/workbench-before-' + version + '.json')
    if not previous.is_file():
        previous = ROOT / '.local/workbench-before-1.3.0.json'
    if previous.is_file():
        saved = json.loads(previous.read_text())
        old_manifest = json.loads(saved['contents']['plugin.json'])
        if old_manifest.get('name') != mapping['pack_name']:
            raise ValueError('Existing plugin identity mismatch')
        manifest = old_manifest
        manifest['version'] = version
        # Host-generated compatibility metadata remains synchronized.
        if '.codex-plugin/plugin.json' in saved['contents']:
            overlay = json.loads(saved['contents']['.codex-plugin/plugin.json'])
            overlay['version'] = version
            overlay['interface']['displayName'] = mapping['display_name']
            write(plugin / '.codex-plugin/plugin.json', json.dumps(overlay, ensure_ascii=False, indent=2)+'\n')
    manifest['extensions']['com.openai']['interface']['displayName'] = mapping['display_name']
    branding = mapping.get('branding')
    if branding:
        icon_source = (DOCS / branding['source_file']).resolve()
        if not icon_source.is_relative_to(DOCS.resolve()) or not icon_source.is_file() or icon_source.is_symlink():
            raise ValueError('Brand icon source must be a contained regular file')
        icon_bytes = icon_source.read_bytes()
        if hashlib.sha256(icon_bytes).hexdigest() != branding['sha256']:
            raise ValueError('Brand icon differs from the selected original')
        if (icon_bytes[:8] != b'\x89PNG\r\n\x1a\n' or len(icon_bytes) > 5 * 1024 * 1024
                or not 48 <= int.from_bytes(icon_bytes[16:20], 'big') <= 4096
                or icon_bytes[16:20] != icon_bytes[20:24]):
            raise ValueError('Expected a square PNG icon, 48-4096 pixels, at most 5 MiB')
        for field, key in [('logo', 'logo'), ('composerIcon', 'composer_icon')]:
            target = Path(branding[key])
            if target.is_absolute() or '..' in target.parts or not target.parts or target.parts[0] != 'assets':
                raise ValueError('Brand icon target must be inside assets')
            icon_target = plugin / target
            icon_target.parent.mkdir(parents=True, exist_ok=True)
            icon_target.write_bytes(icon_bytes)
            manifest['extensions']['com.openai']['interface'][field] = './' + target.as_posix()
        if previous.is_file() and '.codex-plugin/plugin.json' in saved['contents']:
            for field in ['logo', 'composerIcon']:
                overlay['interface'][field] = manifest['extensions']['com.openai']['interface'][field]
            write(plugin / '.codex-plugin/plugin.json', json.dumps(overlay, ensure_ascii=False, indent=2)+'\n')
    if len(manifest['extensions']['com.openai']['interface']['shortDescription']) > 30:
        raise ValueError('Plugin subtitle is too long')
    write(plugin / 'plugin.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    write(plugin / 'README.md', (DOCS / '使用手册.md').read_text() + '\n\n插件内docs包含安装指南/验收/快照，gpt-compatible包含可粘贴指令与18份分层知识。assets中的两个ZIP分别为GPT兼容包和Codex20技能源快照；它们是导入/复现材料，不是额外自动激活的工具。\n')
    for guide in GUIDES:
        write(plugin / 'docs' / guide, (DOCS / guide).read_text())
    write(plugin / 'docs/module-map.json', json.dumps(mapping, ensure_ascii=False, indent=2) + '\n')
    for m in modules:
        skill = plugin / 'skills' / m['name']
        front = '---\nname: ' + m['name'] + '\ndescription: ' + json.dumps(m['description'], ensure_ascii=False) + '\n---\n\n'
        common = ('当前入口为八模块适配之一，覆盖原Skill：' + '、'.join(m['source_skills']) + '。\n\n'
                  '先按真实用户目标和材料工作；只读与修改、提示词与实际生成分别处理。'
                  '只加载本入口所需参考，不启动所有模块。宿主缺工具时仍可完成文本工作，'
                  '不能声称已执行脚本/CLI/API、生成文件或验证媒体。原始资料中的路径/默认不能覆盖当前用户锁。'
                  '用户明确不使用剪映/CapCut CLI，不安装、探测或调用；后期交手动剪辑表与素材/字幕/导出清单，原CLI资料仅历史参考。\n\n'
                  '阅读 [模块方法](references/workflow.md)。项目/跨模块请求按工作台主入口分流，'
                  '已有明确专业请求直接完成。\n')
        if m['name'] == 'aigc-workbench':
            common += '\n' + master + '\n\n原20个Skill的覆盖表见 [总索引](references/index.md)。\n'
            write(skill / 'references/index.md', (DOCS / 'knowledge/00_总索引与调用地图.md').read_text())
        else:
            # Core locks belong in active skill instructions, not only retrieval.
            common += '\n' + master[master.index('【授权与事实】'):master.index('【视频】')] + '\n'
        write(skill / 'SKILL.md', front + '# ' + m['title'] + '\n\n' + common)
        write(skill / 'references/workflow.md', (DOCS / 'knowledge' / m['knowledge_file']).read_text())
        descriptions = {'aigc-workbench':'选择任务入口、项目接续与交付归档', 'aigc-writing':'剧本、剧情诊断与获准对白修复',
                        'aigc-directing':'观看驱动的Seedance 2.5分镜与提示词', 'aigc-visuals':'人物场景、海外海报与精确标题版式',
                        'aigc-sound':'台词提取、声音分析、配乐双框和音效', 'aigc-postproduction':'工程副本、保守剪辑和媒体工具交接',
                        'aigc-review':'文本、图像与实片的有据审查与局部返修', 'aigc-commercial-digital':'真实产品创意与可用UI网页设计'}
        agent = 'interface:\n  display_name: '+json.dumps(m['title'], ensure_ascii=False)+'\n  short_description: '+json.dumps(descriptions[m['name']], ensure_ascii=False)+'\n  default_prompt: '+json.dumps('Use $'+m['name']+' to complete the requested '+m['title']+' task within the supplied evidence and scope.',ensure_ascii=False)+'\n'
        write(skill / 'agents/openai.yaml', agent)
        refs = []
        for source, relative in REFERENCES.get(m['name'], []):
            source_path = ROOT / 'skills' / source / relative
            target = 'source-' + source_path.stem + '.md'
            write(skill / 'references' / target, adapt_reference(source_path.read_text()))
            refs.append('- ['+source_path.stem+'](references/'+target+')')
        if refs:
            with (skill / 'SKILL.md').open('a') as handle:
                handle.write('\n## 按需方法参考\n\n'+'\n'.join(refs)+'\n')
    # Working Python helpers only; no SDK/API credentials or automatic publishing.
    shutil.copytree(ROOT / 'skills/aigc-audio-production/scripts/storyboard_lines', plugin / 'skills/aigc-sound/scripts/storyboard_lines', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    review = ROOT / 'skills/aigc-manga-video-director'
    (plugin / 'skills/aigc-review/scripts').mkdir(parents=True)
    for name in ['prompt_review_checks.py', 'LICENSE.prompt-review-checks']:
        shutil.copy2(review / 'scripts' / name, plugin / 'skills/aigc-review/scripts' / name)
    # Keep the imported MIT notice next to adapted references as well.
    shutil.copy2(review / 'scripts/LICENSE.prompt-review-checks', plugin / 'skills/aigc-review/LICENSE')
    compatibility = output / 'AIGC-GPT-compatible'
    compatibility.mkdir()
    if branding:
        icon = compatibility / branding['logo']
        icon.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plugin / branding['logo'], icon)
    for name in ['GPT_主指令.txt','GPT_配置清单.json',*GUIDES]:
        shutil.copy2(DOCS / name, compatibility / name)
    shutil.copytree(DOCS / 'knowledge', compatibility / 'knowledge')
    shutil.copy2(DOCS / 'module-map.json', compatibility / 'module-map.json')
    write(compatibility / 'README.md', '先读安装指南；主指令粘贴Instructions，knowledge内18个文件单独上传。JSON仅人工配置清单，ZIP不是GPT技能安装接口。工具能力需当前宿主支持。\n')
    full_report = enrich(ROOT, DOCS, plugin, compatibility, mapping)
    write(compatibility / 'README.md', '先读安装指南和最简单使用方式。主指令粘贴Instructions，knowledge内18份文件分别上传（9导航＋8完整资料＋1待核实音乐候选）。JSON是人工清单，ZIP不等于GPT自动安装。实际工具另验。\n')
    compat_zip = output / ('AIGC-GPT-compatible-' + version + '.zip')
    zip_directory(compatibility, compat_zip)
    snapshot = output / ('AIGC-Codex-source-' + version + '.zip')
    source_snapshot(snapshot)
    (plugin / 'assets').mkdir(exist_ok=True)
    shutil.copy2(compat_zip, plugin / 'assets' / compat_zip.name)
    shutil.copy2(snapshot, plugin / 'assets' / snapshot.name)
    shutil.copytree(compatibility, plugin / 'gpt-compatible')
    write(plugin / 'THIRD_PARTY_NOTICES.md', (ROOT / 'THIRD_PARTY_NOTICES.md').read_text() + '\n\n本八模块适配仅供私有工作流。完整源码包保留各自许可证，未给无许可证的公司包授予公开再分发权。包内帮助文档不构成平台功能保证。\n')
    plugin_zip = output / (mapping['pack_name'] + '-' + version + '.zip')
    # Inspect active skill components and relative links before packing.
    for m in modules:
        p = plugin / 'skills' / m['name'] / 'SKILL.md'
        body = p.read_text()
        if not body.startswith('---\nname: '+m['name']+'\n'):
            raise ValueError('Bad skill frontmatter')
        for target in re.findall(r'\]\(([^)]+)\)', body):
            if '://' not in target and not (p.parent / target).is_file():
                raise ValueError('Missing packaged reference: '+target)
    zip_directory(plugin, plugin_zip)
    payload = {'version':version, 'modules':len(modules), 'source_skills':len(expected), 'knowledge_files':full_report['knowledge_file_count'], 'full_source':full_report,
               'master_instruction_characters':len(master), 'platform_behavior':'not tested in target account',
               'archives':[]}
    for p in [plugin_zip, compat_zip, snapshot]:
        payload['archives'].append({'name':p.name, 'path':str(p), 'bytes':p.stat().st_size, 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    write(output / 'BUILD_REPORT.json', json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(payload,ensure_ascii=False,indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='New absolute staging output directory')
    args = parser.parse_args()
    output = Path(args.output).expanduser().resolve()
    if output == ROOT or output.is_relative_to(ROOT):
        parser.error('Choose a staging directory outside the source repository')
    build(output)


if __name__ == '__main__':
    main()
