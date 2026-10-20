#!/usr/bin/env python3
"""Validate bundle structure, Python syntax, risky imports and portable regressions."""
import argparse
import ast
import json
from pathlib import Path
import re
import subprocess
import sys
from source_manifest import snapshot

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', '__pycache__', '.venv', '.local', '.aigc-backups', 'node_modules'}

def structure():
    errors = []; count = 0
    for directory in sorted((ROOT / 'skills').iterdir()):
        entry = directory / 'SKILL.md'
        if not entry.is_file():
            continue
        count += 1
        text = entry.read_text(encoding='utf-8-sig')
        match = re.match(r'^---\n([\s\S]*?)\n---\n', text)
        if not match:
            errors.append(f'{directory.name}: missing frontmatter'); continue
        name = re.search(r'^name:\s*(.+)$', match.group(1), re.M)
        if not name or name.group(1).strip(' \"\'') != directory.name:
            errors.append(f'{directory.name}: incorrect name')
        if not re.search(r'^description:', match.group(1), re.M):
            errors.append(f'{directory.name}: missing description')
        # Only local supporting-resource links; external tools/knowledge use text contracts.
        for target in re.findall(r'\]\((references/[^)#]+|scripts/[^)#]+|assets/[^)#]+)\)', text):
            if not (directory / target).exists():
                errors.append(f'{directory.name}: missing {target}')
    if count != 20:
        errors.append(f'Expected 20 bundled Skills, found {count}; update this check when adding a Skill')
    catalog = json.loads((ROOT / 'skills/aigc-production-router/references/production-profiles.json').read_text(encoding='utf-8'))
    if len(catalog['profiles']) != 9:
        errors.append('Expected nine production profiles')
    manifest = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
    if manifest.get('version') != (ROOT / 'VERSION').read_text().strip():
        errors.append('Source manifest version is stale')
    entries = {item['name']: item for item in manifest['skills']}
    skill_names = {p.name for p in (ROOT / 'skills').iterdir() if (p / 'SKILL.md').is_file()}
    if set(entries) != skill_names:
        errors.append('Source manifest Skill list is stale')
    for name in skill_names & set(entries):
        files, sha = snapshot(ROOT / 'skills' / name)
        if files != entries[name]['files'] or sha != entries[name]['sha256_normalized_text']:
            errors.append(f'{name}: source manifest snapshot is stale')
    for page in [ROOT / 'README.md', *sorted((ROOT / 'docs').glob('*.md'))]:
        for link in re.findall(r'\]\(([^)]+)\)', page.read_text(encoding='utf-8')):
            if '://' in link or link.startswith('#'):
                continue
            if not (page.parent / link.split('#')[0]).exists():
                errors.append(f'{page.name}: missing document link {link}')
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(part in SKIP for part in path.relative_to(ROOT).parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix == '.py':
            try:
                ast.parse(path.read_text(encoding='utf-8-sig'), filename=relative)
            except (SyntaxError, UnicodeError) as exc:
                errors.append(f'{relative}: {type(exc).__name__}')
        if path.suffix in {'.md', '.py', '.yaml', '.json', '.sh'}:
            text = path.read_text(encoding='utf-8-sig')
            # No credential values are displayed; only the offending file and category.
            for category, pattern in [
                ('private-key', r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
                ('github-token', r'gh[pousr]_[A-Za-z0-9]{30,}'),
                ('api-key', r'sk-(?:proj-)?[A-Za-z0-9_-]{35,}')]:
                if re.search(pattern, text):
                    errors.append(f'{relative}: potential {category}')
            if re.search(r'/Users/[A-Za-z0-9_-]+/', text):
                errors.append(f'{relative}: personal home path')
        if path.suffix.lower() in {'.mp4', '.mov', '.wav', '.mp3', '.blend', '.pem', '.key'}:
            errors.append(f'{relative}: runtime media/credential file is excluded from the bundle')
    if errors:
        raise ValueError('\n'.join(errors))
    print(f'Bundle structure/syntax/privacy checks passed: {count} Skills, nine profiles', flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--structure-only', action='store_true')
    args = parser.parse_args()
    try:
        structure()
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr); raise SystemExit(1)
    if not args.structure_only:
        for command in [
            [sys.executable, str(ROOT / 'skills/aigc-production-router/tests/test_workflow.py')],
            [sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'skills/aigc-manga-video-director/tests'), '-v'],
            [sys.executable, str(ROOT / 'skills/aigc-audio-production/scripts/storyboard_lines/test_workflow.py')],
            [sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-v']]:
            subprocess.run(command, cwd=ROOT, check=True)

if __name__ == '__main__':
    main()
