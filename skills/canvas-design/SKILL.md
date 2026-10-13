---
name: canvas-design
description: Design posters, covers and static graphic layouts with readable typography and editable sources. Use for poster composition, Chinese typesetting and multi-size campaign layouts; character, costume and environment concept art belongs to aigc-image-director, and interactive UI belongs to frontend-design.
license: Apache-2.0; complete terms in LICENSE.txt
---

# Poster and Graphic Design

Modified from Anthropic canvas-design on 2026-10-13 for Chinese production, editable delivery and platform-neutral execution. See [upstream snapshot](references/upstream.md) for provenance, not additional mandatory instructions.

## Choose the deliverable

Distinguish a design explanation, prompt-only brief, finished image, or editable layout. Confirm use, size, exact copy, protected logo/product assets and output format when these affect the first action. Never invent event dates, prices, endorsements or a brand logo. Unknown copy can be clearly marked as demonstration copy, not silently finalized.

For posters and covers, lead this layout action directly. Use aigc-image-director only when the main visual needs concept direction or actual image generation. Read [poster production](references/poster-production.md) for copy-heavy Chinese layouts, editable handoff and output checks.

## Direct and build

- Form a short visual thesis tied to this audience and message; translate it into hierarchy, grid, dominant shapes, focal point, palette and type roles. A manifesto is optional, not a mandatory deliverable.
- Respect the approved style, including animation, maximalism or dense information. Minimalism, thin fonts and abstract symbolism are choices, not quality gates.
- Establish first read, second read and essential details. Place all confirmed text at a readable size; do not sacrifice dates, CTA or disclaimers to an artistic preference.
- Separate generated illustration/background from exact text and logo layers. Build exact typography in an editable format supported by the current environment: SVG, HTML/CSS, a requested design editor or an available template tool. Use existing code/vector assets directly; use imagegen only for bitmap creation/editing and read its skill first.
- Use available, licensed fonts with the required Chinese glyphs. Test fallback, weight and line breaks; do not assume a macOS font is installed on Windows or download a font silently.
- Preserve source geometry and protected areas for revisions. Keep the last good version; repair the failing layer before replacing the full composition.

## Verify and hand off

Inspect the actual render at full size and at the intended preview size. Compare all copy, glyphs, margins, crop, focal hierarchy, logo clear space and asset identity. Retain the editable source when requested; PNG alone is not an editable layout.

For print, get the printer's actual bleed, color profile and PDF requirements. Screen RGB preview is not print approval. Export only formats actually produced and checked; if a required renderer/editor is missing, name the blocked format and preserve the source.

For substantial criticism or a learning request, use aigc-design-review. Ordinary self-checks do not require a separate long audit. Explain one important design decision or contrast when the user wants to learn, without turning every delivery into a lesson.
