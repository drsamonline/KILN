"""Every size stated in the docs must match the build."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat  # noqa: E402
from kiln import guards          # noqa: E402
from kiln import sizes           # noqa: E402


class TestSizes(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()
        self.m = sizes.measure(self.c)

    def test_the_measurement_is_sane(self):
        self.assertGreater(self.m["app"], 20)
        self.assertLessEqual(self.m["app"], self.m["ceiling"])
        self.assertGreaterEqual(self.m["largest"], self.m["smallest"])
        self.assertGreater(self.m["studio"], 50)

    def test_every_stated_size_matches(self):
        bad = sizes.check(self.c)
        self.assertEqual([], bad, bad)

    def test_the_rewrite_is_idempotent(self):
        for rel in sizes.CLAIMS:
            p = ROOT / rel
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            self.assertEqual(text, sizes.rewrite(text, self.m), rel)

    def test_a_stale_number_is_detected(self):
        fake = dict(self.m)
        fake["app"] = self.m["app"] + 40
        text = "A generated app — %d KB, one file." % self.m["app"]
        self.assertNotEqual(text, sizes.rewrite(text, fake))

    def test_the_guard_is_in_the_audit(self):
        rows = guards.check_sizes(self.c)
        self.assertFalse([r for r in rows if not r.ok], [r.detail for r in rows])

    def test_no_doc_still_says_the_old_numbers(self):
        for rel in ("README.md", "index.html", "docs/FAQ.md", "docs/PORTABILITY.md"):
            p = ROOT / rel
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            self.assertNotIn("21 KB", text, rel)
            self.assertNotIn("under 60 KB", text, rel)


if __name__ == "__main__":
    unittest.main()
