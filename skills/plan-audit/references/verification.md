# Ledger and verification

Now read the whole plan. Turn it into a ledger of checkable entries, then give every entry a verdict backed by evidence.

## Build the ledger

Split the plan's statements until each entry makes exactly one checkable claim. Number them `L1`, `L2`, and so on, grouped by the plan section they came from. Each entry has a **kind**:

| Kind | What it claims | Example |
|---|---|---|
| `codebase` | Something about the repo as it is now | "`Store.load()` returns `[]` when the file is missing" |
| `external` | Library, API, framework, or tool behavior | "`requests` retries on 503 by default" |
| `runtime` | How the system behaves when run | "the test suite passes on the current branch" |
| `consistency` | The plan agreeing with itself | "step 4 delivers the export the goal promises" |
| `assumption` | Something that must be true for the plan to work, stated or not | "only one process writes the data file" |

**Record premises, not intentions.** A planned change becomes the premises it depends on. "Add a retry wrapper around the HTTP client" yields "the HTTP client is a single shared module" and "callers don't already retry". A file the plan will create is not an entry. The facts that make creating it sensible are.

**Hunt for unstated assumptions.** For each step, ask what has to be true for it to work: about data size, concurrency, who else writes a file, ordering, permissions, the environment, users' existing data. Each answer the plan never states becomes an `assumption` entry. These are the entries the planning session was least likely to examine.

**Entries record what the plan says or relies on.** Work the plan never mentions is a gap, not a claim, and the comparison with your blind draft turns it into a finding later. Background facts the plan never builds on can share a single entry. Spend your verification on the claims the plan's steps depend on.

The ledger is complete when every claim the plan makes or relies on, and every assumption you found, has an entry.

## Verify each entry

Each entry ends with exactly one verdict: **confirmed**, **refuted**, or **unverifiable**. Each verdict cites its evidence, or for unverifiable, the reason there is none.

Judge a claim as the plan means it, reading its terms the way the repo defines them. Refute it only when the evidence shows that meaning is false. An edge case the claim doesn't cover, such as a hand-edited file with a wrong type, is an `assumption` entry or a finding, and the original claim keeps its verdict.

- **`codebase`**: read or search the repo and cite `file:line`. A claim that something is absent needs the search that came up empty, shown in the evidence.
- **`external`**: first establish the version the plan targets, from the lockfile, the manifest, or the plan itself. Then check the claim against evidence for that version: official documentation, other web sources, or the installed dependency's source, type definitions, and lockfile in the checkout. If you can safely exercise the claim with a one-line command, it is also a runtime check, and the command with its output is evidence. When none of these is available, or the target version can't be established, the entry is unverifiable and the reason names what was missing.
- **`runtime`**: run it under the command policy below and cite the command and its output. A long script goes in the report's run notes, and the entry points to it. A claim about code that doesn't exist yet stays unverifiable: simulating that code gives you a lead, and the real code is the evidence.
- **`consistency`**: cite the plan sections or lines involved. Check that every stated goal has work behind it and that no two sections contradict each other. When the plan has implementation steps, check that every requirement maps to at least one step. A spec without steps is checked for goals and contradictions only.
- **`assumption`**: look for evidence on either side, such as a README that says the file is hand-edited, or a lock that already serializes writers. Cite what you found. Most assumptions end unverifiable with that evidence attached. That is the point: they are now labeled.

### Command policy

These run without asking:

- version queries and `--help`
- read-only git commands such as `status`, `log -p` on code paths, `show`, `diff`, and `ls-files`
- type checks with output emission disabled
- a test suite whose configuration shows no database, network, container, or snapshot writes

Put any scratch files you create, such as benchmark data, in the system temp directory, and delete them when you're done.

Before and after any test run, compare `git status`, and record the result in that run's ledger entry ("`git status` unchanged before and after", or what changed). If a run changed a tracked file, leave the file as it is, record the change in the report's run notes as a side effect of the audit, and run no further test commands. It is not a finding against the plan.

Anything that would install, migrate, write outside ignored paths, reach external systems, or that you can't classify from its configuration is asked about first in an interactive run. In a headless run it isn't run, and the entry is unverifiable with the reason.

## Ask the user

In an interactive run, ask whenever an entry can't be verified from the plan, the repo, or external sources. There is no limit on how many questions you ask. Each question names the entry and what would settle it.

What an answer can do:

- An answer is **user-stated evidence**. On its own, the entry stays unverifiable, labeled **user-asserted**, and goes on the assumptions list with the user's stated reason.
- An answer that points at evidence ("it's handled in `services/sync.py`") sends you to check that evidence. Cite what you find, and set the verdict from it.
- An answer that conflicts with evidence you found becomes a finding.
- If the user tells you to stop asking, handle the rest of the run's questions as open questions, the headless way.

In a headless run, every such entry goes on the report's open-questions list.

## Parallel verification

With subagents, you own the ledger and the subagents verify slices of it:

1. Split the ledger by kind or by plan section. Give each subagent its entries, the plan path, the target repo path, the "Rules for every phase" section of `SKILL.md`, and the rules in this file from "Verify each entry" through "Command policy".
2. Each subagent returns a verdict and evidence for each entry, plus a list of the entries it couldn't verify. Subagents ask the user nothing.
3. Merge duplicate questions across subagents. In an interactive run, ask as each subagent's results arrive.
4. When an answer affects entries a subagent already returned, check those entries again yourself. Ask about each entry at most once, unless new evidence comes up.

Verification is done when every entry has a verdict with evidence or a stated reason, and every unverifiable entry has been asked about or listed as an open question.
