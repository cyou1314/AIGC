#!/usr/bin/env python3
"""Print a portable Skill snapshot manifest for review; never copies private data."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'__pycache__', '.DS_Store', '.venv', 'node_modules', '.git'}

def snapshot(directory):
    digest = hashlib.sha256()
    count = 0
    for path in sorted(directory.rglob('*')):
        relative = path.relative_to(directory)
        if not path.is_file() or any(part in SKIP for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError('Symlink not allowed in source snapshots')
        data = path.read_bytes()
        # Normalize text checkout EOL differences; preserve binary bytes.
        try:
            data = data.decode('utf-8').replace('\r\n', '\n').encode('utf-8')
        except UnicodeDecodeError:
            pass
        digest.update(relative.as_posix().encode('utf-8'))
        digest.update(b'\0'); digest.update(data)
        count += 1
    return count, digest.hexdigest()

def main():
    entries = []
    for directory in sorted((ROOT / 'skills').iterdir()):
        if not (directory / 'SKILL.md').is_file():
            continue
        count, sha = snapshot(directory)
        source = directory / 'SOURCE.json'
        provenance = json.loads(source.read_text(encoding='utf-8')) if source.is_file() else {}
        entry = {'name': directory.name, 'path': 'skills/' + directory.name,
                 'origin': 'adapted-upstream' if provenance else 'user-installed-workflow-snapshot',
                 'files': count, 'sha256_normalized_text': sha}
        if provenance:
            entry['upstream'] = {k: provenance[k] for k in ['repository', 'path', 'revision', 'license']}
        entries.append(entry)
    print(json.dumps({'schema_version': 1, 'version': (ROOT / 'VERSION').read_text().strip(),
                      'provenance': 'THIRD_PARTY_NOTICES.md',
                      'note': 'Packaged snapshot, not upstream release verification. Private fixtures excluded.',
                      'skills': entries}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
