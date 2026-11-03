# Compare, pre-mortem, verdict

You now have your blind draft and a verified ledger. Turn them into findings, then compute the verdict.

## Compare with the blind draft

- **Must-cover items.** Match each item on your must-cover list to the plan step that delivers it. An unmatched item becomes a `missing-work` finding when the goal fails or real rework follows without it. An unmatched item that is a nicety, such as an extra test case for behavior the plan already gets right, stays out of the report.
- **Approach.** Your draft is one workable option among several, so a difference from it is not a defect. Where the drafts differ, look for evidence that the plan's approach must be replaced: an existing code path the plan rebuilds, a refuted premise the approach rests on, or a measured result that contradicts it. That evidence makes an `approach` finding. The approach is the plan's core design for reaching the goal. How that design rolls out, migrates existing data, or stays compatible are steps. So a fix that keeps the core design and changes those steps is a `missing-work` or `risk` finding, however serious. Without evidence the difference is taste, and it stays out of the report. Existing code that already does part of what the plan builds always goes in a finding, cited by `file:line`, whatever its category, because the planning agent needs to know it exists.

## Pre-mortem

Imagine it is three months later and the plan failed. Write the strongest account of why. Goal, scope, and approach are all in play: maybe it solved the wrong problem, or solved the right one in a way that breaks something nobody checked.

Each failure story becomes a finding only when it names a concrete scenario, with trigger, mechanism, and consequence, that the plan doesn't address. When no story clears that bar, record "No material case against the plan" in the report. That result is as valuable as a finding.

## Write findings

Every finding has:

- **ID:** `PA-1`, `PA-2`, and so on, in report order.
- **Severity:**

  | Severity | Meaning |
  |---|---|
  | Critical | Following the plan fails its goal or causes damage: data loss, a security hole, an outage |
  | High | An implementer will hit it: a false premise, a step that can't work, missing work the goal needs. Also evidence that the plan's approach should be replaced by a materially simpler or sturdier one |
  | Medium | Likely rework or a wrong turn, but the goal is still reachable |
  | Low | Worth fixing, cheap to ignore |

  When a finding's failure only happens if an unverifiable entry holds, such as a deployment pattern nobody confirmed, rate it one level lower and name that entry in the evidence.

- **Category:** `false-claim`, `missing-work`, `assumption`, `approach`, `risk`, or `consistency`.
- **Evidence:** the ledger entries, `file:line` references, URLs, or command output it rests on. A finding resting on your judgment says so, with the reasoning.
- **Suggested fix:** what the plan should change, specific enough that the planning agent can apply it without asking what you meant.

## Verdict

The first matching row wins.

| Condition | Verdict |
|---|---|
| A Critical or High `approach` finding: the plan's approach can't reach the goal, or evidence shows it should be replaced. Fixes that keep the approach and change steps don't count here. | **Rethink** |
| Any other Critical or High finding, or a refuted entry that changes what an implementer must build | **Revise** |
| Otherwise | **Proceed** |

The verdict line also states how many ledger entries are unverifiable out of the total, for example "Proceed (7 of 31 entries unverifiable)". A Proceed resting on thin evidence should look thin.

This phase is done when every must-cover item is matched or recorded as a finding, the pre-mortem has produced findings or "no material case against the plan", every finding has all five fields, and the verdict follows the table.
