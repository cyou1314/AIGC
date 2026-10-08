"""Portable runtime paths shared by installed skills; no external dependencies."""
import datetime as dt
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

def runtime_config():
    """One resolver for repository commands and installed/legacy Skill scripts."""
    explicit = os.environ.get('AIGC_CONFIG')
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f'AIGC_CONFIG does not exist: {path}')
        return path, json.loads(path.read_text(encoding='utf-8'))
    home = Path.home()
    codex = Path(os.environ.get('CODEX_HOME', str(home / '.codex')))
    for path in [home / '.agents/aigc-workflow.json',
                 Path(__file__).resolve().parents[3] / 'aigc-workflow.json',
                 codex / 'aigc-workflow.json', home / '.codex/aigc-workflow.json']:
        if path.is_file():
            return path, json.loads(path.read_text(encoding='utf-8'))
    return None, {}

def runtime_paths():
    _, config = runtime_config()
    workspace = Path(os.environ.get('AIGC_WORKSPACE', config.get('workspace', str(Path.home() / 'AIGC-workspace')))).expanduser().resolve()
    vault = Path(os.environ.get('AIGC_VAULT', config.get('vault', str(workspace / 'Codex')))).expanduser().resolve()
    outputs = Path(os.environ.get('AIGC_OUTPUT_ROOT', config.get('outputs', str(workspace / 'outputs')))).expanduser().resolve()
    return workspace, vault, outputs

def shanghai_timezone():
    try:
        return ZoneInfo('Asia/Shanghai')
    except ZoneInfoNotFoundError:
        return dt.timezone(dt.timedelta(hours=8), name='Asia/Shanghai')
