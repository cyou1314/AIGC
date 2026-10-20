---
name: aigc-production-router
description: Choose and run the appropriate AIGC production workflow for a new, mixed, or unclear project, including image design, narrative video, commercial content, presenter video, postproduction, audio, 3D, knowledge artifacts, and digital products. Use for 开始新项目 with no established workflow or requests to adapt an AIGC workflow across types. An explicit specialist or an established project path takes priority.
---

# AIGC Production Router

Match the requested deliverable to one production profile in [references/production-profiles.json](references/production-profiles.json). This catalog is the shared route source for the memory layer and local planner. Choose by deliverable and purpose, not by a lone keyword, model name, or the word “开始”.

Within image: overseas short-drama poster prompts/visual direction select the company poster branch in aigc-image-director; actual editable poster/cover typography and layout select canvas-design; character/costume/environment or image editing select aigc-image-director. Within digital: requested UI/web design selects frontend-design while hosting/backend/SDK work keeps its platform route. Explicit design critique selects aigc-design-review without authorizing generation or edits. These are specialized leads within existing profiles, not three new compulsory production stages.

## Select the next production action

1. Recover an existing project snapshot when available. Preserve the user's chosen tool and deliverable; a local task does not restart the project. If a specialist is explicitly named, follow it directly.
2. Infer the production profile from supplied materials and goal. If no meaningful first action can be selected, ask one question about the intended output. Record uncertainty rather than silently assuming a short drama.
3. Use `obsidian-codex-knowledge-loop` for project state. Small one-off answers do not require a new project. Read only this profile's relevant references and specialist SKILL.md files.
4. Select one lead specialist for the current action. Use collaborators only at concrete handoffs. The planner lists candidates; it does not launch them all.
5. Produce the requested artifact, verify the aspects necessary for that artifact, and update the project page. A prompt-only request stops at the prompt; a finished-video request continues through generation and editing if tools and authorization support it.

Read [references/production-contracts.md](references/production-contracts.md) when selecting output requirements, handoffs, cost controls, or cross-domain work. It contains type-specific acceptance conditions, especially for audio, 3D, research, and software.

## Tool availability

Use `scripts/workflow_plan.py list`, `plan --domain image`, or `inventory` for local catalog/discovery checks. Local discovery proves files or executables exist; it does not prove account login, credits, plugin connection, or real output quality. Check the relevant provider with its own tools when actual generation is requested. Do not make network calls to every service at project start.

If a dependency is absent, state the missing dependency and which next action it blocks. Continue independent preparation. A cheaper alternative can be used when it meets the same output contract; if it changes fidelity, output type, privacy, or cost materially, explain the tradeoff and let the user choose.

## Keep the workflow efficient

- For mixed deliverables, create linked work packages under one project: e.g. image identity → product video → subtitle/export. Each package has one owner and a stable asset path. Store technical edit state in its specialist manifest and link it from the project page; do not duplicate timecodes by hand.
- For costly batches, test a representative image, audio passage, or difficult shot before propagating the accepted direction. Reuse approved assets and repair locally when possible.
- Respect user-approved budgets. If no budget was supplied, mark it unknown. Do not treat a catalog entry as permission to subscribe, publish, or mass-generate.
- Record preparation time, actual generation attempts, known spend, adopted outputs, and repair reasons when available. Unknown values remain unknown. Judge optimization by these results rather than skill count.
- Preserve the original narrative R0–R8 modules. They are available operations, not mandatory stages for every output.
