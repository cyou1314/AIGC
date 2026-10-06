# Task Modes

Choose the smallest mode that completes the current request.

| Mode | Trigger | Default output | Stop condition |
| --- | --- | --- | --- |
| 快速诊断 | Existing story or script; user asks to analyze, diagnose, evaluate, or identify problems | Prioritized issue list and repair directions; no rewritten script text | The user can decide whether anything should be rewritten |
| 原创开发 | User asks to create a story, episode, scene, or dialogue from an idea | Confirmed story spine, then only the requested next artifact | A major story boundary needs confirmation |
| 改编重构 | Source work must be adapted to a new format, duration, audience, or episode shape | Preserve/change contract, revised spine or beat structure | Source rights or protected elements are unclear |
| 局部重写 | User explicitly asks to rewrite, improve, polish, or accepts a proposed repair for one scene, beat, hook, relationship, or dialogue section | Complete replacement for the smallest authorized unit | Fix would alter a locked upstream fact |
| 导演交接 | Story content is confirmed and ready for storyboard direction | Director handoff contract | Unresolved narrative questions would change staging |

## Fast Path

Use `快速诊断` by default:

1. Restate the intended story effect in one sentence.
2. Identify up to five highest-impact problems.
3. Give the lowest-cost repair for each.
4. Do not provide replacement script text. Ask for one decision only if the user wants a proposed repair implemented or if it changes a protected story boundary.

Diagnosis never authorizes rewriting. Do not expand into a local or full rewrite without an explicit request or acceptance.

## Full Development Path

Use only when explicitly requested:

1. Confirm premise, protagonist goal, obstacle, stakes, and ending direction.
2. Build beats.
3. Expand selected beats into scenes.
4. Write or revise dialogue.
5. Run narrative self-check.
6. Create director handoff.

## Routing Away

- Confirmed script needing storyboard, blocking, composition, camera, or Seedance prompts: `aigc-manga-video-director`.
- Multi-turn project state and prompt revision: `aigc-project-prompt-loop`.
- Spoken delivery, transcription, timing, pauses, or lip-sync evidence: `audio-to-prompt` or `transcribe`.
- Generated video acceptance and repair decision: `aigc-output-qc`.
