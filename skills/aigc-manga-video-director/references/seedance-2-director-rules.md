# Seedance 2 Director Rules

Use this reference when the task needs Seedance 2.0 / Seedance 2.0 Fast prompt writing, prompt revision, multimodal reference planning, multi-shot timeline prompts, video edit/extend prompts, dialogue/audio prompts, or troubleshooting a failed generation.

This file is a general production rule set. Do not bind it to any single project, character world, or current title. Project-specific standards belong in a project profile; this reference only keeps reusable Seedance directing logic.

## Table of Contents

1. Operating Loop
2. Surface And Format Policy
3. Reference Role Map
4. Mode Selection
5. Director Intention Rule
6. Timeline And Shot Structure
7. Character And Blocking Control
8. Preflight And Bilingual Prompting
9. Audio, Dialogue, Rhythm
10. Edit, Extend, And Reference Recreation
11. Prompt Compression And Anti-Slop
12. Output Templates
13. Retake And Troubleshooting Loop

## Operating Loop

Before writing a final prompt, do this in order:

1. Identify the goal: standalone clip, sequence project, prompt revision, video recreation, edit, extension, storyboard-to-video, or troubleshooting.
2. Identify the active surface if known: Jimeng/Dreamina, Higgsfield, API/provider route, or unknown Seedance-compatible surface. If the user asks about current platform limits, model IDs, pricing, or API behavior, verify live docs before claiming facts.
3. Choose mode: T2V, I2V, V2V, R2V, FLF2V, edit, extend, or sequence.
4. Build a reference role map before drafting. Every uploaded image/video/audio gets one primary job and optional secondary jobs.
5. Name one directorial intention for the clip or shot: reveal, threat, decision, attraction, pursuit, transformation, intimacy, shock, proof, comedy beat, product desire, etc.
6. Build the prompt around one visible beat, one primary camera move, one lighting logic, one performance/action focus, and one sound/rhythm intent.
7. Run the preflight simulation from `seedance-preflight-and-bilingual.md`: mode, reference roles, first frame, action physics, camera path, continuity, artifact risks, endpoint, and likely retake cause.
8. Run the compactness pass: delete filler before deleting control points.
9. If revising after a bad generation, diagnose the cause before adding more adjectives.

When the user's desired effect is `帅`, `酷`, `霸气`, `气场`, `男主感`, `神性`, `疯批感`, or `反派感`, load `charisma-action-language.md` before drafting. Treat those words as output effects, not prompt instructions. Convert them into silhouette, posture, anticipation, action economy, camera power relation, rhythm, environmental response, sound, and endpoint.

When the user asks for cool/hype/fight/anime-action/stylish video reference patterns, load `cool-video-reference-patterns.md` before drafting. Pick one pattern such as wide choreography spectacle, close impact compression, environmental action, anime burst, camera rotation, entrance reveal, one-take coolness, or music-driven hype cutting, then build the Seedance prompt around one playable beat and a strong endpoint.

Load `seedance-preflight-and-bilingual.md` before final prompt delivery. If the prompt has serious runability risk, revise it before showing the user. Add a short suggestion only when the user should provide a first frame, last frame, character reference, scene reference, or split the shot.

## Surface And Format Policy

Use conservative Seedance assumptions unless the user or current platform docs say otherwise:

- Seedance-style generations are usually short clips. Keep one clip physically playable.
- If exact platform fields matter, verify current limits before stating them as facts.
- If the user is using Higgsfield-style multi-shot prompting, put a top production line before the prompt: `Total: [duration] / [shot count] / [aspect ratio]`.
- In this user's existing copyable shot-block workflow, do not add separate model or aspect-ratio fields unless the user asks. Keep source `时间` as source-video timing, not a model parameter.
- For long or complex ideas, split into multiple shots or multiple clips instead of overloading one 4-6 second generation.
- If using a reference video, specify which parts transfer: camera, action, rhythm, expression, edit cadence, sound, or transition. Also specify what must not transfer when needed.
- Avoid presenting community tricks as official behavior. Treat them as useful prompt heuristics.

