#!/usr/bin/env python3
"""Idempotent offline Codex Cloud setup/maintenance; never publishes or generates."""
import argparse
import contextlib
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile

import manage

ROOT = Path(__file__).resolve().parents[1]
BEGIN = '<!-- AIGC cloud entry: begin -->'
END = '<!-- AIGC cloud entry: end -->'
TOKENS = re.compile(r'\{\{(AIGC_VAULT|AIGC_WORKSPACE|AIGC_OUTPUT_ROOT|SKILL_ROOT|PLATFORM|REPO_ROOT|PYTHON)\}\}')


def instruction_block(repo, config):
    return f'''{BEGIN}
## AIGC workflow (conditional)
Apply these rules only to AIGC production or maintenance requests. Other tasks keep their own workflows.
Source repository: `{repo}`. Discovered user Skills: `$HOME/.agents/skills`.
Runtime configuration: `{config}`. Read its vault AGENTS.md only when AIGC project memory is needed.
New or mixed AIGC deliverable: `aigc-production-router`; explicit specialists and existing projects take priority.
Seedance shot/video direction: `aigc-manga-video-director`; image design/editing: `aigc-image-director`;
existing Jianying/剪映 projects: `jianying-editing`. Preserve source media and user edits.
Do not invoke paid generation, publish, upload private assets or sync repositories during initialization.
Do not modify platform-managed CODEX_HOME. Source templates remain portable.
{END}
'''


def safe_file(path):
    """Reject symlinked runtime files/parents rather than writing through them."""
    for parent in [path, *path.parents]:
        if parent.is_symlink():
            raise ValueError(f'Symlink runtime destination requires review: {parent}')


def replace_file(path, content, backup):
    safe_file(path)
    data = content.encode('utf-8')
    if path.is_file() and path.read_bytes() == data:
        return False
    if path.exists():
        target = backup / hashlib.sha256(str(path).encode()).hexdigest()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        manage.write_json(target.with_suffix('.json'), {'original_path': str(path)})
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('wb', dir=path.parent, delete=False) as f:
        f.write(data); staged = Path(f.name)
    try:
        os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)
    return True


