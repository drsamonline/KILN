"""Tests for voting (a tally) and grid (a crosstab)."""
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
VOTE = ROOT / "specs" / "gallery" / "voting.md"
GRID = ROOT / "specs" / "gallery" / "grid.md"


def run_js(src: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        return subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)


class TestTally(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def tally(self, rows):
        src = extract.source("tallyOf") + (
            "const t = tallyOf(%s, 'votes');\n"
            "console.log(JSON.stringify({total: t.total, max: t.max,"
            " shares: t.shares.map((s) => [s.id, s.count, s.pct, s.width, s.leading])}));\n"
            % json.dumps(rows))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stderr)
        return json.loads(p.stdout)

    def test_five_three_two_totals_ten(self):
        rows = [{"id": "a", "votes": 5}, {"id": "b", "votes": 3}, {"id": "c", "votes": 2}]
        t = self.tally(rows)
        self.assertEqual(10, t["total"])
        self.assertEqual(5, t["max"])
        self.assertEqual([["a", 5, 50, 100, True],
                          ["b", 3, 30, 60, False],
                          ["c", 2, 20, 40, False]], t["shares"])

    def test_a_tie_marks_every_leader(self):
        rows = [{"id": "a", "votes": 4}, {"id": "b", "votes": 4}]
        t = self.tally(rows)
        self.assertEqual([True, True], [s[4] for s in t["shares"]])

    def test_no_votes_at_all_is_zero_and_nobody_leads(self):
        rows = [{"id": "a", "votes": 0}, {"id": "b", "votes": 0}]
        t = self.tally(rows)
        self.assertEqual(0, t["total"])
        self.assertEqual([False, False], [s[4] for s in t["shares"]])

    def test_a_negative_count_is_not_a_vote(self):
        rows = [{"id": "a", "votes": 3}, {"id": "b", "votes": -2}]
        t = self.tally(rows)
        self.assertEqual(3, t["total"])
        self.assertEqual(0, t["shares"][1][1])

    def test_a_missing_count_is_zero(self):
        t = self.tally([{"id": "a", "votes": 2}, {"id": "b"}])
        self.assertEqual(2, t["total"])
        self.assertEqual(0, t["shares"][1][1])


class TestCrosstab(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def cross(self, rows):
        src = extract.source("crosstabOf") + (
            "const x = crosstabOf(%s, 'kind', 'month');\n"
            "console.log(JSON.stringify({rows: x.rowKeys, cols: x.colKeys,"
            " cells: x.cells, rt: x.rowTotals, ct: x.colTotals, grand: x.grand}));\n"
            % json.dumps(rows))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stderr)
        return json.loads(p.stdout)

    def test_two_by_two(self):
        rows = [{"kind": "first", "month": "2026-09"}, {"kind": "first", "month": "2026-10"},
                {"kind": "acute", "month": "2026-10"}, {"kind": "acute", "month": "2026-10"}]
        x = self.cross(rows)
        self.assertEqual(["acute", "first"], x["rows"])
        self.assertEqual(["2026-09", "2026-10"], x["cols"])
        self.assertEqual(1, x["cells"]["first\u00002026-09"])
        self.assertEqual(2, x["cells"]["acute\u00002026-10"])
        self.assertEqual(4, x["grand"])

    def test_the_edges_add_up(self):
        rows = [{"kind": "a", "month": "m1"}, {"kind": "b", "month": "m1"},
                {"kind": "b", "month": "m2"}]
        x = self.cross(rows)
        self.assertEqual({"a": 1, "b": 2}, x["rt"])
        self.assertEqual({"m1": 2, "m2": 1}, x["ct"])
        self.assertEqual(3, x["grand"])

    def test_an_empty_cell_is_absent_not_zero(self):
        rows = [{"kind": "a", "month": "m1"}]
        x = self.cross(rows)
        self.assertNotIn("a\u0000m2", x["cells"])

    def test_a_missing_dimension_is_its_own_key(self):
        x = self.cross([{"kind": "a"}, {"month": "m1"}])
        self.assertIn("", x["rows"])
        self.assertIn("", x["cols"])

    def test_no_rows_is_empty(self):
        x = self.cross([])
        self.assertEqual(0, x["grand"])
        self.assertEqual([], x["rows"])


class TestVotingSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_counts_a_number(self):
        s = specmod.load(VOTE, self.c)
        self.assertEqual("votes", s["tally"]["field"])

    def test_a_tally_on_a_text_field_is_refused(self):
        s = specmod.load(VOTE, self.c)
        s["tally"]["field"] = "title"
        problems = specmod.validate(s, self.c, "voting.md")
        self.assertTrue(any("number field" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(VOTE, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function tallyOf(", html)
            self.assertIn("· leading", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestGridSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_crosses_two_selects(self):
        s = specmod.load(GRID, self.c)
        self.assertEqual("kind", s["crosstab"]["row"])
        self.assertEqual("month", s["crosstab"]["column"])

    def test_the_same_field_twice_is_refused(self):
        s = specmod.load(GRID, self.c)
        s["crosstab"]["column"] = "kind"
        problems = specmod.validate(s, self.c, "grid.md")
        self.assertTrue(any("cannot be the same field" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(GRID, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function crosstabOf(", html)
            self.assertIn("rowTotals", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_a_grid_carries_no_tally_bar(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(GRID, self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("function tallyOf(", html)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