## Reference Role Map

Never leave references ambiguous. Do not write only `参考 @视频1`; state the role.

| Reference role | Use when | Prompt wording pattern |
|---|---|---|
| Identity | A character/product must stay stable | `@角色A controls face, hair silhouette, outfit, and key prop` |
| First frame | I2V or start-frame lock | `@图1 as first frame; preserve composition and subject identity` |
| Last frame | FLF2V or endpoint lock | `@图2 as final frame; motion bridges from @图1 to @图2` |
| Scene | Location geography matters | `scene geography and lighting direction from @场景A` |
| Camera | Recreate movement | `camera path and shot rhythm from @视频1 only` |
| Action | Recreate choreography | `action timing and body mechanics from @视频1` |
| Rhythm | Match beat/cut timing | `visual rhythm follows @音频1 / @视频1 beat accents` |
| Audio | Voice, BGM, SFX, or ambience | `SFX/BGM/voice tone references @音频1` |
| Style | Visual finish only | `style reference from @图3; do not copy identity or scene` |
| Outfit/prop | Clothing/product detail | `wardrobe/product detail from @图2` |

Rules:

- Use bare `@` names only: `@角色A`, `@图1`, `@视频1`. Do not include file extensions, paths, positions, or role words inside the mention.
- Put the role in the field text, not inside the `@` mention.
- Assign each asset one primary role. If one asset must do several jobs, explicitly rank them.
- State non-transfer constraints when using V2V/R2V: `do not transfer face, costume, background, or brand elements from @视频1`.
- Prioritize the references that affect the shot most. Do not attach every asset to every shot.

## Mode Selection

Choose the mode before drafting:

| Mode | Best for | Drafting priority | Common failure | Fix |
|---|---|---|---|---|
| T2V | No visual reference | Build subject, scene, action, camera, light, sound, constraints | Too many events | One visible beat and clear endpoint |
| I2V | Start image exists | Preserve visible identity/composition, add motion and camera | Re-describing image causes drift | Say what changes, not everything already visible |
| V2V | Source clip exists | Transfer camera/action/rhythm/edit target only | Accidental identity/scene transfer | State transfer role and non-transfer items |
| R2V | Multiple references | Map each reference to a role | Reference conflict | Rank roles or split shots |
| FLF2V | First and last frames | Describe the continuous bridge | Endpoint too vague | State final visual target clearly |
| Edit | Modify existing video | Preserve source, change one layer | Rewriting the whole scene | `@视频1 is source; change only...` |
| Extend | Continue a clip | Start from accepted end state | Replay or reset | Record actual final frame, then continue |
| Sequence | Connected story | Maintain state across clips | Future beats leak early | Current clip only, update state after accepted take |

## Director Intention Rule

Before writing prompt prose, name the one thing the shot is doing. The camera, light, blocking, performance, and sound should all serve that intention.

Good internal intention examples:

- `威压`: low angle, vertical geometry, protagonist small in foreground, heavy room tone.
- `发现真相`: slow reveal, eyeline-led pan, sound drops, light isolates clue.
- `失控`: handheld instability, faster breathing, broken composition, harsh SFX.
- `亲密`: locked close frame, shallow depth, quiet micro-gestures, soft practical light.
- `产品欲望`: macro texture, controlled turntable motion, highlight sweep, clean sound cue.

Do not stack unrelated directorial choices just because they sound cinematic.

## Timeline And Shot Structure

Use timeline prompting when duration exceeds about 8-10 seconds, when there are multiple beats, or when the user wants a multi-shot result.

For one clip:

- Open with the production shape when useful: `Total: 15s / 5 shots / 9:16`.
- Number shots or time blocks.
- Each block needs: subject/action, camera, lighting/environment, sound or rhythm, endpoint.
- Use escalation arcs: calm -> disturbance -> action -> consequence; or setup -> reveal -> reaction -> decision.
- Avoid forcing six story beats into one short shot. If the beat count is high, split into shots or clips.

