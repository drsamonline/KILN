"""Tests for the checklist archetype: the progress maths, and the built app.

The maths lives in the emitted JavaScript, so it is run there, under node.
"""
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
import _extract as extract  # noqa: E402
from kiln import catalog as cat   # noqa: E402
from kiln import guards           # noqa: E402
from kiln import spec as specmod  # noqa: E402
from kiln import verify           # noqa: E402

SPEC = ROOT / "specs" / "gallery" / "checklist.md"
TEMPLATE = ROOT / "templates" / "app" / "index.html"

HARNESS = r"""
const got = progressOf(%s, %s);
const want = %s;
const fail = [];
for (const k of Object.keys(want)) {
  if (got[k] !== want[k]) fail.push(k + ": got " + JSON.stringify(got[k]) +
    " want " + JSON.stringify(want[k]));
}
if (fail.length) { console.log("FAIL " + fail.join(" | ")); process.exit(1); }
console.log("PASS");
"""


def progress_source() -> str:
    return extract.source("progressOf")


class TestProgressMaths(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def run_case(self, rows, cfg, want):
        src = progress_source() + (HARNESS % (json.dumps(rows), json.dumps(cfg),
                                              json.dumps(want)))
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, (p.stdout or "") + (p.stderr or ""))

    def test_two_of_four_is_fifty_percent(self):
        rows = [{"done": True}, {"done": True}, {"done": False}, {"done": False}]
        self.run_case(rows, {"field": "done"},
                      {"done": 2, "total": 4, "left": 2, "pct": 50})

    def test_all_done_is_one_hundred(self):
        rows = [{"done": True}, {"done": True}]
        self.run_case(rows, {"field": "done"}, {"done": 2, "left": 0, "pct": 100})

    def test_none_done_is_zero(self):
        rows = [{"done": False}, {"done": False}]
        self.run_case(rows, {"field": "done"}, {"done": 0, "left": 2, "pct": 0})

    def test_an_empty_list_does_not_divide_by_zero(self):
        self.run_case([], {"field": "done"}, {"done": 0, "total": 0, "pct": 0})

    def test_rows_without_the_field_are_not_counted(self):
        rows = [{"done": True}, {"title": "no bool"}, {"done": False}]
        self.run_case(rows, {"field": "done"}, {"total": 2, "done": 1, "pct": 50})

    def test_the_string_true_counts_as_done(self):
        rows = [{"done": "true"}, {"done": False}]
        self.run_case(rows, {"field": "done"}, {"done": 1, "pct": 50})

    def test_no_config_is_all_zeros(self):
        self.run_case([{"done": True}], {}, {"done": 0, "total": 0, "pct": 0})

    def test_rounding_is_to_the_nearest_whole_percent(self):
        rows = [{"done": True}, {"done": False}, {"done": False}]
        self.run_case(rows, {"field": "done"}, {"pct": 33})


class TestChecklistSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_loads_and_declares_progress(self):
        s = specmod.load(SPEC, self.c)
        self.assertEqual("checklist", s["pattern"])
        self.assertEqual("done", s["progress"]["field"])

    def test_progress_pointing_at_a_missing_field_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["progress"] = {"field": "nope"}
        problems = specmod.validate(s, self.c, "checklist.md")
        self.assertTrue(any("not a field" in p for p in problems), problems)

    def test_progress_pointing_at_a_text_field_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["progress"] = {"field": "title"}
        problems = specmod.validate(s, self.c, "checklist.md")
        self.assertTrue(any("must be a bool" in p for p in problems), problems)

    def test_the_sample_satisfies_the_pattern(self):
        s = specmod.load(SPEC, self.c)
        res = verify.check_pattern(s, self.c)
        self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])

    def test_the_sample_builds_to_one_file_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-clinic-opening"
            res = verify.build_and_check(SPEC, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            self.assertEqual(["index.html"], sorted(p.name for p in out.iterdir()))
            size = (out / "index.html").stat().st_size
            self.assertLessEqual(size, 40 * 1024, f"{size} bytes exceeds the 40 KB ceiling")

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
