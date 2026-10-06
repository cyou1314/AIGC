# Story Diagnosis

Diagnose from source evidence before suggesting a rewrite.

Diagnosis output must not contain replacement script passages unless the user separately authorizes rewriting or explicitly accepts a repair.

## Priority

Classify each issue:

- `阻塞`: the story cannot be understood, motivated, or continued coherently.
- `高影响`: weakens the central conflict, character choice, climax, or ending.
- `局部`: affects one beat, scene, transition, or dialogue passage.
- `偏好`: a style choice with no clear causal or production harm.

Prioritize blocking and high-impact issues first. Do not silently repair or polish the text while causality is broken.

## Diagnosis Chain

For the story or current sequence, trace:

```text
角色目标
→ 为什么现在行动
→ 阻碍
→ 选择
→ 结果
→ 代价
→ 状态变化
→ 威胁或信息升级
→ 下一段钩子
```

Mark the first broken link. Later symptoms may disappear after that link is repaired.

## Scene Necessity

A scene earns its place when it changes at least one of:

- knowledge
- relationship
- danger
- goal
- leverage
- emotional position
- physical situation

If it only repeats known information, merge, shorten, or remove it unless repetition itself creates pressure.

## Evidence Format

```text
问题:
级别:
原文/情节证据:
为什么会出问题:
最低成本修复:
受影响的后续内容:
需不需要确认:
```

Do not invent missing intent. Write `证据不足` when the source does not establish it. Describe the repair direction without drafting replacement text.

## Common Misdiagnoses

- “节奏慢” may actually be no state change.
- “人物降智” may be missing information, motive, or visible cost.
- “对白尴尬” may be exposition without intention or resistance.
- “转折突然” may be missing setup rather than a bad turn.
- “不够爽” may be weak leverage change, delayed payoff, or unclear consequence.

Name the underlying mechanism and repair that mechanism.
