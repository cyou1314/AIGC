#!/usr/bin/env python3
"""Publish scoped workflow changes, preserving portable adaptations and local edits."""
import argparse
import datetime as dt
import difflib
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
SKIP = {'.git', '__pycache__', '.venv', 'node_modules', '.DS_Store',
        'nat_studio_project', 'collapsed_asr'}
PRIVATE = {'.env', 'auth.json', 'credentials.json', 'token.json', 'aigc-workflow.json', 'aigc-installed.json'}
MEDIA = {'.mp4', '.mov', '.wav', '.mp3', '.blend', '.pem', '.key', '.pyc'}
SCOPES = {'skills', 'docs', 'scripts', 'tests', 'knowledge', 'templates', 'ci'}
ROOT_FILES = {'README.md', 'VERSION', 'CHANGELOG.md', 'AGENTS.md', 'THIRD_PARTY_NOTICES.md',
              '.gitignore', '.gitattributes', 'requirements.txt', 'sources.json'}

class SyncError(ValueError):
    pass

def command(args, cwd, timeout=120):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=timeout)
    if result.returncode:
        raise SyncError(f'{args[0]} operation failed: {result.stderr[-2500:]}')
    return result.stdout.strip()

def digest(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None

def read(path):
    if path.is_symlink():
        raise SyncError(f'Symlink is not automatically synchronized: {path}')
    return path.read_bytes() if path.is_file() else None

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n'); temp = Path(handle.name)
    os.replace(temp, path)

def guarded(data, label):
    if data is None:
        return
    if len(data) > 2_000_000:
        raise SyncError(f'Large file needs review: {label}')
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError:
        if len(data) > 256_000:
            raise SyncError(f'Binary asset needs review: {label}')
        return
    if '/tests/' in '/' + label or label.startswith('tests/'):
        # Public reserved-domain negative-test inputs are not working credentials.
        # This exemption is deliberately limited to tests and reserved hostnames.
        text = re.sub(r'https?://[^\s/@]+:[^\s/@]+@(?:example\.(?:com|org|net)|[A-Za-z0-9.-]+\.(?:invalid|test))(?=[/\s\"\x27]|$)',
                      'https://reserved-test-input/', text)
    for pattern in [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                    r'gh[pousr]_[A-Za-z0-9]{30,}', r'sk-(?:proj-)?[A-Za-z0-9_-]{35,}',
                    r'https?://[^\s/@]+:[^\s/@]+@']:
        if re.search(pattern, text):
            raise SyncError(f'Potential credential; content not displayed: {label}')

def allowed(relative):
    parts = Path(relative).parts
    if not parts or Path(relative).is_absolute() or '..' in parts:
        return False
    if any(part in SKIP or part in PRIVATE or part.startswith('.env.') for part in parts):
        return False
    if Path(relative).suffix.lower() in MEDIA:
        return False
    return parts[0] in SCOPES or (len(parts) == 1 and parts[0] in ROOT_FILES)

def changes(base, current):
    return [(i, j, current[a:b]) for tag, i, j, a, b in
            difflib.SequenceMatcher(None, base, current, autojunk=False).get_opcodes() if tag != 'equal']

def overlap(a, b):
    i, j, _ = a; k, l, _ = b
    if i == j or k == l:
        return (k <= i <= l) if i == j else (i <= k <= j)
    return max(i, k) < min(j, l)

def merge_text(base, local, portable):
    """Three-way text merge. Conflicting adaptations stop instead of being overwritten."""
    if local == base or local == portable:
        return portable
    if portable == base:
        return local
    if base is None or local is None or portable is None:
        raise SyncError('Deletion/addition conflicts with repository changes')
    original = base.splitlines(keepends=True)
    left = changes(original, local.splitlines(keepends=True))
    right = changes(original, portable.splitlines(keepends=True))
    combined = list(right)
    for edit in left:
        if edit in right:
            continue
        if any(overlap(edit, other) for other in right):
            raise SyncError('Local change overlaps a portable/repository adaptation; review required')
        combined.append(edit)
    result = list(original)
    for start, end, replacement in sorted(combined, key=lambda edit: (edit[0], edit[1]), reverse=True):
        result[start:end] = replacement
    return ''.join(result)

class Sync:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        self.state = self.root / '.local/github-sync.json'

    def git(self, *args):
        return command(['git', *args], self.root)

    def load(self):
        if not self.state.is_file():
            raise SyncError('Run setup on this computer before enabling synchronization')
        return json.loads(self.state.read_text(encoding='utf-8'))

    def normalize(self, data, relative, config):
        if data is None:
            return None
        try:
            text = data.decode('utf-8-sig').replace('\r\n', '\n')
        except UnicodeDecodeError:
            return None
        if Path(relative).suffix in {'.md', '.yaml', '.yml'}:
            replacements = {config['vault']: '{{AIGC_VAULT}}',
                            config['skills_dir']: '{{SKILL_ROOT}}',
                            config['outputs']: '{{AIGC_OUTPUT_ROOT}}',
                            config['workspace']: '{{AIGC_WORKSPACE}}'}
            for value, placeholder in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
                text = text.replace(value, placeholder)
                text = text.replace(value.replace('\\', '/'), placeholder)
        return text

    def inventory(self, config):
        found = {}
        for unit in config['units']:
            source = Path(unit['source']); target = unit['target']
            if unit['directory']:
                if not source.is_dir():
                    raise SyncError(f'Managed Skill directory unavailable: {source}')
                paths = sorted(source.rglob('*'))
                for path in paths:
                    relative = target + '/' + path.relative_to(source).as_posix()
                    if not allowed(relative) or not path.is_file():
                        continue
                    data = read(path); guarded(data, relative)
                    found[relative] = (path, data)
            else:
                data = read(source); guarded(data, target)
                found[target] = (source, data)
        return found

    def checkpoint(self, config, observed=None):
        records = {}
        for relative, (path, data) in (observed if observed is not None else self.inventory(config)).items():
            records[relative] = {'source': str(path), 'sha': digest(data),
                                 'text': self.normalize(data, relative, config),
                                 'repo_sha': digest(read(self.root / relative))}
        config['records'] = records
        config['version'] = (self.root / 'VERSION').read_text().strip()
        config['checkpoint'] = dt.datetime.now(dt.timezone.utc).isoformat()
        write_json(self.state, config)

    def setup(self, args):
        if self.state.exists():
            raise SyncError('Baseline already exists; do not reset pending local changes')
        skills = Path(args.skills_dir).expanduser().resolve()
        vault = Path(args.vault).expanduser().resolve()
        names = [item['name'] for item in json.loads((self.root / 'sources.json').read_text())['skills']]
        visibility = getattr(args, 'visibility', 'private')
        excluded = sorted(set(getattr(args, 'exclude_skill', None) or []))
        if any(name not in names for name in excluded):
            raise SyncError('Excluded skill must be in the repository source inventory')
        units = [{'source': str(skills / name), 'target': 'skills/' + name, 'directory': True}
                 for name in names if name not in excluded]
        # Personal vault material is not imported to a public repository automatically.
        if visibility == 'private':
            for group in ['agent', 'learning']:
                for page in sorted((self.root / 'knowledge' / group).glob('*.md')):
                    units.append({'source': str(vault / group / page.name),
                                  'target': 'knowledge/' + group + '/' + page.name, 'directory': False})
            for filename, local_name in [('project-quick.md', '_项目快速模板.md'), ('project-full.md', '_项目模板.md')]:
                units.append({'source': str(vault / 'projects' / local_name),
                              'target': 'templates/' + filename, 'directory': False})
        config = {'schema_version': 1, 'repository': args.repository, 'visibility': visibility,
                  'excluded_skills': excluded,
                  'skills_dir': str(skills), 'vault': str(vault),
                  'workspace': str(Path(args.workspace).expanduser().resolve()),
                  'outputs': str(Path(args.outputs).expanduser().resolve()), 'units': units}
        self.checkpoint(config)
        return {'status': 'configured', 'tracked_sources': len(config['records']),
                'visibility': visibility, 'excluded_skills': excluded,
                'note': 'Historical platform differences recorded, not overwritten'}

    def register(self, args):
        config = self.load()
        if args.skill:
            name = args.skill
            if not re.fullmatch(r'[a-z0-9-]+', name):
                raise SyncError('Invalid Skill name')
            target = 'skills/' + name
            source = Path(config['skills_dir']) / name
            if not (source / 'SKILL.md').is_file() or not (self.root / target / 'SKILL.md').is_file():
                raise SyncError('Add and review the Skill in both source and repository before registration')
            unit = {'source': str(source), 'target': target, 'directory': True}
        else:
            if config.get('visibility', 'private') == 'public':
                raise SyncError('Personal vault pages are not registered for public synchronization')
            relative = Path(args.knowledge)
            if len(relative.parts) != 2 or relative.parts[0] not in {'agent', 'learning'} or relative.suffix != '.md':
                raise SyncError('Knowledge registration uses agent/name.md or learning/name.md')
            target = 'knowledge/' + relative.as_posix()
            source = Path(config['vault']) / relative
            if not source.is_file() or not (self.root / target).is_file():
                raise SyncError('Add and review both knowledge files before registration')
            unit = {'source': str(source), 'target': target, 'directory': False}
        if any(existing['target'] == target for existing in config['units']):
            raise SyncError('Already registered; existing baseline is not reset')
        config['units'].append(unit)
        for relative, (path, data) in self.inventory(config).items():
            if relative == target or relative.startswith(target + '/'):
                config['records'][relative] = {'source': str(path), 'sha': digest(data),
                    'text': self.normalize(data, relative, config), 'repo_sha': digest(read(self.root / relative))}
        if args.skill and args.skill in config.get('excluded_skills', []):
            config['excluded_skills'].remove(args.skill)
        write_json(self.state, config)
        return {'status': 'registered', 'target': target, 'existing_baselines': 'preserved'}

    def plan(self, config):
        roster = {item['name'] for item in json.loads((self.root / 'sources.json').read_text())['skills']}
        registered = {unit['target'].split('/')[1] for unit in config['units'] if unit['directory']}
        excluded = set(config.get('excluded_skills', []))
        if roster != registered | excluded or registered & excluded:
            raise SyncError('Skill roster changed; register new sources or review removed sources before publishing')
        current = self.inventory(config); updates = {}; changed_sources = {}
        for relative in sorted(set(current) | set(config['records'])):
            record = config['records'].get(relative)
            path, data = current.get(relative, (Path(record['source']), None)) if record else current[relative]
            if record and digest(data) == record['sha']:
                continue
            # A previously absent optional page is an addition; missing old pages are deletion.
            changed_sources[str(path)] = digest(data)
            repo = read(self.root / relative)
            local_text = self.normalize(data, relative, config)
            remote_text = self.normalize(repo, relative, config)
            base_text = record['text'] if record else None
            try:
                if (data is None or local_text is not None) and (repo is None or remote_text is not None):
                    merged = merge_text(base_text, local_text, remote_text)
                    result = merged.encode('utf-8') if merged is not None else None
                elif record and digest(repo) == record['repo_sha']:
                    result = data
                else:
                    raise SyncError('Binary asset conflicts with repository version')
            except SyncError as exc:
                raise SyncError(f'{relative}: {exc}') from exc
            guarded(result, relative)
            if result != repo:
                updates[relative] = result
        return updates, changed_sources, current

    def verify_remote(self, config):
        slug = config['repository']
        if not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', slug):
            raise SyncError('Invalid repository identity')
        expected = {f'https://github.com/{slug}.git', f'https://github.com/{slug}', f'git@github.com:{slug}.git'}
        origins = self.git('remote', 'get-url', '--all', 'origin').splitlines()
        pushes = self.git('remote', 'get-url', '--push', '--all', 'origin').splitlines()
        if len(origins) != 1 or len(pushes) != 1 or origins[0] not in expected or pushes[0] not in expected:
            raise SyncError('Remote URL does not match the configured repository')
        private = command(['gh', 'repo', 'view', slug, '--json', 'isPrivate', '--jq', '.isPrivate'], self.root)
        expected_visibility = config.get('visibility', 'private')
        if expected_visibility not in {'private', 'public'}:
            raise SyncError('Invalid expected repository visibility')
        expected_value = 'true' if expected_visibility == 'private' else 'false'
        if private != expected_value:
            raise SyncError('Repository visibility differs from configured expectation')

    def dirty(self):
        names = set(self.git('diff', '--name-only', '-z').split('\0'))
        names.update(self.git('ls-files', '--others', '--exclude-standard', '-z').split('\0'))
        names.discard('')
        for name in names:
            if not allowed(name):
                raise SyncError(f'Out-of-scope file; do not publish automatically: {name}')
            guarded(read(self.root / name), name)
        return sorted(names)

    def verify_outgoing(self):
        for commit in self.git('rev-list', 'refs/remotes/origin/main..HEAD').splitlines():
            for relative in filter(None, self.git('diff-tree', '--no-commit-id', '--name-only', '-z', '-r', commit).split('\0')):
                if not allowed(relative):
                    raise SyncError(f'Out-of-scope outgoing commit: {relative}')
            for relative in filter(None, self.git('diff-tree', '--no-commit-id', '--name-only', '-z', '--diff-filter=ACMRT', '-r', commit).split('\0')):
                payload = subprocess.run(['git', 'show', f'{commit}:{relative}'], cwd=self.root, capture_output=True, timeout=120)
                if payload.returncode:
                    raise SyncError('Cannot verify outgoing file')
                guarded(payload.stdout, relative)

    def run(self):
        config = self.load()
        self.verify_remote(config)
        if self.git('branch', '--show-current') != 'main':
            raise SyncError('Only the configured main branch is automatically published')
        if self.git('diff', '--cached', '--name-only'):
            raise SyncError('Existing staged changes require review; index left untouched')
        self.git('fetch', '--quiet', 'origin', 'main')
        head = self.git('rev-parse', 'HEAD'); remote = self.git('rev-parse', 'refs/remotes/origin/main')
        dirty = self.dirty()
        if head != remote:
            ancestors = self.git('rev-list', '--left-right', '--count', 'HEAD...refs/remotes/origin/main').split()
            behind = int(ancestors[1])
            if behind:
                if int(ancestors[0]) or dirty:
                    raise SyncError('Remote divergence or dirty checkout behind remote; no force push/merge')
                self.git('merge', '--ff-only', 'refs/remotes/origin/main')
        self.verify_outgoing()
        updates, source_hashes, observed = self.plan(config)
        if updates:
            stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = self.root / '.local/sync-backups' / stamp
            # All merge/credential conflicts have been checked before the first write.
            for relative, data in updates.items():
                path = self.root / relative
                if path.exists():
                    saved = backup / relative; saved.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, saved)
                if data is None:
                    if path.exists():
                        path.unlink()
                else:
                    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        dirty = self.dirty()
        if dirty:
            version = (self.root / 'VERSION').read_text().strip()
            if version == config['version'] and 'VERSION' not in dirty:
                parts = version.split('.')
                if len(parts) != 3 or not all(part.isdigit() for part in parts):
                    raise SyncError('Version needs a reviewed semantic version')
                version = '.'.join(parts[:2] + [str(int(parts[2]) + 1)])
                (self.root / 'VERSION').write_text(version + '\n', encoding='utf-8')
                mapping = self.root / 'docs/workbench/module-map.json'
                if mapping.is_file():
                    data = json.loads(mapping.read_text(encoding='utf-8'))
                    data['version'] = version
                    write_json(mapping, data)
                date = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
                changelog = self.root / 'CHANGELOG.md'
                old = changelog.read_text(encoding='utf-8')
                note = f'## {version} — {date}\n\n- 自动同步本机工作流；路径/版本和验证结果记录在Git提交中。\n\n'
                changelog.write_text(old.replace('# Changelog\n\n', '# Changelog\n\n' + note, 1), encoding='utf-8')
            manifest = command([sys.executable, 'scripts/source_manifest.py'], self.root)
            write_json(self.root / 'sources.json', json.loads(manifest))
        if dirty or head != remote:
            command([sys.executable, 'scripts/validate.py'], self.root)
        for path, sha in source_hashes.items():
            if digest(read(Path(path))) != sha:
                raise SyncError('Source changed during validation; retry after editing completes')
        dirty = self.dirty()
        if dirty:
            self.git('add', '--', *dirty)
            self.git('diff', '--cached', '--check')
            self.git('commit', '-m', 'sync: publish AIGC workflow ' + (self.root / 'VERSION').read_text().strip())
        self.verify_outgoing()
        local = self.git('rev-parse', 'HEAD')
        remote_sha = self.git('ls-remote', 'origin', 'refs/heads/main').split()[0]
        published = local != remote_sha
        if published:
            self.git('push', 'origin', 'HEAD:main')
        remote_sha = self.git('ls-remote', 'origin', 'refs/heads/main').split()[0]
        if remote_sha != local:
            raise SyncError('Remote SHA does not match local HEAD; synchronization not confirmed')
        if self.dirty():
            raise SyncError('Repository changed while publishing; next run must finish new changes')
        # Keep the observed source snapshot, not a fresh read that could acknowledge
        # edits made after this run without ever importing them.
        for relative, record in config['records'].items():
            if relative not in observed:
                observed[relative] = (Path(record['source']), None)
        self.checkpoint(config, observed)
        return {'status': 'synced' if published else 'unchanged', 'sha': local,
                'imported_files': len(updates), 'repository': config['repository'],
                'proof': 'remote-main-sha-equals-local-head'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    setup = sub.add_parser('setup')
    setup.add_argument('--skills-dir', default=str(Path.home() / '.agents/skills'))
    setup.add_argument('--vault', required=True); setup.add_argument('--workspace', required=True)
    setup.add_argument('--outputs', required=True); setup.add_argument('--repository', default='cyou1314/AIGC')
    setup.add_argument('--visibility', choices=('private', 'public'), default='private')
    setup.add_argument('--exclude-skill', action='append', default=[], help='leave an unreviewed local skill outside the sync baseline')
    sub.add_parser('run'); sub.add_parser('status')
    register = sub.add_parser('register'); group = register.add_mutually_exclusive_group(required=True)
    group.add_argument('--skill'); group.add_argument('--knowledge')
    args = parser.parse_args(); sync = Sync()
    lock = ROOT / '.local/github-sync.lock'
    acquired = False
    try:
        if args.action != 'status':
            lock.parent.mkdir(parents=True, exist_ok=True)
            try:
                lock.mkdir(); acquired = True
            except FileExistsError as exc:
                raise SyncError('Another synchronization is running, or a stale lock needs review') from exc
        if args.action == 'setup':
            result = sync.setup(args)
        elif args.action == 'run':
            result = sync.run()
        elif args.action == 'register':
            result = sync.register(args)
        else:
            config = sync.load(); updates, changed, _ = sync.plan(config)
            dirty = sync.dirty()
            ahead = int(sync.git('rev-list', '--count', 'refs/remotes/origin/main..HEAD'))
            result = {'status': 'pending' if updates or dirty or ahead else 'clean',
                      'source_changes': len(changed), 'pending_imports': sorted(updates),
                      'repository_changes': dirty, 'outgoing_commits': ahead,
                      'visibility': config.get('visibility', 'private'),
                      'excluded_skills': config.get('excluded_skills', []), 'proof': 'local-check-only'}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status': 'blocked', 'reason': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
    finally:
        if acquired:
            lock.rmdir()

if __name__ == '__main__':
    main()
