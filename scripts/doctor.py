#!/usr/bin/env python3
"""Read-only capability discovery; no login, uploads, installation or paid tasks."""
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/aigc-production-router/scripts'))
from workflow_paths import runtime_paths, runtime_config

def main():
    workspace, vault, outputs = runtime_paths()
    config_path, config = runtime_config()
    result = {
        'platform': platform.platform(), 'python': sys.version.split()[0],
        'workspace': str(workspace), 'vault': str(vault), 'outputs': str(outputs),
        'config': str(config_path) if config_path else None,
        'skills_dir': config.get('skills_dir'),
        'executables': {name: shutil.which(name) for name in ['git', 'ffmpeg', 'ffprobe', 'capcut', 'blender', 'node', 'bash', 'whisper-cli', 'whisper-cpp']},
        'python_modules': {name: importlib.util.find_spec(name) is not None for name in ['yaml', 'PIL', 'numpy', 'cv2', 'openai']},
        'credentials': {'OPENAI_API_KEY_configured': bool(os.environ.get('OPENAI_API_KEY'))},
        'proof': 'local-discovery-only',
        'not_verified': ['provider login', 'credits', 'media model availability', 'actual production', 'editor compatibility']
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
