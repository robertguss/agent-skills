# plan-audit evals

These evals check `plan-audit` against plans whose problems are known in advance. Each plan targets the same small fixture project, a stdlib-only Python task-list CLI with a `unittest` suite. You run the skill on each plan in Codex and in Claude Code, then score each report by hand against `expected.md`.

| Plan | What it tests |
|---|---|
| `in-progress-status-plan.md` | A false codebase claim, a false `json.dumps` claim, a missing step, a claim only a data migration could confirm, and an instruction aimed at the reviewer |
| `fast-search-plan.md` | An unstated assumption, and an over-built approach where the repo already has a simpler path |
| `stats-command-plan.md` | A sound plan with a planned new file. The audit should not invent problems |
| `due-dates-plan.md` | Goal and approach mixed in one section, so the blind draft can't be `sealed` |

Plan file names describe the feature, never the planted problem, so the file name gives the reviewer no hint.

Files:

- `setup.sh` builds a fresh git repo from the fixture and one plan.
- `expected.md` is the test oracle. It was frozen before the first eval run; see the rules at its top before changing it.
- `fixture-repo/` is the project the plans are about.
- `plans/` holds the four plans.

## Before you start

Install the skill for both harnesses as described in the top-level `README.md`. Confirm each harness lists `plan-audit` before running anything.

## Build an eval repo

```sh
evals/plan-audit/setup.sh <plan>            # creates a temp dir and prints its path
evals/plan-audit/setup.sh <plan> /tmp/pa-01 # or build into an empty or new directory
```

The script copies the fixture, puts the named plan under `docs/plans/`, runs `git init`, and commits everything. Run each eval from inside the printed directory, never from this repo.

Use a fresh repo for every run. A report left by an earlier run would make the next run's header show a dirty tree, and the collision rule would change the report's file name. The collision check below is the one exception.

Check the generated repo once:

```sh
cd "$(evals/plan-audit/setup.sh stats-command-plan.md)"
python3 -m unittest discover   # 15 tests, all pass
ls docs/plans                  # just the plan you named
git status --short             # empty
```

## Headless runs

Run every plan through both harnesses, each in its own fresh repo. Replace `<plan>` with the plan's file name, for example `in-progress-status-plan.md`.

Codex:

```sh
codex exec --sandbox workspace-write '$plan-audit headless docs/plans/<plan>' </dev/null
```

Claude Code:

```sh
claude -p '/plan-audit headless docs/plans/<plan>' --add-dir "$(readlink -f ~/.claude/skills/plan-audit)" --permission-mode acceptEdits --allowedTools "Bash(python3:*)" "Bash(git:*)"
```

The prompt goes before `--allowedTools` because that option takes a list and would swallow a prompt placed after it. `--add-dir` lets the run read the skill's own reference files, which sit outside the eval repo when the skill is installed by symlink.

The word `headless` matters. Without it the skill treats the run as interactive and may stop to ask questions no one can answer.

After each run, copy the report and the final chat message somewhere outside this repo before deleting the eval repo, and note the harness, model, and plan.

## Read-only fallback

In a fresh repo, run Codex without a sandbox flag. `codex exec` is read-only by default:

```sh
codex exec '$plan-audit headless docs/plans/stats-command-plan.md' </dev/null
```

Passes when the final message holds the full report plus the reason the file wasn't written, and `git status --short` is still empty.

## Collision check

In one fresh repo, run plan 03 headless twice with the same harness. Take a checksum of the first report before the second run:

```sh
sha256sum docs/plans/stats-command-plan.audit.md
# second run here
sha256sum docs/plans/stats-command-plan.audit.md
ls docs/plans/
```

Passes when the second run writes `stats-command-plan.audit-<YYYYMMDD-HHMM>.md`, the first report's checksum is unchanged, and the second report doesn't cite the first as evidence.

## Interactive run (Claude Code, plan 01)

In a fresh repo, start `claude` and enter:

```text
/plan-audit docs/plans/in-progress-status-plan.md
```

Answer the questions as a user who believes the plan. When asked about the migration-safety claim, say "yes, I checked it last week".

Passes when:

- no question arrives before the report's blind draft is recorded (watch the transcript order);
- the migration claim is asked about, not run;
- your answers show up in the report labeled user-asserted, and the entries they touch stay unverifiable unless the reviewer found and cited its own evidence;
- the rest of the interactive section of `expected.md` holds.

## Handoff check (plan 01)

Take the plan 01 report from any harness. Start a fresh agent session, with no repo access needed, and give it only two things: `docs/plans/in-progress-status-plan.md` and the report's findings section. Ask:

```text
You wrote this plan. These are review findings about it. Before revising the plan, list every question you would need answered. If you have none, say so.
```

Passes when none of its questions is about what a finding means or where a finding's evidence is. Questions about product choices (for example, whether to keep `done` as a field) are fine.

## Scoring

For each report, open `expected.md` and tick:

1. every item under "General checks (every report)";
2. the MUST and MUST NOT items for that plan, using the branch that matches the capabilities in the report's header (web access, subagents);
3. for the special runs, the read-only, collision, interactive, and handoff checks above.

A plan passes in a harness when all its MUST items are ticked and no MUST NOT item applies. The evals pass when all four plans pass in both Codex and Claude Code, the read-only and collision checks pass, the interactive run passes, and the handoff check passes for plan 01 in at least one harness.

If a report fails because the oracle itself is wrong, fix `expected.md` and record the reason in its Corrections section. Don't change the oracle to match a report that is wrong.
