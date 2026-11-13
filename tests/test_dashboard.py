"""Tests for multi-entity storage and the dashboard archetype."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import _extract as extract      # noqa: E402
from kiln import catalog as cat  # noqa: E402
from kiln import guards          # noqa: E402
from kiln import spec as specmod  # noqa: E402
from kiln import verify          # noqa: E402

CEILING = 100 * 1024
SPEC = ROOT / "specs" / "gallery" / "dashboard.md"


class TestMetricOf(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def case(self, rows, card, want):
        src = extract.source("metricOf") + (
            "const got = metricOf(%s, %s);\n"
            "if (got !== %s) { console.log('FAIL ' + got); process.exit(1); }\n"
            "console.log('PASS');\n" % (json.dumps(rows), json.dumps(card), json.dumps(want)))
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_count(self):
        self.case([{"a": 1}, {"a": 2}], {"metric": "count"}, 2)

    def test_sum(self):
        self.case([{"m": 35}, {"m": 20}, {"m": 25}], {"metric": "sum", "field": "m"}, 80)

    def test_average(self):
        self.case([{"m": 35}, {"m": 20}, {"m": 25}], {"metric": "avg", "field": "m"}, 80 / 3)

    def test_max_and_min(self):
        rows = [{"m": 35}, {"m": 20}, {"m": 25}]
        self.case(rows, {"metric": "max", "field": "m"}, 35)
        self.case(rows, {"metric": "min", "field": "m"}, 20)

    def test_latest_uses_the_date(self):
        rows = [{"m": 35, "date": "2026-11-04"}, {"m": 20, "date": "2026-11-12"}]
        self.case(rows, {"metric": "latest", "field": "m"}, 20)

    def test_missing_values_are_skipped(self):
        self.case([{"m": 10}, {}, {"m": None}], {"metric": "sum", "field": "m"}, 10)

    def test_an_empty_list_is_zero(self):
        self.case([], {"metric": "sum", "field": "m"}, 0)

    def test_no_field_is_zero(self):
        self.case([{"m": 10}], {"metric": "sum"}, 0)


class TestMultiEntity(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_declares_two_entities(self):
        s = specmod.load(SPEC, self.c)
        self.assertEqual(["patient", "visit"], [e["name"] for e in s["entities"]])
        self.assertEqual(4, len(s["dashboard"]["cards"]))

    def test_two_entities_without_the_capability_are_refused(self):
        s = specmod.load(SPEC, self.c)
        s["features"] = [f for f in s["features"] if f != "multi"]
        problems = specmod.validate(s, self.c, "dashboard.md")
        self.assertTrue(any("need the 'multi' capability" in p for p in problems), problems)

    def test_multi_with_one_entity_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["entities"] = s["entities"][:1]
        problems = specmod.validate(s, self.c, "dashboard.md")
        self.assertTrue(any("at least two entities" in p for p in problems), problems)

    def test_a_card_naming_a_missing_entity_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["dashboard"]["cards"][0]["entity"] = "nope"
        problems = specmod.validate(s, self.c, "dashboard.md")
        self.assertTrue(any("does not exist" in p for p in problems), problems)

    def test_a_sum_without_a_field_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["dashboard"]["cards"][2].pop("field", None)
        problems = specmod.validate(s, self.c, "dashboard.md")
        self.assertTrue(any("needs a field" in p for p in problems), problems)

    def test_a_sum_on_a_text_field_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["dashboard"]["cards"][2]["field"] = "title"
        problems = specmod.validate(s, self.c, "dashboard.md")
        self.assertTrue(any("not numeric" in p for p in problems), problems)

    def test_it_builds_to_one_file_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(SPEC, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            for needed in ("function setEntity(", "function metricOf(", "function renderDash(",
                           "data: DB"):
                self.assertIn(needed, html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_a_single_entity_app_keeps_the_old_storage_shape(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("rows: rows", html)
            self.assertNotIn("function setEntity(", html)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
