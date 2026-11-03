# agent-skills

Portable agent skills in the open [Agent Skills](https://agentskills.io/specification) format. Each skill is a folder under `skills/` that runs unchanged in Claude Code, Codex, Cursor, Gemini CLI, and Antigravity CLI.

## Skills

| Skill | What it does |
|---|---|
| [`plan-audit`](skills/plan-audit/SKILL.md) | Audits an implementation plan or spec written by an AI agent. It runs in a fresh session, ideally on a different model from the one that wrote the plan. It drafts its own approach blind, verifies every claim against the repo, docs, and read-only commands, argues the case against the plan, and writes a separate audit report. The plan itself stays untouched. |

## Install

Link the skill folder into each harness's user-level skills directory. Run this from the repo root:

```bash
mkdir -p ~/.agents/skills ~/.claude/skills ~/.gemini/skills
ln -sn "$PWD/skills/plan-audit" ~/.agents/skills/plan-audit   # Codex, Cursor
ln -sn "$PWD/skills/plan-audit" ~/.claude/skills/plan-audit   # Claude Code
ln -sn "$PWD/skills/plan-audit" ~/.gemini/skills/plan-audit   # Gemini CLI, Antigravity CLI
```

`ln -sn` refuses to replace an existing path and stops with "File exists". When that happens, check where the existing link points with `readlink -f ~/.claude/skills/plan-audit` (or the matching path). If it isn't this checkout, remove the old link and run the command again.

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
# --add-dir lets the run read the skill's reference files through the symlink.
# Add your project's test command to --allowedTools so the audit can run the suite.
claude -p '/plan-audit headless docs/plans/my-plan.md' --add-dir "$(readlink -f ~/.claude/skills/plan-audit)" \
  --permission-mode acceptEdits --allowedTools "Bash(git:*)" "Bash(python3:*)"
```

Without write access the audit returns the full report in its final message and says why the file wasn't written.

## Evals

`evals/plan-audit/` holds a small fixture repo, four test plans with planted problems, and the expected outcomes for each. See [`evals/plan-audit/README.md`](evals/plan-audit/README.md).
