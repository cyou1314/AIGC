---
name: obsidian-codex-knowledge-loop
description: Maintain persistent project pages, knowledge capsules, generation and delivery receipts, closeout memory, Drive/Obsidian knowledge organization and evidence-based Skill promotion for AIGC work. Use for project recovery, state updates and knowledge governance. Select a new project's production type through aigc-production-router; this skill owns memory, not creative production.
---

# Obsidian Codex Knowledge Loop

The active independent Obsidian vault is `{{AIGC_VAULT}}`, confirmed by its AGENTS.md. Do not assume a placeholder `[vault]/Codex` path or restore old project history wholesale. Start important work by reading vault AGENTS.md. Recover an existing page's snapshot and knowledge capsule before expanding into other knowledge.

## Project routing

Use `aigc-production-router` for a new or mixed project's production type. Read only the selected type's contract and specialist guidance. For established projects and explicit specialists, proceed directly. The original R0–R8 modules remain available for narrative work; not every image, audio, research or software project uses them.

Read `{{AIGC_VAULT}}/agent/跨类型AIGC生产工作流.md` for cross-type entry points. Read `01-快速路由.md` and `agent/AIGC生产规则.md` when narrative modules apply. Use `agent/Obsidian-Codex知识闭环.md` for knowledge promotion and Drive governance.

## State and evidence

The project page owns goal, production type, authoritative input/version, lead Skill, delivery contract, constraints, budget if known, output paths and one next step. A specialist may own a technical manifest or editable timeline; link that file instead of mirroring its changing details.

Use `scripts/project_state.py` to initialize, update and validate pages. An uncertain project starts as `pending`, never automatically as drama. Existing pages remain readable; do not reinitialize them to add fields. Add only the needed contract or receipt section in place.

```bash
python3 {{SKILL_ROOT}}/obsidian-codex-knowledge-loop/scripts/project_state.py init --name "商品海报" --domain image --goal "制作已确认文案的海报" --deliverable "PNG海报" --next "确认商品和文案参考"
```

- `snapshot` changes phase, goal, authority, lead, blocker or next step and synchronizes the resume point.
- `receipt` records real generated assets with states `候选 / 采用 / 成片 / 废弃`. The same asset/version status is updated without duplicating the row. Use `采用` for a final still/audio/3D asset; `成片` for video.
- `delivery` records text, files or generated outputs separately, with optional checking evidence. A technical validity check and creative acceptance are different; the evidence file states what was actually checked.
- `validate --check-files` checks state structure and real receipt paths. It cannot prove generation provenance or creative quality. Do not label a merely existing file as generated without a production source.
- `--force` reinitializes a page only after creating a timestamped backup; routine continuation never uses it.

## Availability and closeout

Discover only the selected action's runtime/provider requirements at execution time. Prior migration reports and catalog files do not prove present login, credit, runtime or generation readiness. Preserve missing stages as `blocked-runtime` or `blocked-provider` with a specific next action. Do not use the paused Antigravity route.

On closeout, record actual output, user acceptance or the scope of performed checks, and the resume point. User confirmation of a video may close the project without extra video-content QC; follow the user's explicit analysis request and the producing specialist's necessary output checks. Production checks for audio, 3D, documents or software follow their own contract.

Keep reusable observations as project candidates. Run broad promotion only at the scheduled review or explicit upgrade task. Never claim rules were updated if no file change occurred. Unresolved cross-project items go to vault TODO.md. No credentials, raw chats or large media in memory. Drive remains a source/archive/fallback; never reverse-sync an empty local vault over it.

## Workflow source updates and GitHub closeout

The user requests scoped local AIGC workflow updates to reach the configured AIGC repository. Its visibility and registered source exclusions are machine-specific: inspect the current sync configuration, and do not assume the repository is private.
After changing a registered production Skill, shared workflow knowledge or template,
follow the configured repository's docs/AUTO_SYNC.md and run scripts/sync_github.py run
with a validated Python interpreter. This standing instruction authorizes scoped
workflow commits and normal pushes only, not personal project pages, media or secrets.
Only a matching remote-main SHA confirms synchronization. On merge/privacy/validation/
authentication failure, retain local changes and record the blocker; never force-push,
discard user changes or label an unpushed commit as synchronized. Newly added workflow
sources must be registered before claiming coverage. Regular creative project-memory
updates alone do not authorize publishing private project data.
