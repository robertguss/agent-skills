# agent-skills

Portable agent skills in the open [Agent Skills](https://agentskills.io/specification) format. Each skill is a folder under `skills/` that runs unchanged in Claude Code, Codex, Cursor, Gemini CLI, and Antigravity CLI.

## Skills

| Skill | What it does |
|---|---|
| [`plan-audit`](skills/plan-audit/SKILL.md) | Audits an implementation plan or spec written by an AI agent. It runs in a fresh session, ideally on a different model from the one that wrote the plan. It drafts its own approach blind, verifies every claim against the repo, docs, and read-only commands, argues the case against the plan, and writes a separate audit report. The plan itself stays untouched. |
| [`research-panel`](skills/research-panel/SKILL.md) | Checks the claims and assumptions behind an idea against the live web, so nothing rests on a model's training data. Three delegates on three model providers each take a role, search with Exa and TinyFish, and return a verdict per claim with a quote from a page fetched in that run. |

## Install

Install with the [`skills` CLI](https://www.skills.sh/docs/cli). It detects the agents on your machine and links the skill into each one's skills directory.

```bash
npx skills add robertguss/agent-skills --skill plan-audit --global
```

Replace `plan-audit` with any skill name from the table.

Useful flags:

- `--global` (`-g`) installs at user level, so the skill works in every repo. Leave it off to install into the current project only.
- `--agent` (`-a`) picks the agents to install to, for example `-a claude-code codex cursor gemini-cli antigravity-cli`. Leave it off to choose interactively.
- `--list` (`-l`) shows the skills in this repo without installing anything.

Keep it current with `npx skills update`, and remove it with `npx skills remove plan-audit --global`.

## Use `plan-audit`

Start a fresh session in the repository the plan targets, then invoke the skill with the plan's path:

| Harness | Invocation |
|---|---|
| Claude Code | `/plan-audit docs/plans/my-plan.md` |
| Codex | `$plan-audit docs/plans/my-plan.md` |
| Cursor, Antigravity CLI | `/plan-audit docs/plans/my-plan.md` |

The audit asks you about anything it can't verify. The report is written next to the plan as `my-plan.audit.md`.

### Headless runs

Add the word `headless` when no one will be there to answer questions. The audit then records every question in the report instead of asking it, and always finishes with a report.

```bash
# Codex: exec runs read-only unless given a writable sandbox. Close stdin.
codex exec --sandbox workspace-write '$plan-audit headless docs/plans/my-plan.md' </dev/null

# Claude Code: allow file edits plus the commands the audit runs for evidence.
# The prompt goes first: --allowedTools takes a list and would swallow it.
# --add-dir lets the run read the skill's reference files where the CLI installed them.
# Add your project's test command to --allowedTools so the audit can run the suite.
claude -p '/plan-audit headless docs/plans/my-plan.md' --add-dir "$(readlink -f ~/.claude/skills/plan-audit)" \
  --permission-mode acceptEdits --allowedTools "Bash(git:*)" "Bash(python3:*)"
```

Without write access the audit returns the full report in its final message and says why the file wasn't written.

## Use `research-panel`

Say "research panel" in a session where you have been working on an idea, or name a document to check. The skill numbers every claim and assumption the idea rests on, sends the list to three delegates, and replies with one verdict per claim: `confirmed`, `refuted`, `outdated`, `unverified`, or `contested`. It then restates the idea with the refuted and outdated claims corrected.

Each delegate checks every claim through one role:

| Role | Looks for |
|---|---|
| Primary | The source of record: official docs, changelogs, pricing pages, specs, papers, repos. |
| Skeptic | The refutation: deprecations, failures, contradicting data, credible criticism. |
| Recency | What changed in the last 12 months: releases, shutdowns, superseding versions. |

It needs:

- A harness that can start subagents on three model providers. The skill names the T3 Code tools and falls back to the harness's own subagent tools. With fewer than three providers it reports that instead of seating one model three times.
- `EXA_API_KEY` in the environment, for [Exa](https://exa.ai).
- The [`tinyfish`](https://docs.tinyfish.ai) CLI, signed in.

## Evals

`evals/plan-audit/` holds a small fixture repo, four test plans with planted problems, and the expected outcomes for each. See [`evals/plan-audit/README.md`](evals/plan-audit/README.md).
