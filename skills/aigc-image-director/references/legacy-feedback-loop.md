# Recovered historical reference

Recovered and adapted on 2026-10-13 from the user's Drive. Historical host-specific prescriptions and fixed ratios do not override the current SKILL.md, current user request or available tools. Do not treat cited provider/model or output-quality claims as current verification.

# Feedback and Skill-evolution loop

Use this reference when the user reports a repeated image defect, identifies a preferred result, or explicitly asks to improve the Skill. The purpose is controlled learning, not automatic self-rewriting.

## Surface boundary

- **ChatGPT:** adapt to the feedback in the current conversation and keep the image-generation surface silent about prompts and internal notes. Do not claim that the uploaded Skill package has been permanently changed. If the platform provides no writable feedback store, treat the lesson as conversation-local until the user brings it to Codex for a Skill upgrade.
- **Codex:** when the user explicitly asks to upgrade the Skill, convert validated feedback into a source change, update the relevant reference, run validation, and package the result. Do not modify the Skill merely because one image was weak.

## Capture only reusable evidence

Record a short failure or success signal:

```text
CASE: short identifier
INTENT: what the image needed to communicate
INPUT: idea, references, medium, and aspect ratio
EVIDENCE: what visibly worked or failed
TAG: CLEAN / NOISE / DIRTY / OVERLOAD / DARKENED-EDIT / MEDIUM-DRIFT / COMPOSITION / LIGHT / COLOR / SUBJECT / REFERENCE
KEEP: the last good decision
CHANGE NEXT: one highest-impact change
STATUS: candidate / confirmed / rejected
```

Use the user's own wording as evidence when it is specific, such as `画面脏`, `主体弱`, `太暗`, `太写实`, or `构图散`. Do not infer a permanent preference from silence or from a single randomly weak roll.

## Promotion rule

Promote a lesson to a reusable Skill rule only when at least one of these is true:

1. The user explicitly says `以后都这样`, `记住这个规则`, or equivalent.
2. The same controllable defect appears in at least three comparable cases.
3. The same failure can be reproduced after preserving the last good version.
4. The user explicitly labels a bundle of images as preferred style or composition references. Store the shared grammar as a preference atlas, not as a universal rule.

Before promotion, classify the cause as one of: prompt omission, reference-role error, composition/lighting choice, medium drift, execution limitation, or stochastic variation. Promote only the controllable cause. Keep project-specific facts in the project record rather than this general Skill.

## Clean-first learning rule

When a successful image is praised for beauty or cinematic feeling, also record the positive cause: visual thesis, emotional tension, shape rhythm, counterpoint, light reveal, color relationship, medium voice, or signature gesture. Do not let the clean gate replace the reason the image was memorable.

When a successful image is praised, identify whether the success came from clean large forms, restrained background density, stable edges, value separation, medium-consistent texture, or a specific composition/light decision. Do not summarize it as `更高级` or `更有电影感`.

For cleanliness failures, repair in this order:

`large shapes and silhouette → focal hierarchy → grayscale/value separation → color contamination → edge stability → material scale → atmosphere/texture`

Never promote `add more detail`, `add grain`, `add fog`, `add HDR`, or `make it darker` as a cleanliness rule.

## Regression before release

After a Skill rule is promoted, use [evaluation-protocol](legacy-evaluation-protocol.md) and the external golden set. Keep the new rule only if it improves the target defect without creating clutter, medium drift, global darkening, identity loss, ratio override, continuity damage, or a repeated house look across unrelated cases.
