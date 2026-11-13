"""Tests for money across rows: variance and line amounts."""
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
BUDGET = ROOT / "specs" / "gallery" / "budget.md"
INVOICE = ROOT / "specs" / "gallery" / "invoice.md"


def run_js(src: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        return subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)


class TestVariance(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def case(self, planned, actual, want):
        src = extract.source("varianceOf") + (
            "const got = varianceOf(%s, %s);\n"
            "const want = %s;\n"
            "if (JSON.stringify(got) !== JSON.stringify(want)) {"
            " console.log('FAIL ' + JSON.stringify(got)); process.exit(1); }\n"
            "console.log('PASS');\n" % (json.dumps(planned), json.dumps(actual),
                                        json.dumps(want, separators=(",", ":"))))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_five_thousand_against_three_and_a_half(self):
        self.case(500000, 350000,
                  {"planned": 500000, "actual": 350000, "remaining": 150000,
                   "pct": 70, "over": False})

    def test_an_overspend_is_negative_and_flagged(self):
        self.case(200000, 260000,
                  {"planned": 200000, "actual": 260000, "remaining": -60000,
                   "pct": 130, "over": True})

    def test_nothing_planned_but_something_spent(self):
        self.case(0, 5000,
                  {"planned": 0, "actual": 5000, "remaining": -5000, "pct": 100,
                   "over": True})

    def test_nothing_at_all(self):
        self.case(0, 0, {"planned": 0, "actual": 0, "remaining": 0, "pct": 0, "over": False})

    def test_exactly_on_budget_is_not_over(self):
        self.case(1000, 1000,
                  {"planned": 1000, "actual": 1000, "remaining": 0, "pct": 100,
                   "over": False})


class TestAmount(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def case(self, qty, rate, want):
        src = extract.source("amountOf") + (
            "const got = amountOf(%s, %s);\n"
            "if (got !== %s) { console.log('FAIL ' + got); process.exit(1); }\n"
            "console.log('PASS');\n" % (json.dumps(qty), json.dumps(rate), json.dumps(want)))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_three_at_two_fifty(self):
        self.case(3, 25000, 75000)

    def test_a_fractional_quantity_rounds_once(self):
        self.case(1.5, 10000, 15000)

    def test_a_third_of_a_rupee_rounds(self):
        self.case(1, 33, 33)

    def test_no_quantity_is_zero(self):
        self.case(None, 500, 0)

    def test_a_bad_rate_is_zero(self):
        self.case(2, "abc", 0)

    def test_the_lines_of_the_sample_add_up(self):
        src = extract.source("amountOf") + (
            "const lines = [[1, 150000], [2, 60000], [3, 25000], [1, 40000]];\n"
            "let t = 0; for (const l of lines) t += amountOf(l[0], l[1]);\n"
            "console.log(t);\n")
        p = run_js(src)
        self.assertEqual("385000", p.stdout.strip())


class TestBudgetSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_names_both_amounts(self):
        s = specmod.load(BUDGET, self.c)
        self.assertEqual("planned", s["variance"]["planned"])
        self.assertEqual("actual", s["variance"]["actual"])

    def test_a_non_numeric_planned_field_is_refused(self):
        s = specmod.load(BUDGET, self.c)
        s["variance"]["planned"] = "title"
        problems = specmod.validate(s, self.c, "budget.md")
        self.assertTrue(any("must be numeric" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(BUDGET, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function varianceOf(", html)
            self.assertIn("vfill", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestInvoiceSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_names_quantity_and_rate(self):
        s = specmod.load(INVOICE, self.c)
        self.assertEqual("qty", s["amount"]["qty"])
        self.assertEqual("rate", s["amount"]["rate"])

    def test_a_missing_quantity_field_is_refused(self):
        s = specmod.load(INVOICE, self.c)
        s["amount"]["qty"] = "nope"
        problems = specmod.validate(s, self.c, "invoice.md")
        self.assertTrue(any("is not a field" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(INVOICE, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function amountOf(", html)
            self.assertIn("Math.round(q * r)", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_an_invoice_carries_no_variance_bar(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(INVOICE, self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("function varianceOf(", html)
            # .vbar is base CSS shared with the tally view, so only the maths is checked here
            self.assertNotIn("varianceOf(", html)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
