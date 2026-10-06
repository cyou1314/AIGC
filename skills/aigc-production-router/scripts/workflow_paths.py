"""Portable runtime paths shared by installed skills; no external dependencies."""
import datetime as dt
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

def runtime_paths():
    # Both repository and installed layouts place this beside the skills directory.
    config_path = Path(__file__).resolve().parents[3] / 'aigc-workflow.json'
    if not config_path.is_file():
        codex = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
        config_path = codex / 'aigc-workflow.json'
    config = json.loads(config_path.read_text(encoding='utf-8')) if config_path.is_file() else {}
    workspace = Path(os.environ.get('AIGC_WORKSPACE', config.get('workspace', str(Path.home() / 'AIGC-workspace')))).expanduser().resolve()
    vault = Path(os.environ.get('AIGC_VAULT', config.get('vault', str(workspace / 'Codex')))).expanduser().resolve()
    outputs = Path(os.environ.get('AIGC_OUTPUT_ROOT', config.get('outputs', str(workspace / 'outputs')))).expanduser().resolve()
    return workspace, vault, outputs

def shanghai_timezone():
    try:
        return ZoneInfo('Asia/Shanghai')
    except ZoneInfoNotFoundError:
        return dt.timezone(dt.timedelta(hours=8), name='Asia/Shanghai')