Multi-shot pattern:

```text
Total: [duration] / [shot count] / [aspect ratio if needed]
Global: [identity, scene, style, continuity, avoid]
Shot 1 ([time]): [start composition], [action], [camera], [sound], [endpoint].
Shot 2 ([time]): ...
```

Single-shot / one-take pattern:

- State `one continuous shot`, `no cuts`, and the viewpoint lock.
- State what the camera must not do: no cuts, no zoom, no angle switch, no sudden teleporting.
- Use one continuous camera logic: follow, POV, orbit, push, pull, handheld, locked-off, or crane-like move.
- If it is POV, keep hands/body cues visible and avoid impossible external views.

## Character And Blocking Control

For recurring characters, create a compact character contract before shot prompts:

- Tag: `角色A`, `角色B`, `@角色A subject`, or the user's original name.
- Identity lock: face shape, hair silhouette, outfit, key prop, body type.
- Position: foreground/background, left/right, seated/standing, eyeline.
- Action: one verb and endpoint per character.
- Expression: observable behavior, not only emotion labels.
- Constraint: what must not change.

Multi-character rules:

- Do not write `他们激烈争吵` when Seedance must decide who moves. Assign actions separately.
- If contact happens, describe contact point and endpoint: `角色A grabs 角色B's wrist, stops the hand at chest height`.
- For crowd scenes, identify the hero subject and keep background motion simple.
- In multi-person shots, default non-focus characters to micro-motion: breathing, blink, gaze drift, small shoulder movement.
- Avoid rapid finger choreography, face-touching during dialogue, and complex hand-object transfers unless that is the single shot beat.
- Lock camera more when face identity, lip-sync, or portrait preservation matters.

## Preflight And Bilingual Prompting

Before delivering final Seedance prompts, mentally simulate whether the clip can run completely and cleanly. Check:

- mode and reference roles
- start frame clarity
- action physics and duration fit
- one primary camera logic
- continuity from previous shot
- risk areas: hands, face, weapon near face, multiple people, fabric, smoke, text, extreme rotation
- exact endpoint or continuing-motion tail frame
- most likely retake cause and repair

If two or more checks fail, rewrite the prompt before delivery.

For this user's workflow, Chinese-English mixed prompting is allowed as a targeted control method:

- Chinese: story intent, character emotion, relationship, dialogue, performance, scene geography, continuity, user-facing notes.
- English: compact, common film/camera/style tags such as `slow dolly in`, `locked-off camera`, `low-angle medium shot`, `over-shoulder`, `shallow depth of field`, `soft rim light`, `one continuous shot`, `no cuts`.
- Do not mix languages every phrase. Keep the final prompt readable and copyable.
- Do not use English stacks of generic adjectives. Use English only when it clarifies a camera, lens/depth, lighting, or continuity instruction.
- Keep spoken dialogue and on-screen text in the language the output should use.

## Audio, Dialogue, Rhythm

Seedance prompts should include sound when it affects performance, timing, or emotion.

Use audio fields for:

- dialogue line, speaker, delivery style, and emotional register
- breath, footsteps, cloth rub, weapon impact, door sound, phone vibration
- environmental bed: wind, rain, crowd, room tone, machinery
- music intensity and beat accents
- sound drop, muffled sound, reverb, or impact hit

Dialogue rules:

- Assign speaker names or character tags.
- Keep dialogue short enough for the clip duration.
- Tell the performance as visible action plus vocal delivery: `角色A forces a smile while voice trembles`.
- For music beat-matching, map visuals to beat positions instead of only saying `卡点`.

## Edit, Extend, And Reference Recreation

Video edit:

- Start with preservation: `@视频1 is the source clip; preserve composition, timing, camera, and background`.
- Then state one controlled change: character replacement, prop change, emotion change, style change, added element, or ending twist.
- Do not rewrite unrelated parts.

Video extend:

- Record the source's actual final frame before drafting.
- The generation duration should match the added segment when the platform asks for duration.
- Continue motion, lighting, screen direction, and sound from the source.
- Do not replay completed action.

