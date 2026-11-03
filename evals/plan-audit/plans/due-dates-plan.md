---
title: Due dates for tasks
type: feat
date: 2026-11-02
status: ready
---

# Due dates for tasks

## Overview

Several people keep deadlines in task titles ("Pay rent by the 1st"), which can't be sorted or filtered, so this change gives tasks an optional due date that is stored as its own field. The plan is to add a `due` field to the `Task` dataclass in `tasks/store.py`, holding an ISO date string (`YYYY-MM-DD`) or `None`, and to read it in `Task.from_dict` with `data.get("due")`, the same way `notes` is read with `data.get("notes", "")` today, so task files written before this change load unchanged with no due dates. `Task.to_dict` always writes the `due` key; older copies of the program ignore it, because `from_dict` reads only the keys it names. On the command line, `tasks add` gets a `--due YYYY-MM-DD` option, `tasks list` shows the due date after the title when there is one, and a new `tasks list --overdue` shows open tasks whose due date is before today. The CSV export gains a `due` column at the end, so spreadsheets that read columns by position keep working. Everything stays standard library only and runs on Python 3.9 or later, which `datetime.date.fromisoformat` supports. Recurring tasks, reminders, and times of day are out of scope.

## Steps

1. **Model.** In `tasks/store.py`, add `due: Optional[str] = None` to `Task` after `done`. Write it in `to_dict` and read it with `data.get("due")` in `from_dict`. Add a `due=None` parameter to `Store.add` and pass it to the new `Task`.
2. **Parsing.** In `tasks/cli.py`, add `parse_due(text)`, which returns `datetime.date.fromisoformat(text).isoformat()` and raises `argparse.ArgumentTypeError("due date must be YYYY-MM-DD")` on `ValueError`. Use it as the `type=` of a new `--due` option on the `add` subparser, and pass `args.due` to `store.add`.
3. **Filtering.** In `tasks/query.py`, add a `due_before=None` parameter to `filter_tasks`. When it is a `date`, keep only tasks that have a due date earlier than it. Tasks with no due date never match.
4. **Listing.** In `tasks/cli.py`, add `--overdue` to the existing mutually exclusive `--open`/`--done` group on `list`. In `cmd_list`, `--overdue` calls `filter_tasks` with `done=False` and `due_before=date.today()`. Change `format_task` to append ` (due YYYY-MM-DD)` when the task has a due date.
5. **Export.** In `tasks/export.py`, append `"due"` to `FIELDS` and write `task.due or ""` as the last column in `write_csv`.
6. **Docs.** Add `--due` and `list --overdue` to the README Usage block.

## Tests

- `tests/test_store.py`: a task added with a due date round-trips; a store file written without any `due` keys loads with `due` set to `None`.
- `tests/test_store.py` (`FilterTest`): `filter_tasks(..., due_before=date(2026, 1, 10))` keeps a task due 2026-01-09, drops one due 2026-01-10, and drops one with no due date. The test passes the date in, so it doesn't depend on today's date.
- `tests/test_cli.py`: `add --due 2000-01-01` then `list --overdue` shows the task; `add --due tomorrow` exits with an argparse error; `list` shows `(due 2000-01-01)`.
- `tests/test_cli.py`: update `test_export_csv` for the new header, `["id", "title", "notes", "done", "created", "due"]`.
- Run `python3 -m unittest discover`.
