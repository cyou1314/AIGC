---
name: frontend-design
description: Design and implement intentional UI and responsive web interfaces in the user's existing stack, including layout, typography, component states and visual review. Use for requested UI/web design or redesign, not generic backend work, posters or character concept art.
license: Apache-2.0; complete terms in LICENSE.txt
---

# UI and Web Design

Modified from Anthropic frontend-design on 2026-10-13 for Chinese interfaces, existing-repository integration and evidence-based delivery. The [upstream snapshot](references/upstream.md) preserves the source; it is not a second mandatory workflow.

## Design the actual user path

Identify product, audience, primary task, requested artifact and existing constraints. A UI mockup, working local interface and deployed app are different outputs. Preserve existing stack, components, tokens and approved brand. Do not create a new hosted site when the user wants a local component or repository edit.

For new directions, make a compact plan with subject-specific visual premise, content hierarchy, color/type/spacing roles and core user flow. Compare alternatives only when the choice matters. Do not default to the same card grid, editorial look or cinematic palette across unrelated products; equally, do not ban a style the user explicitly wants.

Read [UI delivery](references/ui-delivery.md) for state, responsive and verification requirements. A backend-only feature does not require visual redesign.

## Build with usable states

Implement the requested scope with semantic elements and real content where available. Keep Chinese copy clear, label actions by their result, and mark invented demonstration data. Map spacing, color and type to a small token system; reuse the existing system instead of hardcoding a competing one.

Include the states relevant to the task: keyboard focus, active/selected, empty, loading, validation, error and success. Do not show fake functional buttons or fabricated customer statistics. If only a mockup is requested, label nonfunctional interactions explicitly.

Use appropriate local/licensed fonts with CJK fallback and test mixed-script line breaks. Keep effects subordinate to task clarity; respect reduced motion. Prioritize readable contrast and visible focus over novelty.

For requested Figma-native work use the available Figma workflow and check connection first. Do not imply a Figma file was created from HTML. When unavailable, deliver the authorized local alternative with its limitation; publishing or new service setup needs its own authorization.

## Verify the artifact

Run existing meaningful tests and the core user path. Inspect real desktop and narrow-screen renders, overflow, text, focus order, labels and relevant error states. Code validity and screenshots do not prove backend functionality or deployment. If browser execution is unavailable, state that runtime/visual checks remain unverified.

For substantial review or a learning request use aigc-design-review. Repair the largest task/visibility problem first. Preserve accepted assets; avoid a full redesign to fix one component. Summarize what was actually tested and return source plus preview where useful.
