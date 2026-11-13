"""Tests for the generated guides: they must be current, and they must be complete."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat   # noqa: E402
from kiln import guide as guidemod  # noqa: E402
from kiln import guards           # noqa: E402
from kiln import spec as specmod  # noqa: E402


class TestGeneratedGuides(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_generation_is_deterministic(self):
        self.assertEqual(guidemod.build(self.c), guidemod.build(self.c))

    def test_the_committed_guides_are_current(self):
        for name, text in guidemod.build(self.c).items():
            p = ROOT / name
            self.assertTrue(p.exists(), f"{name} is missing")
            self.assertEqual(text, p.read_text(encoding="utf-8"),
                             f"{name} is stale: run python3 -m kiln guide")

    def test_every_capability_appears(self):
        text = guidemod.features_guide(self.c)
        for fid in self.c["features"]:
            self.assertIn(f"`{fid}`", text, fid)

    def test_every_field_type_appears(self):
        text = guidemod.spec_reference(self.c)
        for t in specmod.FIELD_TYPES:
            self.assertIn(f"`{t}`", text, t)

    def test_every_archetype_appears(self):
        for text in guidemod.build(self.c).values():
            for pid in cat.patterns():
                self.assertIn(f"`{pid}`", text, pid)

    def test_every_registry_family_appears(self):
        text = guidemod.features_guide(self.c)
        for fam in {e["family"] for e in cat.registry().values()}:
            self.assertIn(fam, text, fam)

    def test_the_guides_carry_no_date(self):
        for text in guidemod.build(self.c).values():
            self.assertNotIn("2026-", text.split("---")[0])


class TestGuideSet(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_all_six_guides_exist(self):
        for name in guards.GUIDES:
            p = ROOT / name
            self.assertTrue(p.exists(), name)
            self.assertGreater(p.stat().st_size, 400, name)

    def test_the_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_guides(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)

    def test_each_guide_has_the_required_sections(self):
        for name in guards.GUIDES:
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("TL;DR", text, name)
            self.assertIn("## Links", text, name)


if __name__ == "__main__":
    unittest.main()
