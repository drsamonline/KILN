"""kiln report --json and --badge: the same numbers, for a machine."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import __version__      # noqa: E402
from kiln import catalog as cat   # noqa: E402
from kiln import guards           # noqa: E402
from kiln import report as reportmod  # noqa: E402


class TestJson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = reportmod.gather(cat.load(), run_verify=False)
        cls.doc = json.loads(reportmod.as_json(cls.g))

    def test_it_is_valid_json_with_the_expected_keys(self):
        for k in ("version", "date", "guards", "specs", "sizes_kb", "versions",
                  "failures", "skips", "ok"):
            self.assertIn(k, self.doc)

    def test_the_numbers_add_up(self):
        g = self.doc["guards"]
        self.assertEqual(g["total"], g["passed"] + g["failed"] + g["skipped"])

    def test_it_carries_the_version(self):
        self.assertEqual(__version__, self.doc["version"])

    def test_ok_is_true_only_when_nothing_failed(self):
        expected = self.doc["guards"]["failed"] == 0 and self.doc["specs"]["failed"] == 0
        self.assertEqual(expected, self.doc["ok"])

    def test_it_is_deterministic_apart_from_the_timestamp(self):
        """The page must be reproducible; the feed must be checkable for freshness."""
        a = json.loads(reportmod.as_json(self.g, now="2026-11-15T00:00:00Z"))
        b = json.loads(reportmod.as_json(self.g, now="2026-11-16T00:00:00Z"))
        self.assertNotEqual(a["generated_at"], b["generated_at"])
        del a["generated_at"], b["generated_at"]
        self.assertEqual(a, b)

    def test_it_carries_the_instant_the_gate_ran(self):
        import datetime as dt
        stamp = self.doc["generated_at"]
        self.assertRegex(stamp, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        # and it parses, so a consumer can subtract it from now
        dt.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")

    def test_the_page_does_not_carry_a_clock(self):
        """The page is the reproducible artefact; the clock belongs in the feed only."""
        html = reportmod.build(cat.load(), run_verify=False)
        self.assertNotIn("generated_at", html)

    def test_keys_are_sorted_so_a_diff_is_readable(self):
        text = reportmod.as_json(self.g)
        self.assertEqual(text, json.dumps(self.g_doc(), indent=2, sort_keys=True) + "\n")

    def g_doc(self):
        return json.loads(reportmod.as_json(self.g))


class TestBadge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = reportmod.gather(cat.load(), run_verify=False)
        cls.badge = json.loads(reportmod.badge(cls.g))

    def test_it_is_a_shields_endpoint_document(self):
        self.assertEqual(1, self.badge["schemaVersion"])
        self.assertIn("label", self.badge)
        self.assertIn("message", self.badge)
        self.assertIn(self.badge["color"], ("brightgreen", "red"))

    def test_the_message_names_the_counts(self):
        self.assertIn(f"{self.badge['message'].split('/')[1].split()[0]}", self.badge["message"])
        self.assertIn("guards", self.badge["message"])

    def test_the_colour_follows_the_verdict(self):
        self.assertEqual("brightgreen" if self.g["guards_failed"] == 0 else "red",
                         self.badge["color"])

    def test_the_committed_badge_is_current(self):
        rows = guards.check_badge(cat.load())
        self.assertFalse([r for r in rows if not r.ok], [r.detail for r in rows])

    def test_a_badge_that_disagrees_with_the_page_is_caught(self):
        p = reportmod.BADGE
        backup = p.read_text(encoding="utf-8")
        try:
            doc = json.loads(backup)
            doc["color"] = "red" if doc["color"] == "brightgreen" else "brightgreen"
            p.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            rows = guards.check_badge(cat.load())
            self.assertTrue([r for r in rows if not r.ok], "a disagreeing badge was not caught")
        finally:
            p.write_text(backup, encoding="utf-8")


class TestNoRecursion(unittest.TestCase):
    def test_the_badge_guard_does_not_run_the_audit(self):
        """It is called by the audit; calling the audit back would never return."""
        import inspect
        src = inspect.getsource(guards.check_badge)
        self.assertNotIn("guards.audit", src)
        self.assertNotIn("gather(", src)


if __name__ == "__main__":
    unittest.main()
