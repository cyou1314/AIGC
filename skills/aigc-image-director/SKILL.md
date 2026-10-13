---
name: aigc-image-director
description: Direct AIGC still-image work including character and scene design, concept art, cinematic frames, posters, product visuals, visual identity, reference mapping, image editing and image critique. Use when the output or requested direction is a still image; moving-shot choreography stays with the video director. Coordinate actual generation through an available image tool.
---

# AIGC Image Director

Select the requested mode: design/critique, prompt-only, actual generation/edit, or a consistent image set. A request to make an image continues to actual generation when a tool is available. Read `{{AIGC_VAULT}}/learning/图像导演与视觉设计能力.md` when cinematic composition, reference mapping or continuity needs deeper guidance. Historical platform/model prescriptions in that page are references, not current capability guarantees.

## Professional design branches

Read only the branch needed for this action: [characters](references/characters.md) for identity/silhouette/multi-view, [costumes](references/costumes.md) for layers/material/function, and [environments](references/environments.md) for usable space/perspective/continuity. For mixed visual development maintain shared character, costume and scene IDs rather than three disconnected styles.

Poster composition with substantial typography is led by canvas-design; this skill owns its generated main visual. UI/web layout is led by frontend-design, not image generation. Explicit design critique or a learning comparison can use aigc-design-review; video QC remains separate.

Recovered methods are indexed in [recovery and sources](references/recovery-index.md). For multi-reference edits read [reference control](references/legacy-reference-control.md); for an under-authored composition read [composition engine](references/legacy-creative-composition-engine.md); for requested style/light/value diagnosis read [art direction](references/legacy-aesthetic-art-direction.md) or [visual diagnosis](references/legacy-visual-diagnosis.md). Current user intent, output format and this entrypoint override historical host presets. Do not load all recovered references for every image.

## Direct the image

1. Identify visual purpose and viewing context. Use the user's size/crop; otherwise infer from the intended artifact and state consequential assumptions. A movie frame may use 21:9; a poster, product listing, thumbnail or character sheet must use its own layout. Editing inherits source geometry unless a change is requested.
2. Map each supplied reference to identity, product detail, pose, composition, scene, color or material. Lock what must remain stable. An identity sheet does not require reproducing its white background, labels or multi-view layout.
3. Define the focal anchor, eye path, foreground/background relationships, lighting direction, material response and readable silhouette. Give concrete direction rather than adjective piles. Exact copy and logos use the user's supplied assets or confirmed text.
4. For edits, inspect the source and specify the bounded change plus protected areas. Preserve identity, untouched objects, crop, color and brightness baseline as applicable. For sets, establish a compact visual bible and vary only the intended item/shot.
5. Read the selected execution skill. Default actual bitmap generation/editing to `imagegen`; explicit Cowart requests use the appropriate Cowart skill and keep results on its canvas. Template-based typography/design can use Adobe template capabilities. Do not assume any provider's access or fixed model parameters from historical notes.
6. Check the actual output against identity/product detail, reference role, composition, text, crop and requested format. Record visible limitations or necessary local repair. Return the actual image, not just its prompt.

## Efficient variants

For a costly set, establish one representative accepted direction first. Reuse approved identity and assets; do not regenerate the full set for a small local error. When alternatives materially change style, cost or editability, describe the tradeoffs rather than replacing the user's choice.

For static storyboards pass stable panel IDs and continuity anchors to `storyboard-image-replacer` or the video director. Do not add motion/audio choreography to a single-image prompt. A real image receipt does not imply the matching video was generated.
