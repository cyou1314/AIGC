---
name: aigc-design-review
description: Review posters, character/costume/environment concept designs and UI/web interfaces with visible evidence and prioritized repair decisions. Use for design critique, acceptance, A/B learning or a requested design-workflow improvement; video QC stays with aigc-output-qc.
---

# Design Review and Learning

## Evidence before judgment

Read the approved brief, exact copy/identity anchors and actual artifact. A source file, design plan, screenshot and working UI provide different evidence. If the artifact is missing, give only a brief/source-level review; do not invent visual defects or mark rendered QC passed.

Select only the applicable part of [review and learning](references/review-learning.md). A routine creation self-check can stay with its producer; this skill owns explicit critique, acceptance and reusable-learning requests, not every creative task.

## Make the repair actionable

For each material finding provide visible evidence/location → consequence for this purpose → proposed change → protected elements → verification. Separate observed defects, possible causes and taste choices. Prioritize identity, factual copy, core interaction and export correctness before surface polish. A serious defect blocks acceptance even if the rest looks good.

Use a short prioritized list, not an arbitrary beauty score. Keep the last accepted version and repair the smallest useful unit. Return a change specification; do not edit source or regenerate unless the user requested that action. Unclear identity/reference conflicts require the missing reference or choice, not blending by guesswork.

For UI, exercise relevant controls in a real browser when available; screenshots cannot prove interaction. For concepts distinguish a persuasive illustration from a usable multi-view asset, buildable costume or navigable environment.

## Learn without pretending to train

When learning is requested, compare the baseline and one controlled change against the same brief. Record intent, artifacts/versions, actual inspection, kept decision, changed variable, outcome and limits in the project's learning candidate. Leave unknown time/spend/generation counts unknown. A deterministic reproduction or explicit standing user rule can justify a narrow promotion; one attractive result does not establish a universal style.

Use obsidian-codex-knowledge-loop for persistent project evidence. Promotion to a shared Skill requires the upgrade request/scheduled review, appropriate regression and GitHub closeout; do not silently self-rewrite after every criticism.

The optional `scripts/review_gate.py` validates a structured review's evidence and severity bookkeeping. It cannot inspect images, judge aesthetics or certify a working app. Do not turn its output into a visual-quality claim.
