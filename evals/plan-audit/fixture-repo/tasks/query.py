"""Filtering for task lists."""


def filter_tasks(tasks, search=None, done=None):
    """Return the tasks that match every filter given.

    search: case-insensitive substring matched against title and notes.
    done: True for finished tasks only, False for open tasks only.
    """
    needle = search.casefold() if search else None
    result = []
    for task in tasks:
        if done is not None and task.done != done:
            continue
        if needle and needle not in task.title.casefold() and needle not in task.notes.casefold():
            continue
        result.append(task)
    return result
