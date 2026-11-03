"""Command-line entry point: python3 -m tasks.cli <command> ..."""

import argparse
import sys

from tasks.export import write_csv
from tasks.query import filter_tasks
from tasks.store import Store, default_path


def format_task(task):
    mark = "x" if task.done else " "
    return f"{task.id:>4} [{mark}] {task.title}"


def cmd_add(args, store):
    task = store.add(args.title, notes=args.notes)
    print(f"Added task {task.id}")
    return 0


def cmd_list(args, store):
    done = None
    if args.open:
        done = False
    elif args.done:
        done = True
    for task in filter_tasks(store.load(), search=args.search, done=done):
        print(format_task(task))
    return 0


def cmd_done(args, store):
    try:
        task = store.mark_done(args.id)
    except KeyError:
        print(f"No task with id {args.id}", file=sys.stderr)
        return 1
    print(f"Completed task {task.id}")
    return 0


def cmd_export(args, store):
    tasks = store.load()
    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            write_csv(tasks, fh)
    else:
        write_csv(tasks, sys.stdout)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="tasks", description="Keep a simple task list.")
    parser.add_argument(
        "--file", help="path to the task file (default: $TASKS_FILE or ~/.local/share/tasks/tasks.json)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a task")
    p_add.add_argument("title")
    p_add.add_argument("--notes", default="")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="list tasks")
    p_list.add_argument("--search", help="only tasks whose title or notes contain this text")
    state = p_list.add_mutually_exclusive_group()
    state.add_argument("--open", action="store_true", help="only open tasks")
    state.add_argument("--done", action="store_true", help="only finished tasks")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="mark a task finished")
    p_done.add_argument("id", type=int)
    p_done.set_defaults(func=cmd_done)

    p_export = sub.add_parser("export", help="export tasks as CSV")
    p_export.add_argument("--output", help="write to this file instead of stdout")
    p_export.set_defaults(func=cmd_export)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    store = Store(args.file or default_path())
    return args.func(args, store)


if __name__ == "__main__":
    sys.exit(main())
