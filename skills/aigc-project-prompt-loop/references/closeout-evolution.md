# Project Closeout Evolution

Use this reference for an explicitly requested Skill review or separately authorized governance review. During ordinary project closeout, record useful observations as project-local candidates; do not edit or promote global Skills automatically.

## Evidence Order

Judge evidence in this order:

1. Explicit user acceptance, rejection, or correction tied to a concrete output.
2. Actual generation outcome: completeness, visual quality, continuity, action readability, stability, and efficiency.
3. Repeated behavior across multiple revisions or projects.
4. Final prompt structure and wording.
5. External trends, popular prompt claims, or model folklore that were not tested in this project.

The final prompt is important evidence, but it is not proof that every phrase or rule inside it caused the success.

## Whole-Project Audit

Review the project as a sequence:

1. Record the initial material, assumptions, model target, and intended result.
2. Identify where analysis, storyboard mapping, character/scene references, or prompt structure first went wrong or right.
3. Trace each meaningful user correction to the prompt change it caused.
4. Separate corrections that fixed this one shot from corrections that expose a reusable rule.
5. Include actual generation feedback when available. If no generated result was reviewed, lower confidence and avoid universal claims.
6. Compare production cost: extra fields, repeated explanations, manual fixes, reruns, and time spent. A rule that adds work without improving output is a deletion candidate.
7. Inspect current skill rules that touched the project, including rules that were not used because they were irrelevant, confusing, or too rigid.

## Rule Actions

Assign exactly one action to each relevant rule:

| Action | Use when | Result |
| --- | --- | --- |
| 保留 | The rule remains correct, clear, and useful | Keep unchanged |
| 强化 | Repeated evidence shows it should guide future work more strongly | Promote scope or priority |
| 改写 | The intent is useful but wording, scope, sequence, or model assumption is wrong | Replace the old wording |
| 合并 | Two or more rules overlap or conflict | Keep one clearer rule and remove duplicates |
| 降级观察 | Evidence is promising but weak, single-project, or uncertain | Do not make it a default yet |
| 删除 | The rule has no meaningful remaining use and every less-destructive action is unsuitable | Remove it as a last resort |

Do not create a seventh action called “add anyway.” A new rule must justify its scope and should displace ambiguity, replace a bad default, or fill a proven gap.

删除不是每次收尾的必选动作，也没有删除配额。一次审计可以没有任何删除项。默认先判断能否保留、缩小适用范围、改写、合并或降级观察；只有确认规则已经没有剩余适用价值，继续保留反而会误导未来项目时，才使用删除这一最后手段。

## Delete And Replace Tests

Consider deletion only after checking whether the rule can be narrowed, rewritten, merged, or observed. Delete it when the evidence is strong and one or more are true:

- The user repeatedly corrected behavior caused by the rule.
- Actual generations became worse, incomplete, unstable, generic, or harder to control because of it.
- The rule conflicts with a newer accepted rule or current model behavior.
- It is duplicated elsewhere with clearer wording.
- It is too project-specific but was stored as a broad default.
- It forces fields, steps, explanations, or prompt density that do not improve output.
- It encodes a trend or online claim that was never validated and is now treated as fact.

These signals do not force deletion by themselves. If the rule still has a valid niche, narrow its scope or rewrite it. Prefer replacement over keeping both old and new rules, and preserve a short failure reason only when it prevents the same mistake from being reintroduced.

## Scope And Recency

- Do not let one recent project automatically erase a rule validated across many projects; narrow or observe first when evidence conflicts.
- Let explicit user rejection override generic best practice for this user's workflow.
- Scope model-sensitive rules to the model and version observed. Recheck them when the model changes.
- Promote a project-local rule only when the underlying cause can recur beyond the current characters, scene, or shot.
- Review older rules for staleness whenever a new rule changes the same behavior.

## Conflict Resolution

When rules conflict, prefer:

1. Explicit current user intent.
2. Verified generation results.
3. Repeated project evidence.
4. The narrower rule for a matching context.
5. The simpler rule when output quality is equal.

Remove the losing duplicate or mark it with a narrower scope. Do not leave unresolved contradictions for the next project.

## Internal Closeout Record

Keep the closeout compact and internal unless the user asks to see it:

```text
项目结果: accepted / partially verified / unverified generation
关键过程证据: ...
保留: ...
强化: ...
改写: old -> new, because ...
合并: A + B -> C
降级观察: ...
删除: none / ..., only when no less-destructive action is suitable
适用范围: project / similar projects / broad default / model-specific
下次启动变化: ...
```

Never re-output the final prompt during closeout unless the user explicitly asks for it.
