"""Tests for inventory (a derived balance) and timeline (a month grouping)."""
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
INV = ROOT / "specs" / "gallery" / "inventory.md"
TL = ROOT / "specs" / "gallery" / "timeline.md"


def run_js(src: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        return subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)


class TestBalance(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def case(self, rows, want):
        src = extract.source("balanceOf") + (
            "const got = balanceOf(%s, 'qty', 'i1');\n"
            "if (got !== %s) { console.log('FAIL ' + got); process.exit(1); }\n"
            "console.log('PASS');\n" % (json.dumps(rows), json.dumps(want)))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_ten_minus_three_minus_two_is_five(self):
        self.case([{"qty": 10}, {"qty": -3}, {"qty": -2}], 5)

    def test_no_movements_is_zero(self):
        self.case([], 0)

    def test_a_missing_quantity_is_skipped(self):
        self.case([{"qty": 10}, {}, {"qty": None}], 10)

    def test_a_negative_balance_is_allowed(self):
        self.case([{"qty": 2}, {"qty": -5}], -3)

    def test_a_string_number_is_coerced(self):
        self.case([{"qty": "7"}, {"qty": "-2"}], 5)


class TestGroupByMonth(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def groups(self, rows):
        src = extract.source("groupByMonth") + (
            "const g = groupByMonth(%s, 'date');\n"
            "console.log(JSON.stringify(g.map((x) => [x.key, x.rows.length])));\n"
            % json.dumps(rows))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stderr)
        return json.loads(p.stdout)

    def test_two_months(self):
        rows = [{"date": "2026-11-04"}, {"date": "2026-11-13"}, {"date": "2026-10-14"}]
        self.assertEqual([["2026-11", 2], ["2026-10", 1]], self.groups(rows))

    def test_newest_first(self):
        rows = [{"date": "2025-01-01"}, {"date": "2026-11-04"}]
        self.assertEqual(["2026-11", "2025-01"], [g[0] for g in self.groups(rows)])

    def test_an_undated_record_is_kept_last(self):
        rows = [{"date": ""}, {"date": "2026-11-04"}]
        self.assertEqual([["2026-11", 1], ["", 1]], self.groups(rows))

    def test_no_rows_is_no_groups(self):
        self.assertEqual([], self.groups([]))

    def test_a_malformed_date_is_undated(self):
        rows = [{"date": "sometime"}]
        self.assertEqual([["", 1]], self.groups(rows))


class TestInventorySpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_balances_a_signed_field(self):
        s = specmod.load(INV, self.c)
        self.assertEqual("qty", s["balance"]["field"])
        self.assertEqual("reorder", s["balance"]["reorder"])

    def test_a_non_numeric_balance_field_is_refused(self):
        s = specmod.load(INV, self.c)
        s["balance"]["field"] = "title"
        problems = specmod.validate(s, self.c, "inventory.md")
        self.assertTrue(any("must be numeric" in p for p in problems), problems)

    def test_a_balance_lookup_that_is_not_a_lookup_is_refused(self):
        s = specmod.load(INV, self.c)
        s["balance"]["lookup"] = "title"
        problems = specmod.validate(s, self.c, "inventory.md")
        self.assertTrue(any("must be the lookup field" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(INV, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function balanceOf(", html)
            self.assertIn("to reorder", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestTimelineSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_groups_on_a_date(self):
        s = specmod.load(TL, self.c)
        self.assertEqual("date", s["timeline"]["field"])

    def test_a_timeline_on_a_text_field_is_refused(self):
        s = specmod.load(TL, self.c)
        s["timeline"] = {"field": "title"}
        problems = specmod.validate(s, self.c, "timeline.md")
        self.assertTrue(any("must be a date" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(TL, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function groupByMonth(", html)
            self.assertIn("function renderTimeline(", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_a_timeline_carries_no_balance(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(TL, self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("function balanceOf(", html)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
