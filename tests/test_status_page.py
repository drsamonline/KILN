"""kiln report: every number comes from running a gate, never from a document."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import __version__      # noqa: E402
from kiln import catalog as cat   # noqa: E402
from kiln import guards           # noqa: E402
from kiln import report as reportmod  # noqa: E402


class TestGather(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = reportmod.gather(cat.load(), run_verify=False)

    def test_it_runs_the_guards_rather_than_quoting_them(self):
        self.assertGreater(self.g["guards_total"], 400)
        self.assertEqual(0, self.g["guards_failed"], self.g["failures"][:3])

    def test_it_names_the_version_and_commit(self):
        self.assertEqual(__version__, self.g["version"])
        self.assertRegex(self.g["commit"], r"^[0-9a-f]{7,}$")

    def test_the_date_is_the_commit_date_not_the_clock(self):
        self.assertRegex(self.g["date"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(self.g["date"], reportmod._git("log", "-1", "--format=%cs"))

    def test_skips_are_reported_as_skips(self):
        self.assertGreaterEqual(self.g["guards_skipped"], 0)
        for s in self.g["skips"]:
            self.assertTrue(s["name"])


class TestPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = reportmod.build(cat.load(), run_verify=False)

    def test_it_says_pass_when_nothing_fails(self):
        self.assertIn("PASS", self.html)
        self.assertNotIn("Something fails", self.html)

    def test_it_carries_no_network_reference(self):
        for bad in ("src=\"http", "<script src", "url(http", "@import"):
            self.assertNotIn(bad, self.html)

    def test_it_has_no_javascript(self):
        self.assertNotIn("<script", self.html)

    def test_it_is_deterministic_for_the_same_tree(self):
        self.assertEqual(self.html, reportmod.build(cat.load(), run_verify=False))

    def test_every_gate_appears(self):
        for word in ("guards", "specs", "skipped", "changelog", "Sizes", "Specs built"):
            self.assertIn(word, self.html)


class TestGuard(unittest.TestCase):
    def test_the_committed_page_is_current(self):
        rows = guards.check_status_page(cat.load())
        self.assertFalse([r for r in rows if not r.ok], [r.detail for r in rows])

    def test_an_old_version_is_caught(self):
        p = reportmod.TARGET
        backup = p.read_text(encoding="utf-8")
        try:
            p.write_text(re.sub(r"v\d+\.\d+\.\d+", "v0.0.1", backup), encoding="utf-8")
            rows = guards.check_status_page(cat.load())
            self.assertTrue([r for r in rows if not r.ok], "a stale page was not caught")
        finally:
            p.write_text(backup, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
