"""Tests for scheduler (recurring dates) and playlist (an explicit order)."""
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
SCHED = ROOT / "specs" / "gallery" / "scheduler.md"
PLAY = ROOT / "specs" / "gallery" / "playlist.md"


def run_js(src: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        return subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)


class TestNextDue(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def case(self, last, every, want):
        src = (extract.source("addDays") + extract.source("nextDue") +
               "const got = nextDue(%s, %s);\n"
               "if (got !== %s) { console.log('FAIL ' + got); process.exit(1); }\n"
               "console.log('PASS');\n"
               % (json.dumps(last), json.dumps(every), json.dumps(want)))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_thirty_days_from_november_first(self):
        self.case("2026-11-01", 30, "2026-12-01")

    def test_across_a_year_end(self):
        self.case("2026-12-20", 30, "2027-01-19")

    def test_a_leap_day(self):
        self.case("2028-02-01", 29, "2028-03-01")

    def test_no_interval_is_no_date(self):
        self.case("2026-11-01", 0, "")

    def test_a_missing_date_is_no_date(self):
        self.case("", 30, "")

    def test_a_malformed_date_is_no_date(self):
        self.case("sometime", 30, "")


class TestSequence(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def order(self, rows):
        src = extract.source("sequenceOf") + (
            "const g = sequenceOf(%s, 'position');\n"
            "console.log(JSON.stringify(g.map((r) => r.id)));\n" % json.dumps(rows))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stderr)
        return json.loads(p.stdout)

    def test_the_order_field_wins_over_the_record_order(self):
        rows = [{"id": "a", "position": 3}, {"id": "b", "position": 1},
                {"id": "c", "position": 2}]
        self.assertEqual(["b", "c", "a"], self.order(rows))

    def test_a_missing_position_goes_last(self):
        rows = [{"id": "a", "position": 2}, {"id": "b"}, {"id": "c", "position": 1}]
        self.assertEqual(["c", "a", "b"], self.order(rows))

    def test_a_tie_is_broken_by_id_so_it_is_stable(self):
        rows = [{"id": "b", "position": 1}, {"id": "a", "position": 1}]
        self.assertEqual(["a", "b"], self.order(rows))

    def test_the_input_is_not_mutated(self):
        src = extract.source("sequenceOf") + (
            "const rows = [{id:'a',position:2},{id:'b',position:1}];\n"
            "sequenceOf(rows, 'position');\n"
            "console.log(rows[0].id);\n")
        p = run_js(src)
        self.assertEqual("a", p.stdout.strip())


class TestSchedulerSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_recurs_on_a_date_and_a_number(self):
        s = specmod.load(SCHED, self.c)
        self.assertEqual("last", s["recur"]["last"])
        self.assertEqual("every", s["recur"]["every"])

    def test_a_text_last_date_is_refused(self):
        s = specmod.load(SCHED, self.c)
        s["recur"]["last"] = "title"
        problems = specmod.validate(s, self.c, "scheduler.md")
        self.assertTrue(any("must be a date" in p for p in problems), problems)

    def test_a_text_interval_is_refused(self):
        s = specmod.load(SCHED, self.c)
        s["recur"]["every"] = "title"
        problems = specmod.validate(s, self.c, "scheduler.md")
        self.assertTrue(any("must be a number" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(SCHED, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function nextDue(", html)
            self.assertIn("due since ", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestPlaylistSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_orders_on_a_number(self):
        s = specmod.load(PLAY, self.c)
        self.assertEqual("position", s["sequence"]["order"])

    def test_a_text_order_field_is_refused(self):
        s = specmod.load(PLAY, self.c)
        s["sequence"]["order"] = "title"
        problems = specmod.validate(s, self.c, "playlist.md")
        self.assertTrue(any("must be a number" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(PLAY, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function sequenceOf(", html)
            self.assertIn("fmtDuration(run)", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_a_playlist_carries_no_recurrence(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(PLAY, self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("function nextDue(", html)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
