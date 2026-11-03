"""Export tasks to CSV."""

import csv

FIELDS = ["id", "title", "notes", "done", "created"]


def write_csv(tasks, out):
    """Write tasks as CSV rows to the file object out."""
    writer = csv.writer(out)
    writer.writerow(FIELDS)
    for task in tasks:
        writer.writerow(
            [task.id, task.title, task.notes, "yes" if task.done else "no", task.created]
        )
