"""Task model and JSON file storage."""

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone

DEFAULT_PATH = os.path.join("~", ".local", "share", "tasks", "tasks.json")


def default_path():
    """Return the store path from TASKS_FILE, or the default location."""
    return os.path.expanduser(os.environ.get("TASKS_FILE", DEFAULT_PATH))


@dataclass
class Task:
    id: int
    title: str
    notes: str = ""
    done: bool = False
    created: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "notes": self.notes,
            "done": self.done,
            "created": self.created,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data["title"],
            notes=data.get("notes", ""),
            done=data["done"],
            created=data["created"],
        )


class Store:
    """A list of tasks kept in one JSON file.

    The file holds a JSON array of task objects. A missing file is an
    empty store.
    """

    def __init__(self, path):
        self.path = path

    def load(self):
        try:
            with open(self.path, encoding="utf-8") as fh:
                raw = json.load(fh)
        except FileNotFoundError:
            return []
        return [Task.from_dict(item) for item in raw]

    def save(self, tasks):
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)
        payload = json.dumps([t.to_dict() for t in tasks], indent=2)
        fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tasks-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(payload + "\n")
            os.replace(tmp, self.path)
        except BaseException:
            os.unlink(tmp)
            raise

    def add(self, title, notes=""):
        title = title.strip()
        if not title:
            raise ValueError("title must not be empty")
        tasks = self.load()
        next_id = max((t.id for t in tasks), default=0) + 1
        task = Task(id=next_id, title=title, notes=notes)
        tasks.append(task)
        self.save(tasks)
        return task

    def mark_done(self, task_id):
        tasks = self.load()
        for task in tasks:
            if task.id == task_id:
                task.done = True
                self.save(tasks)
                return task
        raise KeyError(task_id)
