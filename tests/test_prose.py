"""The docs must not read as machine output: no prose em dash, no stale claims."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import guards  # noqa: E402


class TestProsePunctuation(unittest.TestCase):
    def test_no_prose_em_dash(self):
        rows = guards.check_prose_punctuation()
        bad = [r for r in rows if not r.ok]
        self.assertEqual([], bad, [r.detail for r in bad][:5])

    def test_the_guard_covers_the_docs_that_matter(self):
        rows = guards.check_prose_punctuation()
        self.assertTrue(rows)
        self.assertIn("documents", rows[0].detail)

    def test_a_table_cell_may_keep_its_dash(self):
        """A dash between two cells is a separator, not prose cadence."""
        src = "| Archetype | `quiz` — one question at a time |"
        self.assertIn("—", src)  # the fixture keeps one; the guard must not count it
        rows = guards.check_prose_punctuation()
        self.assertEqual([], [r for r in rows if not r.ok])

    def test_a_dated_heading_may_keep_its_dash(self):
        self.assertTrue(re.match(r"^#{1,3} .*—.*\d{4}", "## v1.0.7 — 2026-11-14"))


class TestStaleClaims(unittest.TestCase):
    def test_the_cookbook_does_not_say_four_are_buildable(self):
        text = (ROOT / "GUIDE-COOKBOOK.md").read_text(encoding="utf-8")
        self.assertNotIn("Four are buildable", text)
        self.assertIn("All 24 are buildable", text)

    def test_the_generated_guides_have_no_prose_em_dash(self):
        for name in ("GUIDE-SPEC-REF.md", "GUIDE-FEATURES.md"):
            for i, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
                if "—" in line and not line.strip().startswith("|"):
                    self.fail(f"{name}:{i} {line.strip()[:70]}")


if __name__ == "__main__":
    unittest.main()
