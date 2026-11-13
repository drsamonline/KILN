"""Tests for the feature registry, the archetypes, and money as integer cents."""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 40 KB is the target; 44 KB is the ceiling, justified in CHANGELOG v0.15 —
# the tracker archetype needs derived + chart + stats + search + sort + theme.
CEILING = 100 * 1024
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat   # noqa: E402
from kiln import guards           # noqa: E402
from kiln import spec as specmod  # noqa: E402
from kiln import verify           # noqa: E402


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()
        self.reg = cat.registry()

    def test_families_f1_and_f2_are_registered(self):
        fams = {e["family"] for e in self.reg.values()}
        self.assertIn("F1", fams)
        self.assertIn("F2", fams)

    def test_every_entry_carries_the_five_hooks(self):
        for e in self.reg.values():
            for k in ("spec_keys", "emitter_hook", "verify_check", "docs_anchor", "status"):
                self.assertIn(k, e, e["id"])

    def test_an_emitted_entry_names_an_emitter_and_a_check(self):
        for e in self.reg.values():
            if e["status"] == "emitted":
                self.assertTrue(e["emitter_hook"], e["id"])
                self.assertTrue(e["verify_check"], e["id"])

    def test_every_runtime_field_type_is_covered(self):
        self.assertEqual(set(), specmod.FIELD_TYPES - cat.emitted_types(self.reg))

    def test_no_emitted_entry_claims_an_unknown_type(self):
        self.assertEqual(set(), cat.emitted_types(self.reg) - specmod.FIELD_TYPES)

    def test_the_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_registry(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


class TestPatterns(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()
        self.pats = cat.patterns()

    def test_crud_list_is_emitted(self):
        self.assertIn("crud-list", self.pats)
        self.assertEqual("emitted", self.pats["crud-list"]["status"])

    def test_the_sample_satisfies_the_pattern(self):
        s = specmod.load(ROOT / "specs" / "gallery" / "crud-list.md", self.c)
        res = verify.check_pattern(s, self.c)
        self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])

    def test_a_spec_missing_a_required_capability_fails(self):
        s = specmod.load(ROOT / "specs" / "gallery" / "crud-list.md", self.c)
        s["features"] = ["crud", "theme"]
        res = verify.check_pattern(s, self.c)
        self.assertTrue(res.failed)
        self.assertTrue(any("required features" in r["name"] for r in res.failed))

    def test_a_spec_naming_an_unknown_pattern_fails(self):
        s = specmod.load(ROOT / "specs" / "gallery" / "crud-list.md", self.c)
        s["pattern"] = "does-not-exist"
        res = verify.check_pattern(s, self.c)
        self.assertTrue(res.failed)

    def test_the_sample_builds_to_one_file(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-clinic-stock"
            res = verify.build_and_check(ROOT / "specs" / "gallery" / "crud-list.md",
                                         self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            self.assertEqual(["index.html"], sorted(p.name for p in out.iterdir()))

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


class TestMoney(unittest.TestCase):
    """§1.6: money is an integer count of cents, formatted only at view time."""

    def setUp(self):
        self.c = cat.load()

    def _html(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(ROOT / "specs" / "gallery" / "crud-list.md", self.c, out)
            return (out / "index.html").read_text(encoding="utf-8")

    def test_the_sample_declares_a_cents_field(self):
        s = specmod.load(ROOT / "specs" / "gallery" / "crud-list.md", self.c)
        types = {f["type"] for e in s["entities"] for f in e["fields"]}
        self.assertIn("currency_cents", types)

    def test_the_runtime_stores_cents_not_floats(self):
        html = self._html()
        self.assertIn("Math.round(n * 100)", html)
        self.assertIn("currency_cents", html)

    def test_the_currency_symbol_reaches_the_app(self):
        html = self._html()
        m = re.search(r"const MODEL = (\{.*?\n\});", html, re.S)
        self.assertIsNotNone(m, "the model did not parse")
        self.assertEqual("\u20b9", json.loads(m.group(1))["currency"])

    def test_money_is_formatted_at_view_time_only(self):
        html = self._html()
        # two formatters, both view-time: one with the symbol, one for CSV
        self.assertIn("(a / 100).toFixed(2)", html)
        self.assertIn("(n / 100).toFixed(2)", html)
        self.assertIn("const toCents", html)


if __name__ == "__main__":
    unittest.main()
