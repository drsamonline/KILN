"""The printable changelog must be the changelog, and must say nothing new."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat    # noqa: E402
from kiln import changelog as chlog  # noqa: E402
from kiln import guards            # noqa: E402


class TestParse(unittest.TestCase):
    def setUp(self):
        self.versions = chlog.parse(chlog.SOURCE.read_text(encoding="utf-8"))

    def test_every_version_heading_is_found(self):
        text = chlog.SOURCE.read_text(encoding="utf-8")
        headings = re.findall(r"^## (v[\d.]+) — ", text, re.M)
        self.assertEqual(len(headings), len(self.versions))
        self.assertEqual(headings, [v["version"] for v in self.versions])

    def test_newest_first_and_oldest_last(self):
        self.assertGreater(self.versions[0]["version"], self.versions[-1]["version"])
        self.assertEqual("v0.1", self.versions[-1]["version"])

    def test_every_version_has_a_date_and_a_summary(self):
        for v in self.versions:
            self.assertRegex(v["date"], r"^\d{4}-\d{2}-\d{2}$", v["version"])
            self.assertTrue(v["summary"], v["version"])


class TestRender(unittest.TestCase):
    def setUp(self):
        self.html = chlog.build(cat.load())

    def test_it_is_deterministic(self):
        self.assertEqual(self.html, chlog.build(cat.load()))

    def test_tables_become_tables(self):
        self.assertIn("<table>", self.html)
        self.assertIn("<th>", self.html)

    def test_inline_code_becomes_code(self):
        self.assertIn("<code>", self.html)

    def test_no_raw_markdown_pipes_survive_in_a_paragraph(self):
        # a table row must not leak as text
        for line in self.html.splitlines():
            self.assertFalse(line.strip().startswith("|"), line[:80])

    def test_it_carries_no_network_reference(self):
        for bad in ("src=\"http", "<script src", "@import url(http", "url(http"):
            self.assertNotIn(bad, self.html)

    def test_it_says_where_it_came_from(self):
        self.assertIn("from CHANGELOG.md", self.html)
        self.assertIn("No entry was", self.html)


class TestGuard(unittest.TestCase):
    def test_the_committed_page_is_current(self):
        rows = guards.check_changelog_report(cat.load())
        self.assertFalse([r for r in rows if not r.ok], [r.detail for r in rows])

    def test_a_stale_page_is_caught(self):
        target = chlog.TARGET
        backup = target.read_text(encoding="utf-8") if target.exists() else None
        try:
            target.write_text("<!doctype html><title>old</title>", encoding="utf-8")
            rows = guards.check_changelog_report(cat.load())
            self.assertTrue([r for r in rows if not r.ok], "a stale page was not caught")
        finally:
            if backup is not None:
                target.write_text(backup, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
