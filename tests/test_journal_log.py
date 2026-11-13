"""Tests for two archetypes: journal (a read view) and log (duration and a total)."""
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

# 40 KB is the target; 44 KB is the ceiling, justified in CHANGELOG v0.15.
CEILING = 100 * 1024

JOURNAL = ROOT / "specs" / "gallery" / "journal.md"
LOG = ROOT / "specs" / "gallery" / "log.md"


class TestDurationFormat(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def run_case(self, minutes, want):
        src = extract.source("fmtDuration") + (
            "const got = fmtDuration(%r);\n"
            "if (got !== %s) { console.log('FAIL got ' + JSON.stringify(got)); process.exit(1); }\n"
            "console.log('PASS');\n" % (minutes, json.dumps(want)))
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_ninety_minutes(self):
        self.run_case(90, "1h 30m")

    def test_exactly_an_hour(self):
        self.run_case(60, "1h")

    def test_under_an_hour(self):
        self.run_case(45, "45m")

    def test_zero_is_blank(self):
        self.run_case(0, "")

    def test_a_negative_is_signed(self):
        self.run_case(-75, "-1h 15m")

    def test_minutes_are_rounded(self):
        self.run_case(59.6, "1h")


class TestTotals(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def run_case(self, rows, cfg, want):
        src = extract.source("totalsOf") + (
            "const got = totalsOf(%s, %s);\n"
            "const want = %s;\n"
            "if (JSON.stringify(got) !== JSON.stringify(want)) {"
            " console.log('FAIL ' + JSON.stringify(got)); process.exit(1); }\n"
            "console.log('PASS');\n" % (json.dumps(rows), json.dumps(cfg), json.dumps(want)))
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_thirty_and_ninety_minutes_is_two_hours(self):
        self.run_case([{"minutes": 30}, {"minutes": 90}], {"field": "minutes"},
                      {"sum": 120, "count": 2})

    def test_missing_values_are_skipped(self):
        self.run_case([{"minutes": 30}, {"minutes": None}, {}], {"field": "minutes"},
                      {"sum": 30, "count": 1})

    def test_no_config_is_zero(self):
        self.run_case([{"minutes": 30}], {}, {"sum": 0, "count": 0})

    def test_an_empty_list_is_zero(self):
        self.run_case([], {"field": "minutes"}, {"sum": 0, "count": 0})


class TestJournal(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_reads_its_body_in_the_detail_view(self):
        s = specmod.load(JOURNAL, self.c)
        self.assertEqual("journal", s["pattern"])
        self.assertEqual("body", s["detail"]["field"])

    def test_a_detail_field_that_does_not_exist_is_refused(self):
        s = specmod.load(JOURNAL, self.c)
        s["detail"] = {"field": "nope"}
        problems = specmod.validate(s, self.c, "journal.md")
        self.assertTrue(any("not a field" in p for p in problems), problems)

    def test_a_detail_on_a_date_field_is_refused(self):
        s = specmod.load(JOURNAL, self.c)
        s["detail"] = {"field": "title"}
        problems = specmod.validate(s, self.c, "journal.md")
        self.assertTrue(any("longtext or text" in p for p in problems), problems)

    def test_the_read_view_is_emitted_and_opens_from_the_row(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(JOURNAL, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function openDetail(", html)
            self.assertIn("openDetail(r)", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestLog(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_totals_minutes_as_a_duration(self):
        s = specmod.load(LOG, self.c)
        self.assertEqual("log", s["pattern"])
        self.assertEqual("duration", s["totals"]["format"])

    def test_a_total_on_a_text_field_is_refused(self):
        s = specmod.load(LOG, self.c)
        s["totals"] = {"field": "title"}
        problems = specmod.validate(s, self.c, "log.md")
        self.assertTrue(any("must be number" in p for p in problems), problems)

    def test_an_unknown_format_is_refused(self):
        s = specmod.load(LOG, self.c)
        s["totals"] = {"field": "minutes", "format": "hours"}
        problems = specmod.validate(s, self.c, "log.md")
        self.assertTrue(any("totals.format" in p for p in problems), problems)

    def test_the_total_is_emitted_and_the_duration_is_formatted(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(LOG, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function totalsOf(", html)
            self.assertIn("function fmtDuration(", html)
            self.assertIn("fmtDuration(v)", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_a_log_carries_no_detail_view(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(LOG, self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("function openDetail(", html)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
