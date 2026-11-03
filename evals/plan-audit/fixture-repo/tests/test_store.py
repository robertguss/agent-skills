import json
import os
import tempfile
import unittest

from tasks.query import filter_tasks
from tasks.store import Store, Task


class StoreTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "tasks.json")
        self.store = Store(self.path)

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_file_is_empty(self):
        self.assertEqual(self.store.load(), [])

    def test_add_assigns_increasing_ids(self):
        first = self.store.add("write report")
        second = self.store.add("send report")
        self.assertEqual((first.id, second.id), (1, 2))

    def test_add_rejects_blank_title(self):
        with self.assertRaises(ValueError):
            self.store.add("   ")

    def test_round_trip(self):
        self.store.add("buy milk", notes="semi-skimmed")
        [task] = self.store.load()
        self.assertEqual(task.title, "buy milk")
        self.assertEqual(task.notes, "semi-skimmed")
        self.assertFalse(task.done)

    def test_file_is_a_json_array(self):
        self.store.add("one")
        with open(self.path, encoding="utf-8") as fh:
            raw = json.load(fh)
        self.assertIsInstance(raw, list)
        self.assertEqual(raw[0]["title"], "one")

    def test_mark_done(self):
        task = self.store.add("call plumber")
        self.store.mark_done(task.id)
        self.assertTrue(self.store.load()[0].done)

    def test_mark_done_unknown_id(self):
        with self.assertRaises(KeyError):
            self.store.mark_done(99)


class FilterTest(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            Task(id=1, title="Renew passport", notes="photo booth on Main St"),
            Task(id=2, title="Pay rent", done=True),
            Task(id=3, title="Book flights", notes="check PASSPORT expiry"),
        ]

    def test_search_matches_title_and_notes_case_insensitively(self):
        found = filter_tasks(self.tasks, search="passport")
        self.assertEqual([t.id for t in found], [1, 3])

    def test_done_filter(self):
        self.assertEqual([t.id for t in filter_tasks(self.tasks, done=True)], [2])
        self.assertEqual([t.id for t in filter_tasks(self.tasks, done=False)], [1, 3])

    def test_no_filters_returns_everything(self):
        self.assertEqual(len(filter_tasks(self.tasks)), 3)


if __name__ == "__main__":
    unittest.main()
