# Recovered historical reference

Recovered and adapted on 2026-10-13 from the user's Drive. Historical host-specific prescriptions and fixed ratios do not override the current SKILL.md, current user request or available tools. Do not treat cited provider/model or output-quality claims as current verification.

# Regression and optimization protocol

Use this reference only when the user explicitly asks to improve, evaluate, or repackage this Skill. It protects visual quality from rule accumulation and turns real feedback into controlled changes.

## ChatGPT-first acceptance gates

Treat ChatGPT as the primary deployment surface. A candidate release must preserve all of these behaviors:

- a clear image idea triggers silent internal direction followed by built-in image generation, even when the user does not write `生成图片`;
- the image is the primary result and the optimized prompt, reference map, analysis, and checklist remain hidden unless requested;
- an attached-image edit preserves source ratio, crop, identity, composition, brightness baseline, color relationship, medium, and unrelated regions;
- a short revision such as `亮一点` or `不要太写实` continues from the latest accessible image and changes one requested variable instead of rebuilding the concept;
- a missing source blocks source-dependent editing rather than producing a pretend source-matched prompt;
- planning, critique, reverse engineering, and prompt-only requests remain non-generating when explicitly requested;
- the Skill never claims to have permanently learned or rewritten itself inside ChatGPT.

Keep Codex tests as secondary authoring and diagnostic coverage. Do not let Codex's visible prompt contract leak into the default ChatGPT response.

## Optimization hierarchy

Protect these in order:

1. user intent, current references, and hard constraints;
2. authored visual thesis, composition motive, eye path, and signature decision;
3. focal hierarchy, value readability, and clean-image release gate;
4. medium fit, realism scope, material language, and surface voice;
5. deliverable correctness, edit locality, and multi-shot continuity;
6. prompt economy and host-surface behavior.

Do not raise a checklist score by making every image minimal, photographic, dark, symmetrical, ultrawide, or stylistically similar. `Clean` is not sterile, `cinematic` is not dark, `premium` is not glossy, and `21:9` is not mandatory when the user or deliverable overrides it.

## Golden regression set

Keep a fixed test set outside the deployed Skill. It must cover at least:

| ID | Case | Main regression to catch |
|---|---|---|
| G01 | high-key red/white cloud corridor with one figure | clipped whites, red contamination, corridor clutter, repeated-motif overload |
| G02 | low-key black-clad swordsman in rain | crushed blacks, unreadable face/hand/sword, dirty rain, dark-filter cinema |
| G03 | non-photoreal fantasy or ink/watercolor scene | accidental photorealism, camera jargon replacing medium language |
| G04 | real-person portrait in a stylized environment | identity drift or forcing the whole image into photography |
| G05 | creature or vehicle over a city/landscape | weak scale, equal-detail city, directionless spectacle |
| G06 | game environment or prop concept | beauty image without function, scale, shape language, or usable space |
| G07 | close-up plus three-view character board | identity, scale, view, layout, or lighting drift across panels |
| G08 | composite or local edit | global darkening, crop/perspective drift, cutout edges, unrelated changes |
| G09 | six-shot storyboard | independent-shot drift, broken axis, eyeline, geography, light, prop, or tail-frame logic |
| G10 | reference reverse engineering | subject copying, artist-name dependence, or missing role map |
| G11 | explicit square/portrait ratio | default 21:9 overriding the requested deliverable |
| G12 | negative routing case | script writing, audio work, video QC, API guidance, or file work incorrectly absorbed by this Skill |
| G17 | explicit case-library request plus generation | case retrieval interrupts ChatGPT direct generation, prompt/template leakage, exact-copy behavior, or external-reference homogenization |

Add cases only when they cover a new failure class. Do not create several near-duplicates of the same red/white corridor or character portrait.

## Three validation layers

1. **Static validation:** frontmatter, description length, file links, line limits, navigation, metadata, package structure, and required route/schema terms.
2. **Semantic dry run:** use fresh agents with raw user requests. Check route, assumptions, ChatGPT prompt invisibility/direct-generation intent, Codex output shape, composition logic, medium diversity, edit preservation, cleanliness behavior, and refusal to overreach. Do not tell the agent the expected answer.
3. **Rendered comparison:** when the user explicitly authorizes generation, compare candidate and previous Skill on the same brief, references, model, ratio, and generation count. Inspect outputs; prompt quality alone is not a visual win.

Label every result as `STATIC`, `STRUCTURAL DRY RUN`, or `RENDERED QC`. Never combine them into one unsupported quality score.

## Promotion and rollback rule

For every candidate change, record:

```text
TARGET FAILURE:
EVIDENCE:
RULE CHANGED:
EXPECTED BENEFIT:
GOLDEN CASES TO RE-RUN:
RESULT: keep / narrow / revert / needs rendered evidence
UNRELATED REGRESSIONS:
```

Keep the change only when the target defect improves and no hard gate fails. If two unrelated golden cases regress, revert the rule. If one case regresses, narrow the rule to its correct mode, medium, subject, or failure tag. Preserve the previous working package before every release.

## Anti-homogenization check

Across the golden set, require multiple composition families, at least three medium families, both high-key and low-key scenes, more than one aspect ratio, and both quiet and forceful images. Reject an update when it repeatedly introduces the same corridor, centered hero, low-angle lens, red accent, fog, particles, rim light, shallow depth of field, or photoreal surface without a case-specific reason.

The goal is not one universal look. The goal is stable decision quality across the user's range while preserving a recognizable preference for motivated composition, eye flow, thematic color, narrative continuation, clean richness, and controlled surprise.
