"""Tests for report (a grouped summary) and decision-log (a choice and a reason)."""
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
REPORT = ROOT / "specs" / "gallery" / "report.md"
DECIDE = ROOT / "specs" / "gallery" / "decision-log.md"


def run_js(src: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        return subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)


class TestSummarise(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def groups(self, rows, group, total):
        src = extract.source("summarise") + (
            "const g = summarise(%s, %s, %s);\n"
            "console.log(JSON.stringify(g.map((x) => [x.key, x.count, x.sum])));\n"
            % (json.dumps(rows), json.dumps(group), json.dumps(total)))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stderr)
        return json.loads(p.stdout)

    def test_two_kinds_with_counts_and_sums(self):
        rows = [{"kind": "first", "fee": 1500}, {"kind": "first", "fee": 1500},
                {"kind": "acute", "fee": 400}]
        self.assertEqual([["first", 2, 3000], ["acute", 1, 400]],
                         self.groups(rows, "kind", "fee"))

    def test_the_bigger_sum_comes_first(self):
        rows = [{"kind": "a", "fee": 10}, {"kind": "b", "fee": 99}]
        self.assertEqual([["b", 1, 99], ["a", 1, 10]], self.groups(rows, "kind", "fee"))

    def test_a_tie_breaks_on_the_count(self):
        rows = [{"kind": "a", "fee": 10}, {"kind": "b", "fee": 10},
                {"kind": "b", "fee": 0}]
        self.assertEqual([["b", 2, 10], ["a", 1, 10]], self.groups(rows, "kind", "fee"))

    def test_a_missing_group_is_its_own_row(self):
        rows = [{"kind": "a", "fee": 5}, {"fee": 5}]
        self.assertEqual([["", 1, 5], ["a", 1, 5]], self.groups(rows, "kind", "fee"))

    def test_no_sum_field_still_counts(self):
        rows = [{"kind": "a"}, {"kind": "a"}, {"kind": "b"}]
        self.assertEqual([["a", 2, 0], ["b", 1, 0]], self.groups(rows, "kind", None))

    def test_no_rows_is_no_groups(self):
        self.assertEqual([], self.groups([], "kind", "fee"))


class TestReportSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_groups_on_a_select_and_sums_a_fee(self):
        s = specmod.load(REPORT, self.c)
        self.assertEqual("kind", s["report"]["group"])
        self.assertEqual("fee", s["report"]["sum"])

    def test_a_group_on_a_date_field_is_refused(self):
        s = specmod.load(REPORT, self.c)
        s["report"]["group"] = "date"
        problems = specmod.validate(s, self.c, "report.md")
        self.assertTrue(any("select, text or tags" in p for p in problems), problems)

    def test_a_sum_on_a_text_field_is_refused(self):
        s = specmod.load(REPORT, self.c)
        s["report"]["sum"] = "title"
        problems = specmod.validate(s, self.c, "report.md")
        self.assertTrue(any("must be numeric" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(REPORT, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function summarise(", html)
            self.assertIn('className = "grand"', html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestDecideSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_names_its_choice_and_reason(self):
        s = specmod.load(DECIDE, self.c)
        self.assertEqual("choice", s["decide"]["choice"])
        self.assertEqual("why", s["decide"]["why"])

    def test_a_choice_on_a_tags_field_is_refused(self):
        s = specmod.load(DECIDE, self.c)
        s["decide"]["choice"] = "options"
        problems = specmod.validate(s, self.c, "decision-log.md")
        self.assertTrue(any("text or select" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(DECIDE, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("chose ", html)
            self.assertIn("still open", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_a_decision_log_carries_no_summary_table(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(DECIDE, self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("function summarise(", html)
            self.assertNotIn('id="report"', html)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
