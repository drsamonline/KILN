"""Tests for two archetypes: kanban (a board) and calendar (a month grid)."""
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
BOARD = ROOT / "specs" / "gallery" / "kanban.md"
CAL = ROOT / "specs" / "gallery" / "calendar.md"


def run_js(src: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        return subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)


class TestGroupBy(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def case(self, rows, cols, want):
        src = extract.source("groupBy") + (
            "const got = groupBy(%s, 'stage', %s);\n"
            "const shape = got.map((c) => [c.key, c.items.length]);\n"
            "if (JSON.stringify(shape) !== JSON.stringify(%s)) {"
            " console.log('FAIL ' + JSON.stringify(shape)); process.exit(1); }\n"
            "console.log('PASS');\n" % (json.dumps(rows), json.dumps(cols),
                                        json.dumps(want, separators=(",", ":"))))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_two_stages_with_two_and_one(self):
        rows = [{"stage": "new"}, {"stage": "new"}, {"stage": "done"}]
        self.case(rows, ["new", "done"], [["new", 2], ["done", 1]])

    def test_every_column_appears_even_when_empty(self):
        self.case([{"stage": "new"}], ["new", "done"], [["new", 1], ["done", 0]])

    def test_a_value_outside_the_columns_lands_in_unplaced(self):
        rows = [{"stage": "new"}, {"stage": "archived"}]
        self.case(rows, ["new", "done"], [["new", 1], ["done", 0], ["", 1]])

    def test_a_missing_stage_lands_in_unplaced(self):
        self.case([{}], ["new", "done"], [["new", 0], ["done", 0], ["", 1]])

    def test_no_rows_means_empty_columns(self):
        self.case([], ["new", "done"], [["new", 0], ["done", 0]])


class TestMonthGrid(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def grid(self, ym):
        src = extract.source("monthGrid") + (
            "const g = monthGrid(%s);\n"
            "console.log(JSON.stringify(g));\n" % json.dumps(ym))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stderr)
        return json.loads(p.stdout)

    def test_six_rows_of_seven(self):
        self.assertEqual(42, len(self.grid("2026-11")))

    def test_starts_on_a_monday(self):
        g = self.grid("2026-11")
        # 2026-11-01 is a Sunday, so the first cell is 2026-10-26
        self.assertEqual("2026-10-26", g[0]["date"])

    def test_the_month_starts_where_it_should(self):
        g = self.grid("2026-11")
        firsts = [c for c in g if c["date"].startswith("2026-11")]
        self.assertEqual("2026-11-01", firsts[0]["date"])
        self.assertEqual(30, len(firsts))

    def test_the_thirteenth_is_in_the_month(self):
        g = self.grid("2026-11")
        self.assertIn("2026-11-13", [c["date"] for c in g if c["inMonth"]])

    def test_days_outside_the_month_are_marked(self):
        g = self.grid("2026-11")
        self.assertTrue(any(not c["inMonth"] for c in g))
        self.assertTrue(any(c["inMonth"] for c in g))

    def test_a_leap_february(self):
        g = self.grid("2028-02")
        self.assertEqual(29, len([c for c in g if c["inMonth"]]))

    def test_add_months_crosses_a_year(self):
        src = extract.source("addMonths") + (
            "console.log(addMonths('2026-12', 1) + ' ' + addMonths('2026-01', -1));\n")
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stderr)
        self.assertEqual("2027-01 2025-12", p.stdout.strip())


class TestBoardSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_boards_on_a_select_field(self):
        s = specmod.load(BOARD, self.c)
        self.assertEqual("kanban", s["pattern"])
        self.assertEqual("stage", s["board"]["field"])

    def test_a_board_on_a_text_field_is_refused(self):
        s = specmod.load(BOARD, self.c)
        s["board"] = {"field": "title"}
        problems = specmod.validate(s, self.c, "kanban.md")
        self.assertTrue(any("must be a select" in p for p in problems), problems)

    def test_a_board_without_the_capability_is_refused(self):
        s = specmod.load(BOARD, self.c)
        s["features"] = [f for f in s["features"] if f != "board"]
        problems = specmod.validate(s, self.c, "kanban.md")
        self.assertTrue(any("'board' capability" in p for p in problems), problems)

    def test_the_sample_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(BOARD, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function renderBoard(", html)
            self.assertIn("#board{display:none", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestCalendarSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_calendars_on_a_date_field(self):
        s = specmod.load(CAL, self.c)
        self.assertEqual("calendar", s["pattern"])
        self.assertEqual("date", s["calendar"]["field"])

    def test_a_calendar_on_a_text_field_is_refused(self):
        s = specmod.load(CAL, self.c)
        s["calendar"] = {"field": "title"}
        problems = specmod.validate(s, self.c, "calendar.md")
        self.assertTrue(any("must be a date" in p for p in problems), problems)

    def test_the_sample_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(CAL, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function renderCalendar(", html)
            self.assertIn(".grid7{display:grid", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_a_calendar_carries_no_board(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(CAL, self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("function renderBoard(", html)
            self.assertNotIn(".col{flex:", html)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
