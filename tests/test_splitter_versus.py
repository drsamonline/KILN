"""Tests for splitter (apportionment) and comparison-of-records (two records)."""
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
SPLIT = ROOT / "specs" / "gallery" / "splitter.md"
VERSUS = ROOT / "specs" / "gallery" / "comparison-of-records.md"


def run_js(src: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        return subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)


class TestSplit(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def shares(self, rows, total):
        src = extract.source("splitOf") + (
            "const p = splitOf(%s, 'w', %s);\n"
            "console.log(JSON.stringify(p.map((x) => x.share)));\n"
            % (json.dumps(rows), json.dumps(total)))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stderr)
        return json.loads(p.stdout)

    def test_three_equal_shares_of_one_hundred(self):
        rows = [{"id": "a", "w": 1}, {"id": "b", "w": 1}, {"id": "c", "w": 1}]
        self.assertEqual([34, 33, 33], self.shares(rows, 100))

    def test_the_parts_always_add_up(self):
        for total in (1, 7, 100, 999, 10000):
            for weights in ([1, 1, 1], [3, 2, 2, 1], [1, 2, 3, 4, 5], [7, 7, 7]):
                rows = [{"id": str(i), "w": w} for i, w in enumerate(weights)]
                with self.subTest(total=total, weights=weights):
                    self.assertEqual(total, sum(self.shares(rows, total)))

    def test_a_zero_weight_gets_nothing(self):
        rows = [{"id": "a", "w": 3}, {"id": "b", "w": 0}]
        self.assertEqual([100, 0], self.shares(rows, 100))

    def test_no_weight_at_all_splits_nothing(self):
        rows = [{"id": "a", "w": 0}, {"id": "b", "w": 0}]
        self.assertEqual([0, 0], self.shares(rows, 100))

    def test_a_negative_weight_is_treated_as_zero(self):
        rows = [{"id": "a", "w": 2}, {"id": "b", "w": -5}]
        self.assertEqual([100, 0], self.shares(rows, 100))

    def test_the_largest_remainder_goes_first(self):
        rows = [{"id": "a", "w": 1}, {"id": "b", "w": 2}]
        self.assertEqual([33, 67], self.shares(rows, 100))


class TestComparePair(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def rows(self, a, b, fields, directions):
        src = extract.source("comparePair") + (
            "const r = comparePair(%s, %s, %s, %s);\n"
            "console.log(JSON.stringify(r.map((x) => [x.field, x.same, x.better])));\n"
            % (json.dumps(a), json.dumps(b), json.dumps(fields), json.dumps(directions)))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stderr)
        return json.loads(p.stdout)

    def test_a_cheaper_price_is_marked(self):
        out = self.rows({"price": 4200}, {"price": 3500}, ["price"], {"price": "lower"})
        self.assertEqual([["price", False, "b"]], out)

    def test_a_higher_rating_is_marked(self):
        out = self.rows({"rating": 4}, {"rating": 5}, ["rating"], {"rating": "higher"})
        self.assertEqual([["rating", False, "b"]], out)

    def test_nothing_is_marked_without_a_stated_direction(self):
        out = self.rows({"rating": 4}, {"rating": 5}, ["rating"], {})
        self.assertEqual([["rating", False, None]], out)

    def test_an_equal_value_is_same_and_unmarked(self):
        out = self.rows({"potency": "30C"}, {"potency": "30C"}, ["potency"],
                        {"potency": "lower"})
        self.assertEqual([["potency", True, None]], out)

    def test_text_is_never_marked_even_with_a_direction(self):
        out = self.rows({"potency": "30C"}, {"potency": "200C"}, ["potency"],
                        {"potency": "lower"})
        self.assertEqual([["potency", False, None]], out)


class TestSplitterSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_splits_a_total_by_a_weight(self):
        s = specmod.load(SPLIT, self.c)
        self.assertEqual("weight", s["split"]["weight"])
        self.assertEqual(10000, s["split"]["total"])

    def test_a_zero_total_is_refused(self):
        s = specmod.load(SPLIT, self.c)
        s["split"]["total"] = 0
        problems = specmod.validate(s, self.c, "splitter.md")
        self.assertTrue(any("positive integer" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(SPLIT, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function splitOf(", html)
            self.assertIn("left -= 1", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestVersusSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_states_a_direction_per_field(self):
        s = specmod.load(VERSUS, self.c)
        self.assertEqual("lower", s["versus"]["better"]["price"])
        self.assertEqual("higher", s["versus"]["better"]["rating"])

    def test_a_direction_on_a_field_not_compared_is_refused(self):
        s = specmod.load(VERSUS, self.c)
        s["versus"]["better"]["body"] = "lower"
        problems = specmod.validate(s, self.c, "comparison-of-records.md")
        self.assertTrue(any("not in versus.fields" in p for p in problems), problems)

    def test_an_unknown_direction_is_refused(self):
        s = specmod.load(VERSUS, self.c)
        s["versus"]["better"]["price"] = "cheaper"
        problems = specmod.validate(s, self.c, "comparison-of-records.md")
        self.assertTrue(any("lower or higher" in p for p in problems), problems)

    def test_it_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(VERSUS, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function comparePair(", html)
            self.assertIn("MODEL.versus.better", html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
