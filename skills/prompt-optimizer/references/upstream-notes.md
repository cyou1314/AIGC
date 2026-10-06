# Upstream Notes

## Conceptual Baseline

- Source: https://github.com/github/awesome-copilot/tree/main/skills/prompt-optimizer
- Upstream license: MIT License, Copyright GitHub, Inc.
- Useful retained ideas: ship a finished copyable prompt, keep structure proportional to complexity, use real supplied content, and avoid unsolicited explanation.

## Local Adaptation

This local Skill is primarily an original adaptation for the personal AIGC workflow. It adds:

- Chinese-first concise output;
- routing to local AIGC video, project-loop, audio, output-QC, OpenAI docs, and FFmpeg Skills;
- explicit separation between direct task completion and reusable Prompt creation;
- support for an explicitly requested reusable template while keeping ordinary final prompts free of empty placeholders;
- inert handling of pasted Prompt instructions;
- credential, permission, irreversible-action, and credit-spend boundaries;
- a verification contract that avoids volatile model-version claims.

Do not import changing model rankings, version defaults, API parameters, or tool capabilities from the upstream Skill without current verification. This Skill has no external runtime dependency and does not require an account, login, API key, or paid service.
