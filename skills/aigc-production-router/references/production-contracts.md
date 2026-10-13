# Production contracts

Use only the section matching the requested output. The profile is a default route, not a compulsory pipeline.

## Shared brief and handoff

Record `生产类型｜本轮交付物｜用途/受众｜权威输入｜保持项｜允许修改项｜输出规格｜已知预算｜完成证据｜唯一下一步` in the project page. Unknown fields are unknown; ask only when they block the first action. Record the reason when changing production type.

At a handoff send `来源路径/版本｜输入职责｜要解决的问题｜保留项｜输出路径/格式｜必要核验｜接收者`. A character image locks identity; it does not impose its white background or grid on a video. An audio passage locks spoken timing; estimates must not overwrite it.

## Narrative

Use the existing project prompt loop and applicable R1/R2/R4/R5/R6 modules. Scripts, reference matching, continuity, time contracts and actual tail frames remain relevant. Request-specific QC is optional; the necessary verification of a newly rendered deliverable still applies. Confirmation of a final file is sufficient for project registration, not proof of frame-by-frame review.

## Image

Use `aigc-image-director`. Confirm where it will be viewed or printed before choosing crop and text layout. Text rendering, final visual dimensions and protected product details matter more than adding style adjectives. For multi-image identity, prove the direction on a representative frame, then propagate.

Poster/cover layout with exact typography selects canvas-design; generated main visuals stay with the image director. Character, costume and environment design have separate references but shared identity/world anchors. Editable layout, costume pattern and buildable space are distinct contracts; do not deliver a flat image as all three. Explicit design review uses aigc-design-review and records source/render/interaction evidence separately.

## Commercial content

Use `aigc-commercial-content`. Connect one message to observable product evidence. Distinguish finished-video production from concept/script-only requests. Choose the UGC form from the explicit creative intent: product-only, unboxing, try-on, tutorial, website demonstration. For ordinary brand cinema route shot work to the existing video director, not UGC by default.

## Presenter / explainer

First distinguish an on-camera presenter, explicitly faceless narration, supplied real presenter footage, and a script-only deliverable. Lock the accepted identity/voice; check actual speech duration and supporting image alignment. Use `ai-host-video`, `faceless-video`, `auto-edit-video`, or a writing specialist accordingly. Narrator and subtitle specialist triggers remain authoritative. A general voiceover request alone does not automatically invoke `narrator`.

## Postproduction

Existing JianYing/CapCut draft: use `jianying-editing` as the lead, with `capcut-edit` as the command reference. Inspect the exact draft, back it up via the supported tool and comply with open-editor conflict checks. Editable project delivery and rendered MP4 are distinct. JSON validation cannot prove playback quality.

Raw local speech footage with automatic cleanup requested: `auto-edit-video`. Run its own preflight; do not infer readiness from a CLI file. Deterministic trimming/conversion: `ffmpeg`. Requested Higgsedit composition: `video-editing`. Burned captions: `subtitles` or an applicable local renderer. A caption style suggestion does not trigger video rendering.

Basic export verification is part of making an output: decoding, media presence, requested duration/size, caption legibility and representative listening where relevant. Additional editorial QC is triggered by the project request, not by mere file registration.

## Audio

Use `aigc-audio-production`. Transcription, voice generation, score/sound generation, mixing and audio-to-visual prompting are separate operations. Installed transcription support does not imply a TTS or music generator exists. If requested creation cannot be executed, provide the production specification and state the missing provider; do not call that an audio deliverable.

Measure durations from files. Verify intelligibility, pronunciation, seams, silence and distortion by listening to the relevant passage. Use delivery-specific audio specifications from the user or verified target requirements, not a universal loudness preset. Music and sound design need temporal landmarks and explicit scene purpose.

## 3D / previs / printing

Choose the intended consuming system first: game, animation, product render, previs, or physical print. Read the appropriate Meshy skill when executing Meshy generation, edits, rigging or printing. A `.glb`/`.fbx`/scene artifact must be imported or checked with a suitable runtime before promising integration compatibility.

For previs, inspect static geography → screen positions/headings → fixed-camera action → camera/editing as complexity requires. Technical rendering success does not establish directorial correctness. Blender discovery is only a readiness check; scene scripts and actual execution need separate verification. If unavailable, camera/blocking specifications can proceed and the render remains blocked.

For printing, dimensions, closed geometry, wall thickness and slicer/material constraints apply. Do not send a print job merely because a digital model was requested. Game engine-specific performance and topology limits require the target engine/project; avoid universal counts.

## Research / documents / data

Research uses authoritative sources and distinguishes source-supported facts, inference and proposals. Writing or reorganizing user-provided material does not need unnecessary external research. Select the document, presentation, spreadsheet or PDF skill by the actual artifact. Follow its required render/recalculation checks. Do not force a storyboard into a research report.

## Software / interactive products

Respect existing code and instructions; select a platform only when one is needed. Hosted Sites, Higgsfield products, provider-specific Agent SDK work, and an existing local repository are separate routes. API/provider requirements are checked through the chosen specialist. Run the core user path and meaningful tests; a screenshot or code listing does not establish an operational app. Publishing follows the user's actual authorization.

Requested UI/web visual and interaction design selects frontend-design; preserve existing tokens/components and platform route. Verify relevant states, keyboard/focus, long Chinese text and desktop/narrow-screen behavior. Figma-native editing requires an available Figma integration; local HTML is not a Figma file. Do not require Figma setup to deliver an authorized local webpage.

## Cost and iteration

Before high-volume work, test the cheapest representative unit that will expose the likely failure: product detail, recurring face, difficult action, vocal name, or editable project import. Record accepted examples as anchors. Repair a local failure before replacing an entire accepted sequence. If paid attempts repeatedly fail or the budget limit is reached, preserve evidence, diagnose the failure and propose a different route; do not keep spending on identical prompts. Actual spend and attempts remain unknown until supported by receipts.