def bootstrap(args):
    skills = Path(args.skills_dir).expanduser().absolute()
    workspace = Path(args.workspace).expanduser().absolute()
    vault = Path(args.vault).expanduser().absolute() if args.vault else workspace / 'Codex'
    outputs = Path(args.outputs).expanduser().absolute() if args.outputs else workspace / 'outputs'
    instructions = Path(args.instructions_file).expanduser().absolute()
    config_path = manage.config_for(skills)
    explicit = os.environ.get('AIGC_CONFIG')
    if explicit and Path(explicit).expanduser().resolve() != config_path.resolve():
        raise ValueError('AIGC_CONFIG selects another installation; align environment settings before initialization')
    state_path = skills.parent / 'aigc-cloud-state.json'
    for p in [skills, vault, outputs, config_path, state_path, instructions]:
        safe_file(p)
    old_state = manage.load(state_path)
    if old_state and old_state.get('repo') != str(ROOT):
        raise ValueError('Existing cloud configuration belongs to another checkout; review before migration')
    mapping = {'AIGC_WORKSPACE': str(workspace), 'AIGC_VAULT': str(vault),
               'AIGC_OUTPUT_ROOT': str(outputs), 'SKILL_ROOT': str(skills),
               'REPO_ROOT': str(ROOT), 'PYTHON': sys.executable,
               'PLATFORM': 'Windows' if os.name == 'nt' else 'macOS' if sys.platform == 'darwin' else sys.platform}
    registry = manage.load(manage.registry_for(skills))
    if registry and registry.get('owner') != 'AIGC':
        raise ValueError('Installation registry belongs to another manager')
    if config_path.exists() and not registry:
        raise ValueError('Existing unregistered AIGC configuration is protected; review before adopting it')
    if instructions.with_name('AGENTS.override.md').is_file():
        raise ValueError('AGENTS.override.md takes precedence; merge the AIGC entry there after review')
    names = sorted(p.name for p in (ROOT / 'skills').iterdir() if (p / 'SKILL.md').is_file())
    if len(names) != 17:
        raise ValueError(f'Expected 17 source Skills, got {len(names)}')
    # Report differing relative filenames, never contents; reject all conflicts before writes.
    conflicts = []
    with tempfile.TemporaryDirectory(prefix='aigc-cloud-preflight-') as folder:
        for name in names:
            target = skills / name; safe_file(target)
            staged = Path(folder) / name
            manage.rendered_copy(ROOT / 'skills' / name, staged, mapping)
            before = manage.digest(target)
            if before is not None and before != manage.digest(staged):
                if registry.get('managed', {}).get(str(target)) != before:
                    relative = {str(p.relative_to(target)) for p in target.rglob('*') if p.is_file()}
                    relative |= {str(p.relative_to(staged)) for p in staged.rglob('*') if p.is_file()}
                    changed = [r for r in sorted(relative)
                               if not (target / r).is_file() or not (staged / r).is_file()
                               or (target / r).read_bytes() != (staged / r).read_bytes()]
                    conflicts.append({'skill': name, 'different_files': changed})
    if conflicts:
        raise ValueError('Protected existing Skill differences: ' + json.dumps(conflicts, ensure_ascii=False))
    desired = instruction_block(ROOT, config_path)
    current = instructions.read_text(encoding='utf-8') if instructions.is_file() else ''
    if BEGIN in current or END in current:
        if current.count(BEGIN) != 1 or current.count(END) != 1:
            raise ValueError('Ambiguous AIGC instructions markers; original preserved')
        start = current.index(BEGIN); end = current.index(END) + len(END)
        existing = current[start:end]
        expected_hash = old_state.get('instruction_block_sha256')
        if existing != desired.rstrip() and hashlib.sha256(existing.encode()).hexdigest() != expected_hash:
            raise ValueError('AIGC instructions were edited or are unmanaged; original preserved')
        merged = current[:start] + desired.rstrip() + current[end:]
    else:
        merged = current.rstrip() + ('\n\n' if current.strip() else '') + desired
    repairs = []
    if vault.is_dir():
        for path in sorted(vault.rglob('*')):
            if '.incoming' in path.relative_to(vault).parts or path.suffix not in {'.md', '.yaml', '.yml'} or not path.is_file():
                continue
            text = path.read_text(encoding='utf-8-sig')
            if TOKENS.search(text):
                safe_file(path)
                repairs.append((path, TOKENS.sub(lambda m: mapping[m[1]], text)))
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = workspace / '.aigc-backups' / ('cloud-' + stamp)
    # Existing managed Skills retain manage.py's backup/rollback and local-change checks.
    install_args = argparse.Namespace(skills_dir=str(skills), workspace=str(workspace),
                                     vault=str(vault), outputs=str(outputs),
                                     adopt_existing=False, replace_local=False)
    with contextlib.redirect_stdout(io.StringIO()) as stream:
        manage.install(install_args)
    installation = json.loads(stream.getvalue())
    changed = []
    for path, _ in repairs:
        # manage.py may already have upgraded a managed template; use its current content.
        text = TOKENS.sub(lambda m: mapping[m[1]], path.read_text(encoding='utf-8-sig'))
        if replace_file(path, text, backup):
            changed.append(str(path))
    if replace_file(instructions, merged, backup):
        changed.append(str(instructions))
    state = {'repo': str(ROOT), 'instruction_block_sha256': hashlib.sha256(desired.rstrip().encode()).hexdigest()}
    replace_file(state_path, json.dumps(state, ensure_ascii=False, indent=2) + '\n', backup)
    outputs.mkdir(parents=True, exist_ok=True)
    # Check every managed installation against the source rendered for this runtime.
    registry = manage.load(manage.registry_for(skills))
    for name in names:
        if manage.digest(skills / name) != registry['managed'][str(skills / name)]:
            raise ValueError(f'Post-install digest mismatch: {name}')
    unresolved = []
    for path in vault.rglob('*.md'):
        if '.incoming' not in path.relative_to(vault).parts and TOKENS.search(path.read_text(encoding='utf-8-sig')):
            unresolved.append(str(path))
    if unresolved:
        raise ValueError('Unresolved runtime tokens: ' + json.dumps(unresolved))
    return {'installation': installation, 'runtime_files_changed': changed,
            'runtime_backup': str(backup) if backup.exists() else None,
            'config': str(config_path), 'skills': names, 'instructions': str(instructions),
            'global_instructions': 'platform CODEX_HOME untouched; workspace-scope entry only',
            'proof': 'installed-files-only; verify with Codex skills/list and a new web task'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', default=str(ROOT.parent / 'AIGC-workspace'))
    parser.add_argument('--vault'); parser.add_argument('--outputs')
    parser.add_argument('--skills-dir', default=str(Path.home() / '.agents/skills'))
    parser.add_argument('--instructions-file', default=str(ROOT.parent / 'AGENTS.md'))
    args = parser.parse_args()
    try:
        print(json.dumps(bootstrap(args), ensure_ascii=False, indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr); raise SystemExit(2)


if __name__ == '__main__':
    main()
