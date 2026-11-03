---
title: Task count summary command
type: feat
date: 2026-11-01
status: ready
---

# Task count summary command

## Goal

A user can run `tasks stats` and see how many tasks they have in total, how many are open, and how many are done.

## Problem

The only way to answer "how much is left?" today is to run `tasks list --open` and count the lines by hand, or pipe the output through `wc -l`. People who review their list weekly want the numbers directly.

## Constraints

- Standard library only, Python 3.9 or later, same as the rest of the project.
- Read-only: `tasks stats` never writes the task file.
- No change to the task file's format.
- Non-goal: charts, per-day history, or breakdowns by date.

## Context

- `tasks/store.py` defines the `Task` dataclass, whose `done` field is a boolean, and the `Store` class. `Store.load()` returns a list of `Task` and returns an empty list when the file doesn't exist. It doesn't write anything.
- `tasks/cli.py` builds the parser in `build_parser()`. Each subcommand is registered with `sub.add_parser(...)` and `set_defaults(func=cmd_<name>)`, and each handler has the signature `cmd_<name>(args, store)` and returns an exit code. `main(argv)` creates the `Store` from `--file` or `default_path()` and calls the handler.
- `tests/test_cli.py` runs the CLI in-process through a `run_cli(*argv)` helper that passes `--file` pointing into a `tempfile.TemporaryDirectory` and captures stdout with `redirect_stdout`.
- The README has a Usage block listing every command.

## Approach

Put the counting in a small pure function in a new module, `tasks/stats.py`, and keep the CLI handler to formatting and printing. The function takes the list from `Store.load()`, so it can be tested without touching the file system, and the handler stays as thin as the existing ones.

Output is three aligned lines:

```text
total: 3
open:  2
done:  1
```

An empty or missing store prints the same three lines with zeros and exits 0.

## Steps

1. **New module.** Create `tasks/stats.py` with `summarize(tasks)`. It returns a dict with the keys `total`, `open`, and `done`, where `open` counts tasks with `done` false and `done` counts tasks with `done` true.
2. **CLI.** In `tasks/cli.py`, import `summarize`, add `cmd_stats(args, store)` that prints the three lines from `summarize(store.load())` and returns 0, and register a `stats` subparser in `build_parser()` with `set_defaults(func=cmd_stats)`. The subcommand takes no arguments.
3. **Docs.** Add `python3 -m tasks.cli stats` to the README Usage block.

## Test plan

- New `tests/test_stats.py`: `summarize([])` returns all zeros; a mix of open and done `Task` objects gives the right counts.
- `tests/test_cli.py`: add a test that adds two tasks, marks one done, runs `stats` through `run_cli`, and checks the three lines. Add one that runs `stats` on a missing file and checks the zeros and exit code 0, and that the file still doesn't exist afterwards.
- Run `python3 -m unittest discover` and confirm the existing tests still pass.
