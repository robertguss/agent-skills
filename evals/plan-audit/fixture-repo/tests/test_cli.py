import csv
import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from tasks.cli import main


class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._tmp.name, "tasks.json")

    def tearDown(self):
        self._tmp.cleanup()

    def run_cli(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--file", self.path, *argv])
        return code, out.getvalue()

    def test_add_then_list(self):
        self.run_cli("add", "water plants")
        code, out = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertIn("[ ] water plants", out)

    def test_done_marks_task(self):
        self.run_cli("add", "water plants")
        self.run_cli("done", "1")
        _, out = self.run_cli("list", "--done")
        self.assertIn("[x] water plants", out)

    def test_done_unknown_id_fails(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code, _ = self.run_cli("done", "7")
        self.assertEqual(code, 1)
        self.assertIn("No task with id 7", err.getvalue())

    def test_list_search(self):
        self.run_cli("add", "fix bike", "--notes", "rear brake")
        self.run_cli("add", "fix sink")
        _, out = self.run_cli("list", "--search", "BRAKE")
        self.assertIn("fix bike", out)
        self.assertNotIn("fix sink", out)

    def test_export_csv(self):
        self.run_cli("add", "file taxes")
        _, out = self.run_cli("export")
        rows = list(csv.reader(io.StringIO(out)))
        self.assertEqual(rows[0], ["id", "title", "notes", "done", "created"])
        self.assertEqual(rows[1][1:4], ["file taxes", "", "no"])


if __name__ == "__main__":
    unittest.main()
