# Recovered historical reference

Recovered and adapted on 2026-10-13 from the user's Drive. Historical host-specific prescriptions and fixed ratios do not override the current SKILL.md, current user request or available tools. Do not treat cited provider/model or output-quality claims as current verification.

# Visual diagnosis and reference reverse engineering

Use this reference when the user provides an existing image, failed output, preferred reference, social post, or asks how to reproduce a visual result. Inspect the actual image when available; otherwise label the result as prompt-level inference.

## Diagnostic contract

Return or reason in this order:

```text
MODE: image critique / edit diagnosis / reference reverse
EVIDENCE: what is visibly present or absent
IMPACT: how it harms hierarchy, story, usability, or continuity
LIKELY CAUSE: composition / camera / staging / light / color / medium / material / atmosphere / artifact / stochastic variation
FIX: one highest-impact controllable change
IMPROVED PROMPT: one complete prompt or edit contract
VERIFICATION: inspected image / prompt-level only / rendered QC not available
```

Do not call a structural prompt review a rendered QC pass. For a local edit, use `CHANGE ONLY`, `KEEP UNCHANGED`, and tonal preservation. For a broad redesign, state which locked elements are intentionally released.

## Inspect in layers

1. **Composition:** subject clarity, crop, balance, focal point, line termination, negative space, foreground/midground/background, scale relationship, and whether the frame has a motive.
2. **Camera:** shot size, height, angle, camera side, lens perspective or compression, horizon, focus plane, and distortion.
3. **Staging:** body/prop contact, gaze, screen direction, landmark geography, action vector, and usable continuation space.
4. **Light and value:** source direction, key/fill/rim/negative fill, shadow readability, highlight roll-off, high-key clipping, low-key crush, and atmosphere as a depth cue.
5. **Color:** dominant/supporting/neutral/accent relationship, temperature contrast, saturation hierarchy, and narrative color function.
6. **Environment and design:** landmark, navigable path, scale reference, big/medium/small shapes, repetition/variation, material variation, construction, and environmental storytelling.
7. **Medium and surface:** realism scope, silhouette, edge behavior, brush/line/wash/3D/print language, texture scale, and medium drift.
8. **Cleanliness:** random noise, muddy fields, broken edges, equal-detail clutter, accidental halos, directionless particles, and global darkening after edits.

## Reverse-engineer a reference

Extract named roles instead of a literal prompt:

```text
REFERENCE ROLE MAP
COMPOSITION: crop, subject scale, dominant shapes, line endpoints, counterweight
CAMERA: shot size, height, angle, perspective/compression, focus
SPACE: foreground / midground / background jobs, landmark, horizon, scale
LIGHT: source, direction, softness, value pattern, focal reveal
COLOR: dominant / supporting / neutral / accent and story function
MATERIAL: surface response, edge behavior, texture scale
MEDIUM: photographic / painterly / ink / watercolor / 2D / 3D / graphic / hybrid
ATMOSPHERE: source, direction, depth layer, density
SIGNATURE: one memorable decision
DO NOT COPY: identity, exact subject arrangement, watermark, text, creator signature, exact prompt
```

For multiple references, assign each image a role such as identity, pose, composition, environment, lighting, palette, material, medium, or edit target. If roles conflict, keep one primary source and borrow only named layers from the others. If three or more references repeat a trait and the user explicitly likes the bundle, promote it to the user aesthetic atlas as a preference—not a universal template.

## Defect-to-fix examples

| Evidence | Diagnose | First fix |
|---|---|---|
| beautiful subject but eye has nowhere to travel | composition motive / eye path missing | add one destination or counterweight and terminate the strongest line there |
| many details but image feels dirty | overload, not insufficient detail | simplify large shapes, demote repeated motifs, restore quiet tonal fields |
| cinematic means dark and muddy | cinematic imbalance | restore midtones, define motivated key/fill/rim, protect whites and blacks |
| edit changed the whole exposure | darkened edit | repeat tonal-preservation and local-match locks; keep the change local |
| concept art looks like generic photo | medium drift | choose a surface authority and limit realism to identity, structure, or material credibility |
| reference prompt is only artist name + adjectives | low-information / style-label dependence | reconstruct shape, camera, light, color, material, atmosphere, and signature |
