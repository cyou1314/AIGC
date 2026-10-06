#!/usr/bin/env python3
"""Cross-platform AIGC install/upgrade/rollback with local-change protection."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'__pycache__', '.DS_Store', '.venv', 'node_modules'}

def digest(path):
    if not path.exists():
        return None
    if path.is_symlink():
        raise ValueError(f'Symlink destination is not managed: {path}')
    h = hashlib.sha256()
    files = [path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file() and not any(part in SKIP for part in p.relative_to(path).parts))
    for file in files:
        if file.is_symlink():
            raise ValueError(f'Symlink in managed content: {file}')
        name = 'file-content' if path.is_file() else file.relative_to(path).as_posix()
        h.update(name.encode('utf-8')); h.update(b'\0'); h.update(file.read_bytes())
    return h.hexdigest()

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        temp = Path(f.name)
    os.replace(temp, path)

def load(path, default=None):
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else (default if default is not None else {})

def skills_default():
    return Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills'

def config_for(skills):
    return skills.parent / 'aigc-workflow.json'

def registry_for(skills):
    return skills.parent / 'aigc-installed.json'

def revision():
    result = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--verify', 'HEAD'], capture_output=True, text=True) if shutil.which('git') else None
    return result.stdout.strip() if result and result.returncode == 0 else 'working-tree'

def rendered_copy(source, destination, mapping):
    if source.is_dir():
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(*SKIP, '*.pyc', '.git'))
        files = destination.rglob('*')
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        files = [destination]
    for path in files:
        if not path.is_file() or path.suffix not in {'.md', '.yaml', '.yml'}:
            continue
        text = path.read_text(encoding='utf-8-sig')
        for key, value in mapping.items():
            text = text.replace('{{' + key + '}}', value)
        path.write_text(text, encoding='utf-8')

def preserve_and_restore(journal, backup, force=False):
    # Restore in reverse operation order. Current files are moved to recovery,
    # never recursively deleted. A completed rollback refuses subsequent reuse.
    if journal.get('status') == 'rolled-back':
        raise ValueError('This transaction has already been rolled back')
    for op in journal['operations']:
        if not op.get('started'):
            continue
        target = Path(op['target'])
        if not force and op.get('after') is not None and digest(target) != op['after']:
            raise ValueError(f'Local changes after installation: {target}; use --replace-local after review')
    for i in reversed(range(len(journal['operations']))):
        op = journal['operations'][i]
        if not op.get('started'):
            continue
        target = Path(op['target']); previous = backup / 'previous' / str(i)
        if op['existed'] and not previous.exists():
            continue  # operation had not yet displaced the original
        if target.exists():
            recovery = backup / 'rollback-current' / str(i)
            recovery.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(recovery))
        if previous.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            if previous.is_dir():
                shutil.copytree(previous, target)
            else:
                shutil.copy2(previous, target)
    journal['status'] = 'rolled-back'
    write_json(backup / 'journal.json', journal)

def install(args):
    skills = Path(args.skills_dir).expanduser().resolve()
    old_config = load(config_for(skills))
    workspace = Path(args.workspace or old_config.get('workspace', str(Path.home() / 'AIGC-workspace'))).expanduser().resolve()
    vault = Path(args.vault or old_config.get('vault', str(workspace / 'Codex'))).expanduser().resolve()
    outputs = Path(args.outputs or old_config.get('outputs', str(workspace / 'outputs'))).expanduser().resolve()
    registry = load(registry_for(skills), {'owner': 'AIGC', 'managed': {}})
    if registry.get('owner') != 'AIGC':
        raise ValueError('The existing installation registry belongs to another manager')
    version = (ROOT / 'VERSION').read_text().strip()
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = workspace / '.aigc-backups' / stamp
    mapping = {'AIGC_WORKSPACE': str(workspace), 'AIGC_VAULT': str(vault), 'AIGC_OUTPUT_ROOT': str(outputs),
               'SKILL_ROOT': str(skills), 'REPO_ROOT': str(ROOT), 'PYTHON': sys.executable,
               'PLATFORM': 'Windows' if os.name == 'nt' else 'macOS' if sys.platform == 'darwin' else sys.platform}
    operations = []; conflicts = []; incoming = []
    with tempfile.TemporaryDirectory(prefix='aigc-install-') as staging_name:
        staging = Path(staging_name)
        prepared_count = 0
        def prepare(source, target, kind):
            nonlocal prepared_count
            target = target.absolute()
            key = str(target)
            staged = staging / ('candidate-' + str(prepared_count))
            prepared_count += 1
            rendered_copy(source, staged, mapping)
            before = digest(target)
            after = digest(staged)
            if before == after:
                return
            tracked = registry.get('managed', {}).get(key)
            if before is not None:
                if kind == 'skill' and tracked is None and not args.adopt_existing:
                    conflicts.append(key + ' (unmanaged existing Skill)'); return
                if kind == 'skill' and tracked is not None and before != tracked and not args.replace_local:
                    conflicts.append(key + ' (locally modified Skill)'); return
                if kind == 'knowledge' and (tracked is None or before != tracked):
                    target = vault / '.incoming' / target.relative_to(vault)
                    key = str(target); incoming.append(key)
                    if target.exists() and digest(target) == after:
                        return
            operations.append({'target': key, 'staged': str(staged), 'kind': kind, 'existed': target.exists(), 'after': after})
        names = []
        for source in sorted((ROOT / 'skills').iterdir()):
            if not (source / 'SKILL.md').is_file():
                continue
            if not re.fullmatch(r'[a-z0-9-]+', source.name):
                raise ValueError('Invalid Skill directory name')
            names.append(source.name)
            prepare(source, skills / source.name, 'skill')
        for source in sorted((ROOT / 'knowledge').rglob('*')):
            if source.is_file():
                prepare(source, vault / source.relative_to(ROOT / 'knowledge'), 'knowledge')
        for name, target_name in [('project-quick.md', '_项目快速模板.md'), ('project-full.md', '_项目模板.md')]:
            prepare(ROOT / 'templates' / name, vault / 'projects' / target_name, 'knowledge')
        if conflicts:
            raise ValueError('Installation stopped before any target changed:\n' + '\n'.join(conflicts))
        new_config = dict(old_config, workspace=str(workspace), vault=str(vault), outputs=str(outputs),
                          skills_dir=str(skills), repo=str(ROOT), version=version)
        config_source = staging / 'config.json'; write_json(config_source, new_config)
        prepare(config_source, config_for(skills), 'config')
        managed = dict(registry.get('managed', {}))
        for op in operations:
            if op['kind'] in {'skill', 'knowledge'}:
                managed[op['target']] = op['after']
        # Identical files are also registered on the first adoption.
        for name in names:
            path = skills / name
            if path.exists() and str(path) not in managed:
                managed[str(path)] = digest(path)
        new_registry = {'owner': 'AIGC', 'version': version, 'revision': revision(), 'managed': managed,
                        'latest_transaction': stamp, 'backup_root': str(workspace / '.aigc-backups')}
        registry_source = staging / 'registry.json'; write_json(registry_source, new_registry)
        prepare(registry_source, registry_for(skills), 'registry')
        journal = {'id': stamp, 'status': 'prepared', 'version': version, 'operations': operations}
        backup.mkdir(parents=True, exist_ok=False)
        write_json(backup / 'journal.json', journal)
        try:
            for i, op in enumerate(operations):
                target = Path(op['target']); target.parent.mkdir(parents=True, exist_ok=True)
                op['started'] = True; write_json(backup / 'journal.json', journal)
                if target.exists():
                    previous = backup / 'previous' / str(i); previous.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(target), str(previous))
                shutil.move(op['staged'], str(target))
                # Hashes must use final target basename for single-file targets.
                op['after'] = digest(target)
                if op['kind'] in {'skill', 'knowledge'}:
                    managed[op['target']] = op['after']
                write_json(backup / 'journal.json', journal)
            # Registry tracks final file names, and includes its own verified revision.
            new_registry['managed'] = managed
            write_json(registry_for(skills), new_registry)
            operations[-1]['after'] = digest(registry_for(skills))
            journal['status'] = 'complete'; write_json(backup / 'journal.json', journal)
        except Exception:
            preserve_and_restore(journal, backup, force=True)
            raise
    print(json.dumps({'version': version, 'skills': len(names), 'changed_targets': len(operations),
                      'workspace': str(workspace), 'vault': str(vault), 'config': str(config_for(skills)),
                      'transaction': stamp, 'backup': str(backup), 'incoming': incoming}, ensure_ascii=False, indent=2))

def rollback(args):
    skills = Path(args.skills_dir).expanduser().resolve()
    registry = load(registry_for(skills))
    transaction = args.transaction or registry.get('latest_transaction')
    if not transaction or not re.fullmatch(r'[0-9TZ]+', transaction):
        raise ValueError('No valid transaction ID; use the ID returned by install')
    root = Path(args.backup_root or registry.get('backup_root', ''))
    if not root.is_absolute():
        raise ValueError('Provide an absolute --backup-root if the registry is unavailable')
    backup = root / transaction
    journal = load(backup / 'journal.json')
    if not journal:
        raise ValueError('Backup journal not found')
    preserve_and_restore(journal, backup, args.replace_local)
    print(f'Rolled back {transaction}; displaced current files preserved in {backup / "rollback-current"}')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ['install', 'upgrade']:
        p = sub.add_parser(command)
        p.add_argument('--workspace'); p.add_argument('--vault'); p.add_argument('--outputs')
        p.add_argument('--skills-dir', default=str(skills_default()))
        p.add_argument('--adopt-existing', action='store_true'); p.add_argument('--replace-local', action='store_true')
        p.set_defaults(func=install)
    p = sub.add_parser('rollback'); p.add_argument('--skills-dir', default=str(skills_default()))
    p.add_argument('--transaction'); p.add_argument('--backup-root'); p.add_argument('--replace-local', action='store_true')
    p.set_defaults(func=rollback)
    args = parser.parse_args()
    try:
        args.func(args)
        if args.command in {'install', 'upgrade'}:
            sync_after_install(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr); raise SystemExit(2)

def sync_after_install(args):
    """An installation can succeed while publication is blocked; report separately."""
    profile = ROOT / '.local/github-sync.json'
    if not profile.is_file():
        return
    settings = load(profile)
    if Path(settings['skills_dir']).resolve() != Path(args.skills_dir).expanduser().resolve():
        return  # isolated/test installation must not publish production changes
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/sync_github.py'), 'run'],
                            cwd=ROOT, timeout=180)
    if result.returncode:
        print('Installation completed, but GitHub synchronization is blocked; local installation retained.', file=sys.stderr)
        raise SystemExit(3)

if __name__ == '__main__':
    main()
