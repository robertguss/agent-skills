# Audit: <plan title>

- **audit_of:** `<plan path>`
- **date:** <YYYY-MM-DD>
- **auditor:** <harness and model, as far as you know them, or "unknown">
- **mode:** <interactive | headless>
- **capabilities:** subagents <yes/no>, web <yes/no>, file writes <yes/no>, shell <yes/no>
- **draft independence:** <sealed | partial | compromised>: <one line on what the drafter saw>
- **target repo:** `<path>` at `<HEAD short sha>`, <clean | uncommitted changes>
- **notes:** <non-markdown input, assumed target repo, no checkout, or "none">

## Verdict

**<Proceed | Revise | Rethink>** (<N> of <M> ledger entries unverifiable)

<Two to four sentences for a human deciding whether to trust this plan: what holds up, what doesn't, and what to do next.>

### Top issues

1. <PA-n: the most consequential finding, in one line>
2. <...>

## Findings

### PA-1. <consequence-first title>

- **Severity:** <Critical | High | Medium | Low>
- **Category:** <false-claim | missing-work | assumption | approach | risk | consistency>
- **Evidence:** <ledger entries, file:line, URLs, command output; or "Judgment:" plus the reasoning>
- **Suggested fix:** <the specific change to the plan>

<Repeat for each finding. Write "No findings." when there are none.>

## Pre-mortem

<Either the failure stories that became findings, each pointing to its PA-n, or: "No material case against the plan.">

## Open questions

<Each unverifiable entry not settled by the user: the entry ID, the question, and what answer would settle it. Write "None." when empty.>

## Assumptions

<Every assumption the plan depends on: ledger assumption entries, user-asserted answers with the user's stated reason, and the blind draft's own assumptions. Mark each one's source.>

## Run notes

<Side effects of the audit (for example a test run that changed a tracked file), commands not run and why, and anything that limited the audit. Write "None." when empty.>

## Claim ledger

| ID | Section | Kind | Claim | Verdict | Evidence or reason |
|---|---|---|---|---|---|
| L1 | <plan section> | <codebase / external / runtime / consistency / assumption> | <one checkable claim> | <confirmed / refuted / unverifiable> | <file:line, URL, the command run and its output, or the reason none exists; mark user-asserted answers> |

## Blind draft

**Excerpt used:** <the goal, problem, and external constraints the draft started from>

**Approach:** <the draft approach>

**Must-cover:**

- <item>: <covered by plan step X | missing, see PA-n>

**Draft assumptions:**

- <Extracted goal, when the goal came from a mixed section or a linked document: the goal as you stated it. Omit this line when the goal had its own section.>
- <assumption>
