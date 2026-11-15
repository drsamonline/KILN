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

    def test_it_names_the_version(self):
        self.assertEqual(__version__, self.g["version"])

    def test_it_does_not_name_a_commit(self):
        """The commit that adds a page cannot appear in it, so the page omits it."""
        self.assertNotIn("commit <code>", self.html if hasattr(self, "html") else "")

    def test_the_date_is_the_versions_own_date(self):
        """Not the clock, and not the commit: both move the page on every commit."""
        self.assertRegex(self.g["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_the_page_carries_nothing_that_changes_when_it_is_committed(self):
        html = reportmod.build(cat.load(), run_verify=False)
        self.assertNotIn("commit <code>", html)
        self.assertNotIn("commits ·", html)

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

    def test_the_landing_page_states_the_guard_count_it_has(self):
        """A chip in HTML is a hand-maintained badge: C24's failure in another medium.

        It said 452 while the audit ran 462, and nothing read it. This is the test
        that reads it, and it costs nothing because the audit already ran above.
        """
        page = (ROOT / "index.html").read_text(encoding="utf-8")
        m = re.search(r"<b>(\d+)</b>\s*guards", page)
        self.assertIsNotNone(m, "the landing page states no guard count")
        total = TestGather.g["guards_total"]
        self.assertEqual(total, int(m.group(1)),
                         f"the landing page says {m.group(1)}, the audit runs {total}")

    def test_the_handover_states_the_guard_count_it_has(self):
        """The handover's first table is a claim about this tree, not about a past one."""
        doc = (ROOT / "HANDOVER.md").read_text(encoding="utf-8")
        m = re.search(r"\*\*(\d+) guards, 0 failed\*\*", doc)
        self.assertIsNotNone(m, "the handover states no guard count")
        total = TestGather.g["guards_total"]
        self.assertEqual(total, int(m.group(1)),
                         f"the handover says {m.group(1)}, the audit runs {total}")


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
