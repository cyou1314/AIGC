#!/usr/bin/env bash
# Codex Cloud setup AND maintenance script. Bash required; no downloads or generation.
set -euo pipefail
if [[ -n "${AIGC_REPO_ROOT:-}" ]]; then
  aigc_repo="$AIGC_REPO_ROOT"
elif [[ -f "scripts/cloud_bootstrap.py" ]]; then
  aigc_repo="$PWD"
elif [[ -f "/workspace/AIGC/scripts/cloud_bootstrap.py" ]]; then
  aigc_repo="/workspace/AIGC"
else
  echo "AIGC checkout not found; set AIGC_REPO_ROOT in environment settings." >&2
  exit 2
fi
if command -v python3 >/dev/null 2>&1; then
  aigc_python=python3
else
  aigc_python=python
fi
"$aigc_python" -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
export PYTHONDONTWRITEBYTECODE=1
aigc_workspace="${AIGC_WORKSPACE:-$(dirname "$aigc_repo")/AIGC-workspace}"
"$aigc_python" "$aigc_repo/scripts/validate.py" --structure-only
"$aigc_python" "$aigc_repo/scripts/cloud_bootstrap.py" \
  --workspace "$aigc_workspace" \
  --vault "${AIGC_VAULT:-$aigc_workspace/Codex}" \
  --outputs "${AIGC_OUTPUT_ROOT:-$aigc_workspace/outputs}" \
  --skills-dir "$HOME/.agents/skills" \
  --instructions-file "${AIGC_INSTRUCTIONS_FILE:-$(dirname "$aigc_repo")/AGENTS.md}"
"$aigc_python" "$aigc_repo/scripts/doctor.py"
# The CLI may not yet be installed during setup. Verify the actual runner in a new task.
if command -v codex >/dev/null 2>&1; then
  "$aigc_python" "$aigc_repo/scripts/check_codex_discovery.py" --cwd "$aigc_repo" --cwd "$(dirname "$aigc_repo")"
else
  echo "Codex CLI absent in setup phase; native Skill discovery awaits the agent phase."
fi