Reference recreation:

- Use source timecode when available.
- Separate observed evidence from inferred intent.
- Translate camera evidence into prompt controls: start frame, endpoint, path, speed/easing, parallax, foreground occlusion, depth/focal shift.

## Prompt Compression And Anti-Slop

Keep prompts compact but not shallow. Cut in this order:

1. Duplicate style adjectives.
2. Generic quality words: `cinematic`, `high quality`, `beautiful`, when they do not control anything.
3. Background details already visible in references.
4. Secondary camera moves.
5. Secondary actions.
6. Speculative emotion labels not visible on screen.

Keep:

- reference role map
- start and end frame
- primary subject/action
- primary camera move and endpoint
- timing or shot order
- lighting direction if it changes emotion or continuity
- sound/rhythm intent
- character/scene preservation constraints
- avoid list for known risks

Anti-slop rewrite:

- Replace `cinematic and dramatic` with the exact composition, light, action, and camera reason.
- Replace `very emotional` with visible behavior: blink held too long, jaw tightens, grip loosens, half-step back.
- Replace `dynamic camera` with the path, speed, and endpoint.
- Replace `epic battle` with who attacks, from where, what the camera tracks, and what impact ends the beat.
- Replace `handsome/cool/badass/霸气/男主感` with visible charisma controls from `charisma-action-language.md`: readable silhouette, relaxed or dominant posture, pre-action pause, one precise action, camera power relation, delayed cloth/hair/dust response, sound cue, and a held endpoint.

## Output Templates

### Compact Seedance Shot Block

Use for this user's copyable per-shot workflow:

```text
时间: [source timecode if recreating reference]
参考: [@角色A / @场景A / @视频1 role map, only when useful]
首帧: [subject, pose, composition, environment, lighting]
运动: [subject action + camera movement + foreground/background motion]
镜头: [shot size, angle, lens/depth feel, path, speed/easing]
尾帧: [ending composition and emotion]
声音: [dialogue/SFX/BGM/rhythm if relevant]
稳定性: [identity, wardrobe, props, location, screen direction, lighting direction]
避免: [known risks]
```

### Timeline Prompt

Use for multi-shot Seedance generation, ads, short drama beats, transformations, montage, music cuts, or 10-15 second structures:

```text
Total: [duration] / [shot count] / [aspect ratio if the target surface needs it]
Global references: [role map and continuity locks]
Shot 1 ([time]): [composition + action + camera + sound + endpoint].
Shot 2 ([time]): ...
Continuity: [identity, wardrobe, screen direction, props, lighting]
Avoid: [conflicts, overload, drift, artifacts]
```

### First/Last Frame Bridge

```text
@图1 as first frame, @图2 as final frame.
Preserve [identity/scene/style] from @图1.
Over [duration], [subject] moves from [start state] to [end state].
Camera [single path] while [foreground/background] creates [parallax or transition].
End exactly on @图2 composition; no extra cut, no unrelated scene.
```

## Retake And Troubleshooting Loop

When the user gives a bad generation or correction, classify the failure before rewriting:

| Failure | Likely cause | Repair |
|---|---|---|
| Identity drift | Weak character anchor, too much re-description | Strengthen tag/identity lock, remove competing identity cues |
| Camera ignored | Too many moves, no endpoint | One camera move, start/end framing, path, speed |
| Random cut appears | One-take not locked | Add `one continuous shot`, `no cuts`, `no angle switch` |
| Action overload | Too many beats for duration | Split into shots or remove secondary action |
| Hand/face artifacts | Complex hands/face under motion | Simplify hand action, lock camera, move prop interaction off-screen |
| Reference conflict | One asset asked to do too much | Assign primary roles or split references |
| Weak emotion | Emotion described abstractly | Add visible gesture, rhythm, sound, and blocking |
| Poor continuation | Actual end state missing | Review accepted final frame, then write from that state |

Change one major variable per retake when possible. Do not add adjectives blindly.
