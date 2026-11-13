"""Tests for two archetypes: search-directory (a lookup) and comparison (a matrix)."""
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
DIR_SPEC = ROOT / "specs" / "gallery" / "search-directory.md"
CMP_SPEC = ROOT / "specs" / "gallery" / "comparison.md"


def run_js(src: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        return subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)


class TestColumnBest(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def case(self, rows, field, mode, want):
        src = extract.source("columnBest") + (
            "const got = columnBest(%s, %s, %s);\n"
            "if (got !== %s) { console.log('FAIL ' + got); process.exit(1); }\n"
            "console.log('PASS');\n"
            % (json.dumps(rows), json.dumps(field), json.dumps(mode), json.dumps(want)))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_max(self):
        self.case([{"n": 1}, {"n": 9}, {"n": 4}], "n", "max", 9)

    def test_min(self):
        self.case([{"n": 1}, {"n": 9}, {"n": 4}], "n", "min", 1)

    def test_missing_values_are_skipped(self):
        self.case([{"n": 5}, {}, {"n": None}, {"n": ""}], "n", "max", 5)

    def test_negative_numbers(self):
        self.case([{"n": -5}, {"n": -1}], "n", "max", -1)

    def test_no_usable_rows_is_null(self):
        self.case([{}], "n", "max", None)

    def test_a_string_number_is_coerced(self):
        self.case([{"n": "12"}, {"n": 3}], "n", "max", 12)


class TestDirectorySpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_is_search_first(self):
        s = specmod.load(DIR_SPEC, self.c)
        self.assertEqual("search-directory", s["pattern"])
        self.assertEqual("potency", s["directory"]["subtitle"])

    def test_a_directory_without_search_is_refused(self):
        s = specmod.load(DIR_SPEC, self.c)
        s["features"] = [f for f in s["features"] if f != "search"]
        problems = specmod.validate(s, self.c, "search-directory.md")
        self.assertTrue(any("'search' capability" in p for p in problems), problems)

    def test_a_directory_naming_a_missing_field_is_refused(self):
        s = specmod.load(DIR_SPEC, self.c)
        s["directory"] = {"subtitle": "nope"}
        problems = specmod.validate(s, self.c, "search-directory.md")
        self.assertTrue(any("not a field" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(DIR_SPEC, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function renderDirectory(", html)
            self.assertIn("function highlight(", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestComparisonSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_marks_a_min_price_and_a_max_rating(self):
        s = specmod.load(CMP_SPEC, self.c)
        self.assertEqual("min", s["comparison"]["highlight"]["price"])
        self.assertEqual("max", s["comparison"]["highlight"]["rating"])

    def test_one_column_is_refused(self):
        s = specmod.load(CMP_SPEC, self.c)
        s["comparison"]["columns"] = ["price"]
        problems = specmod.validate(s, self.c, "comparison.md")
        self.assertTrue(any("at least two fields" in p for p in problems), problems)

    def test_a_missing_column_is_refused(self):
        s = specmod.load(CMP_SPEC, self.c)
        s["comparison"]["columns"] = ["price", "nope"]
        problems = specmod.validate(s, self.c, "comparison.md")
        self.assertTrue(any("does not exist" in p for p in problems), problems)

    def test_an_unknown_direction_is_refused(self):
        s = specmod.load(CMP_SPEC, self.c)
        s["comparison"]["highlight"] = {"price": "best"}
        problems = specmod.validate(s, self.c, "comparison.md")
        self.assertTrue(any("max or min" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(CMP_SPEC, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function renderComparison(", html)
            self.assertIn("function columnBest(", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_a_comparison_carries_no_directory(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(CMP_SPEC, self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("function renderDirectory(", html)
            self.assertNotIn(".hit{background:", html)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
