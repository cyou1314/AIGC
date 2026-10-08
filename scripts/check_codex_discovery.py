#!/usr/bin/env python3
"""Query the installed Codex app-server Skills API without starting a model turn."""
import argparse
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def discover(cwds, executable='codex', timeout=30):
    if not shutil.which(executable):
        raise ValueError('Codex CLI is missing; automatic discovery cannot be verified')
    process = subprocess.Popen([executable, 'app-server', '--stdio'], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    selector = selectors.DefaultSelector(); selector.register(process.stdout, selectors.EVENT_READ)
    buffer = b''

    def send(message):
        process.stdin.write((json.dumps(message) + '\n').encode()); process.stdin.flush()

    def request(number, method, params):
        nonlocal buffer
        send({'id': number, 'method': method, 'params': params})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                if not line.strip():
                    continue
                message = json.loads(line)
                if message.get('id') == number:
                    if 'error' in message:
                        raise ValueError(f'{method} failed: {message["error"]}')
                    return message['result']
            if selector.select(min(1, max(0, deadline - time.monotonic()))):
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    raise ValueError('Codex app-server exited before returning Skills')
                buffer += chunk
        raise ValueError(f'Codex app-server timed out: {method}')

    try:
        request(1, 'initialize', {'clientInfo': {'name': 'aigc_discovery_check', 'version': '1.0'}})
        send({'method': 'initialized'})
        return request(2, 'skills/list', {'cwds': cwds, 'forceReload': True})
    finally:
        selector.close(); process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=5)
        process.stdin.close(); process.stdout.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', action='append')
    parser.add_argument('--output')
    args = parser.parse_args()
    expected = {p.name for p in (ROOT / 'skills').iterdir() if (p / 'SKILL.md').is_file()}
    try:
        result = discover(args.cwd or [str(ROOT), str(ROOT.parent)])
        checks = []
        for entry in result['data']:
            enabled = {s['name'] for s in entry['skills'] if s['enabled']}
            checks.append({'cwd': entry['cwd'], 'expected': len(expected),
                           'found': sorted(expected & enabled), 'missing': sorted(expected - enabled),
                           'errors': entry['errors']})
        report = {'proof': 'Codex app-server skills/list; no thread or model turn started',
                  'cross_task_web_restore': 'not-tested', 'checks': checks, 'response': result}
        if args.output:
            Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'proof': report['proof'], 'checks': checks}, ensure_ascii=False, indent=2))
        if not checks or any(c['missing'] or c['errors'] for c in checks):
            raise SystemExit(1)
    except (ValueError, OSError) as exc:
        parser.exit(2, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
