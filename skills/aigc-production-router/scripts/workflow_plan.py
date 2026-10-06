#!/usr/bin/env python3
"""Local AIGC profile planning and discovery; never invokes production services."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from workflow_paths import runtime_paths

CATALOG = Path(__file__).resolve().parents[1] / 'references/production-profiles.json'

def profiles():
    return json.loads(CATALOG.read_text(encoding='utf-8'))['profiles']

def discover_skills():
    codex = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    roots = [Path(__file__).resolve().parents[2], codex / 'skills', Path.home() / '.agents/skills', codex / 'plugins/cache']
    found = {}
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob('SKILL.md'):
            try:
                text = path.read_text(encoding='utf-8-sig')
            except (OSError, UnicodeError):
                continue
            match = re.search(r'^name:\s*[\"\']?([^\n\"\']+)', text, re.M)
            if match:
                found.setdefault(match.group(1).strip(), []).append(str(path))
    return found

def candidates(name, found):
    return found.get(name, found.get(name.split(':')[-1], []))

def plan(domain, lead=None, discovered=None):
    profile = profiles()[domain]
    found = discovered if discovered is not None else discover_skills()
    names = list(dict.fromkeys([profile['lead']] + profile.get('alternatives', []) + profile['support']))
    if lead is not None and lead not in names:
        raise ValueError(f'{lead} is not a candidate for {domain}')
    return {
        'domain': domain, 'label': profile['label'], 'selected_lead': lead or profile['lead'],
        'deliverables': profile['deliverables'], 'acceptance': profile['acceptance'], 'boundary': profile['boundary'],
        'candidates': [{'name': name, 'discovery': 'skill-discovered' if candidates(name, found) else 'not-discovered',
                        'paths': candidates(name, found)} for name in names],
        'execution': 'not-executed',
        'readiness': 'provider/runtime/project checks required only for the selected action',
        'note': 'Candidates are alternatives or conditional collaborators, not an execution sequence.'
    }

def inventory():
    found = discover_skills()
    bins = {name: shutil.which(name) for name in ['ffmpeg', 'ffprobe', 'capcut', 'blender', 'whisper-cli', 'whisper-cpp']}
    workspace, _, _ = runtime_paths()
    adapter = workspace / 'runtime/bin' / ('ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
    if bins['ffmpeg'] is None and adapter.is_file() and os.access(adapter, os.X_OK):
        bins['ffmpeg'] = str(adapter)
    blender = Path('/Applications/Blender.app/Contents/MacOS/Blender')
    if bins['blender'] is None and blender.is_file() and os.access(blender, os.X_OK):
        bins['blender'] = str(blender)
    return {'profiles': {key: plan(key, discovered=found) for key in profiles()}, 'executables': bins,
            'proof': 'local-discovery-only',
            'not_verified': ['plugin connection', 'authentication', 'credits', 'media-model readiness', 'actual output', 'creative acceptance']}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    p = sub.add_parser('plan'); p.add_argument('--domain', choices=list(profiles()), required=True); p.add_argument('--lead')
    sub.add_parser('inventory')
    args = parser.parse_args()
    try:
        if args.command == 'list':
            result = {k: v['label'] for k, v in profiles().items()}
        elif args.command == 'plan':
            result = plan(args.domain, args.lead)
        else:
            result = inventory()
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
