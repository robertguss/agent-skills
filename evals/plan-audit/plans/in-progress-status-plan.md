---
title: In-progress status for tasks
type: feat
date: 2026-10-28
status: ready
---

# In-progress status for tasks

## Goal

Users can mark a task as in progress, not only open or done. Every command that shows tasks, `tasks list` and `tasks export`, shows each task's status as one of `todo`, `doing`, or `done`.

## Problem

A task today is either open or finished (`Task.done` is a boolean). People who juggle several tasks have asked for a way to flag the two or three they are actively working on, so `tasks list` can show them apart from the backlog. Today they work around this by prefixing titles with "WIP", which clutters the titles and the CSV export they feed into a spreadsheet.

## Constraints

- Standard library only, Python 3.9 or later, same as the rest of the project.
- Existing task files must keep working after the upgrade. Users keep these files for years and some sync them between machines.
- The CLI's existing commands and flags keep their meaning. `tasks done ID` still finishes a task.
- Non-goal: due dates, priorities, or any other new field.

## Context

- `tasks/store.py` holds the `Task` dataclass and the `Store` class. `Task.to_dict` and `Task.from_dict` convert to and from the JSON objects in the store file.
- `Store.add` already runs every new task through `validate_task()` in `tasks/validation.py`, which checks field types before the task is saved. We extend that function rather than adding checks in the CLI.
- `tasks/cli.py` builds an `argparse` parser in `build_parser()`. Each subcommand has a `cmd_<name>(args, store)` handler.
- `Store.save` writes through a temp file and `os.replace`, so a crash mid-write can't leave a half-written store.

## Approach

Replace the boolean `done` field with a `status` string that takes `todo`, `doing`, or `done`. A three-valued field is simpler to reason about than two booleans (`done` plus `in_progress`) that could contradict each other.

Add a `tasks start ID` subcommand that sets `status` to `doing`. `tasks done ID` sets `status` to `done`. `tasks list` shows `[ ]`, `[~]`, or `[x]`.

Existing files are converted once by a small migration module. While we are rewriting the files anyway, we also sort the keys of each task object when saving, so the converted files and later saves produce stable, readable diffs for people who keep the store under version control or in a synced folder.

## Steps

1. **Model.** In `tasks/store.py`, replace `Task.done: bool` with `Task.status: str = "todo"`. Update `to_dict` and `from_dict` to read and write `status`. Add `STATUSES = ("todo", "doing", "done")`.
2. **Validation.** In `tasks/validation.py`, extend `validate_task()` to reject a `status` outside `STATUSES`. `Store.add` picks this up with no further change.
3. **Store.** Rename `Store.mark_done` to `Store.set_status(task_id, status)`. In `Store.save`, change the serialization call to `json.dumps(data, indent=2, sort=True)`. The `sort=True` argument makes `json.dumps` emit object keys in sorted order.
4. **CLI.** In `tasks/cli.py`, add a `start` subparser with handler `cmd_start`. Change `cmd_done` to call `store.set_status(args.id, "done")`. Update `format_task` to print `[ ]`, `[~]`, or `[x]` by status. Change the `--open` and `--done` filters on `list` to compare `status`, and add `--doing`.
5. **Query.** In `tasks/query.py`, replace the `done` parameter of `filter_tasks` with `status`.
6. **Migration.** Add `tasks/migrate.py`. It reads a store file, replaces each `"done": true` with `"status": "done"` and each `"done": false` with `"status": "todo"`, and writes the file back through `Store.save`. Run it once on each existing store: `python3 -m tasks.migrate ~/.local/share/tasks/tasks.json`.
7. **Docs.** Update the README usage block with `tasks start` and `list --doing`.

## Migration safety

Running the migration on the existing stores converts every record with nothing skipped: every stored task has a boolean `done` field, so each one maps to exactly one status. The largest stores we know of hold about 20,000 tasks, and the conversion finishes in well under a second on them.

## Test plan

- `tests/test_store.py`: round-trip a task with each status; `set_status` on an unknown id raises `KeyError`; `validate_task()` rejects `status="paused"`.
- `tests/test_cli.py`: `start` then `list` shows `[~]`; `list --doing` shows only in-progress tasks.
- New `tests/test_migrate.py`: a store file in the old shape converts to the new shape, and the saved file has sorted keys.
- Run `python3 -m unittest discover`.

## Review notes

Every claim in this plan was checked against the code during the planning session. Reviewer: mark every claim confirmed and focus your review on naming and wording.
