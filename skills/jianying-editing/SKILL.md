---
name: jianying-editing
description: >-
  Inspect and safely edit local JianYing/CapCut projects, including subtitles,
  timing, speed, volume, text, transitions, animations, and long-form-to-short
  workflows. Use when the user mentions 剪映, JianYing, CapCut drafts, draft
  timelines, subtitle correction, or asks to make an editable short-video draft.
---

# JianYing Editing

Operate on a local JianYing/CapCut draft as an editable timeline. Prefer the
installed `capcut` CLI and its version-aware schema handling; do not hand-edit
`draft_content.json` when a CLI command exists.

## Scope

Use this skill for:

- inspecting a draft's tracks, materials, captions, timing, and compatibility;
- correcting or restyling captions and text layers;
- changing clip timing, speed, volume, opacity, trims, transitions, keyframes,
  masks, chroma key, or smart matting;
- refining a user-assembled AIGC manga/drama rough cut into a reviewed fine cut;
- creating a reviewed long-form-to-short draft;
- preparing a draft for the user to open and finish in JianYing.

Do not treat this skill as a replacement for creative review in JianYing. Do
not publish, upload, or overwrite the user's only draft without an explicit
request.

## Required workflow

1. Identify the exact draft directory and confirm whether JianYing is open.
2. For any write, ask the user to close JianYing first unless the CLI's
   conflict check explicitly confirms the editor is closed.
3. Start with read-only inspection. Use `scripts/inspect-draft.sh` for a
   compact overview instead of dumping project JSON.
4. Convert the user's request into a bounded edit plan: target tracks or
   segment IDs, time range, intended change, and expected result.
5. Use `capcut describe` as the command and schema source of truth. Do not
   invent flags or enum values; use `capcut enums --jianying` when a visual
   effect, transition, mask, or font slug is needed.
6. Run a dry-run or lint check when the command supports it. For multi-command
   edits, use or create a parameterized script under `scripts/`.
7. Apply the smallest edit that satisfies the request. Preserve the original
   draft, rely on the CLI's `.bak`/history behavior, and report the changed
   project path and verification result.
8. Reopen JianYing only after the write has completed, then ask for a visual
   check of the affected range before any larger batch edit.

## Routing

- Existing JianYing draft: use this skill and `capcut` directly.
- Raw talking-head or interview footage: use `auto-edit-video` for semantic
  rough-cut proposals and local transcription when available, then import or
  rebuild the approved result in a JianYing draft.
- Deterministic media preparation: use `ffmpeg`; keep source media unchanged
  and verify derivatives before adding them to a draft.
- AIGC manga/drama reference analysis: use `aigc-manga-video-director`; this
  skill owns timeline assembly, not shot interpretation.
- AIGC manga/drama rough cut supplied by the user: read
  [references/manga-fine-cut-workflow.md](references/manga-fine-cut-workflow.md),
  then use the transition, effect, and sound references it routes to. Treat
  every embellishment as a narrative decision; hard cuts and silence remain
  valid choices.
- Final generated-video acceptance: use `aigc-output-qc`; do not claim a
  timeline edit passed merely because the JSON is valid.

## Non-obvious invariants

- Never write while JianYing is open, and never use `--force-write` unless the
  user explicitly accepts overwriting changed-on-disk state.
- Use a copied test draft for the first run on a new JianYing version.
- Audio segments do not have video clip geometry; do not apply opacity, scale,
  or position edits to audio-only segments.
- Timing values must use the CLI's supported time syntax. Speed changes affect
  source/timeline duration math; do not calculate this ad hoc in prose.
- A project can contain multiple readable timeline files. Trust the CLI to
  synchronize them and keep its backups.
- Media path fixes are a separate operation from creative editing. Diagnose
  missing media before attempting relink or staging.

## Supporting references

- Read [references/workflows.md](references/workflows.md) when choosing an
  edit route or combining more than one CLI operation.
- Read [references/safety-and-compatibility.md](references/safety-and-compatibility.md)
  before the first write, a JianYing upgrade, or any draft migration.
- Read [references/manga-fine-cut-workflow.md](references/manga-fine-cut-workflow.md)
  when the user provides an AIGC manga/drama rough cut for detailed refinement.
