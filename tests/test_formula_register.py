"""Tests for formula-app (a computed column) and register (a running balance),
plus the check that keeps a strip figure inside the strip."""
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
FORMULA = ROOT / "specs" / "gallery" / "formula-app.md"
REGISTER = ROOT / "specs" / "gallery" / "register.md"

# capability -> a string only that capability's strip figure contains
STRIP_FIGURES = {
    "formula-app": "bad rows",
    "register": "closing",
    "budget": " left</span>",
    "invoice": " total</span>",
    "decision-log": " open</span>",
    "scheduler": "due this week",
    "playlist": " total</span>",
    "voting": " votes</span>",
}


class TestRunningTotal(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def run_case(self, rows, want_order, want_marks, want_closing):
        src = extract.source("runningTotal") + (
            "const r = runningTotal(%s, 'amount', 'date');\n"
            "const got = {order: r.order.map((x) => x.id), marks: r.marks, closing: r.closing};\n"
            "const want = %s;\n"
            "if (JSON.stringify(got) !== JSON.stringify(want)) {"
            " console.log('FAIL ' + JSON.stringify(got)); process.exit(1); }\n"
            "console.log('PASS');\n"
            % (json.dumps(rows),
               json.dumps({"order": want_order, "marks": want_marks,
                           "closing": want_closing}, separators=(",", ":"))))
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_three_entries(self):
        rows = [{"id": "a", "date": "2026-11-01", "amount": 500},
                {"id": "b", "date": "2026-11-04", "amount": -200},
                {"id": "c", "date": "2026-11-06", "amount": -100}]
        self.run_case(rows, ["a", "b", "c"],
                      {"a": 500, "b": 300, "c": 200}, 200)

    def test_the_date_order_wins_over_the_record_order(self):
        rows = [{"id": "late", "date": "2026-11-09", "amount": -100},
                {"id": "early", "date": "2026-11-01", "amount": 500}]
        self.run_case(rows, ["early", "late"],
                      {"early": 500, "late": 400}, 400)

    def test_the_same_date_breaks_on_id(self):
        rows = [{"id": "b", "date": "2026-11-01", "amount": 10},
                {"id": "a", "date": "2026-11-01", "amount": 5}]
        self.run_case(rows, ["a", "b"], {"a": 5, "b": 15}, 15)

    def test_a_missing_amount_leaves_the_balance(self):
        rows = [{"id": "a", "date": "2026-11-01", "amount": 500},
                {"id": "b", "date": "2026-11-02"}]
        self.run_case(rows, ["a", "b"], {"a": 500, "b": 500}, 500)

    def test_no_rows_is_zero(self):
        self.run_case([], [], {}, 0)


class TestFormulaApp(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_computes_bottles_times_rate(self):
        s = specmod.load(FORMULA, self.c)
        self.assertEqual("bottles * rate", s["compute"]["formula"])
        self.assertEqual(["bottles", "rate"], s["compute"]["inputs"])

    def test_a_formula_using_an_unknown_name_is_refused(self):
        s = specmod.load(FORMULA, self.c)
        s["compute"]["formula"] = "bottles * mystery"
        problems = specmod.validate(s, self.c, "formula-app.md")
        self.assertTrue(any("not inputs" in p for p in problems), problems)

    def test_a_text_input_is_refused(self):
        s = specmod.load(FORMULA, self.c)
        s["compute"]["inputs"] = ["title", "rate"]
        problems = specmod.validate(s, self.c, "formula-app.md")
        self.assertTrue(any("not numeric" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(FORMULA, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("evalFormula(MODEL.compute.formula", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestRegisterSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_runs_on_a_signed_amount(self):
        s = specmod.load(REGISTER, self.c)
        self.assertEqual("amount", s["running"]["field"])
        self.assertEqual("date", s["running"]["date"])

    def test_a_text_amount_is_refused(self):
        s = specmod.load(REGISTER, self.c)
        s["running"]["field"] = "title"
        problems = specmod.validate(s, self.c, "register.md")
        self.assertTrue(any("must be numeric" in p for p in problems), problems)

    def test_a_text_date_is_refused(self):
        s = specmod.load(REGISTER, self.c)
        s["running"]["date"] = "title"
        problems = specmod.validate(s, self.c, "register.md")
        self.assertTrue(any("must be a date" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(REGISTER, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function runningTotal(", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestStripFiguresAreInsideTheStrip(unittest.TestCase):
    """A strip figure written into the row loop renders nothing. This has happened
    three times in this project, so it is checked per archetype."""

    def setUp(self):
        self.c = cat.load()

    def strip_body(self, html: str) -> str:
        start = html.index("function renderStrip()")
        end = html.index("\nfunction render(", start)
        return html[start:end]

    def test_every_strip_figure_is_in_render_strip(self):
        for sample, needle in STRIP_FIGURES.items():
            with self.subTest(sample=sample):
                path = ROOT / "specs" / "gallery" / f"{sample}.md"
                if not path.exists():
                    self.skipTest(f"{sample}.md not present")
                with tempfile.TemporaryDirectory() as td:
                    out = Path(td) / "app"
                    verify.build_and_check(path, self.c, out)
                    html = (out / "index.html").read_text(encoding="utf-8")
                    self.assertIn(needle, self.strip_body(html),
                                  f"{sample}: its strip figure is not inside renderStrip")

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
