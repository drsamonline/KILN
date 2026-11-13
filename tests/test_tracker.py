"""Tests for the tracker archetype: the derived maths, and the built app.

The maths lives in the emitted JavaScript, so it is tested by running that
JavaScript under node. If node is absent the maths test reports SKIP rather than
passing quietly — the same rule the guards follow.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 40 KB is the target; 44 KB is the ceiling, justified in CHANGELOG v0.15 —
# the tracker archetype needs derived + chart + stats + search + sort + theme.
CEILING = 44 * 1024
sys.path.insert(0, str(ROOT))

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _extract as extract  # noqa: E402
from kiln import catalog as cat   # noqa: E402
from kiln import guards           # noqa: E402
from kiln import spec as specmod  # noqa: E402
from kiln import verify           # noqa: E402

SPEC = ROOT / "specs" / "gallery" / "tracker.md"
TEMPLATE = ROOT / "templates" / "app" / "index.html"

HARNESS = r"""
const rows = %s;
const tracker = %s;
const got = derive(rows, tracker, %s);
const want = %s;
const fail = [];
for (const k of Object.keys(want)) {
  const a = got[k], b = want[k];
  const same = (typeof b === "number") ? Math.abs(a - b) < 1e-9 : JSON.stringify(a) === JSON.stringify(b);
  if (!same) fail.push(k + ": got " + JSON.stringify(a) + " want " + JSON.stringify(b));
}
if (fail.length) { console.log("FAIL " + fail.join(" | ")); process.exit(1); }
console.log("PASS");
"""


def derive_source() -> str:
    """The pure derivation, plus the two helpers it calls."""
    return (extract.source("dayISO") + extract.source("shiftDay") +
            extract.source("derive"))


class TestDerivedMaths(unittest.TestCase):
    """Run the emitted derivation under node, on fixtures with known answers."""

    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def run_case(self, rows, tracker, today, want):
        src = derive_source() + (HARNESS % (json.dumps(rows), json.dumps(tracker),
                                            json.dumps(today), json.dumps(want)))
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, (p.stdout or "") + (p.stderr or ""))

    def test_three_consecutive_days_is_a_streak_of_three(self):
        rows = [{"date": "2026-11-11", "litres": 2},
                {"date": "2026-11-12", "litres": 2},
                {"date": "2026-11-13", "litres": 2}]
        self.run_case(rows, {"field": "litres", "goal": 2, "window": 7},
                      "2026-11-13", {"streak": 3, "days": 3})

    def test_a_missing_day_breaks_the_streak(self):
        rows = [{"date": "2026-11-13", "litres": 2},
                {"date": "2026-11-11", "litres": 2}]
        self.run_case(rows, {"field": "litres", "goal": 2, "window": 7},
                      "2026-11-13", {"streak": 1})

    def test_a_streak_ending_yesterday_still_counts(self):
        rows = [{"date": "2026-11-12", "litres": 2},
                {"date": "2026-11-11", "litres": 2}]
        self.run_case(rows, {"field": "litres", "goal": 2, "window": 7},
                      "2026-11-13", {"streak": 2})

    def test_a_streak_older_than_yesterday_does_not_count(self):
        rows = [{"date": "2026-11-10", "litres": 2}]
        self.run_case(rows, {"field": "litres", "goal": 2, "window": 7},
                      "2026-11-13", {"streak": 0})

    def test_the_average_divides_by_logged_days(self):
        rows = [{"date": "2026-11-13", "litres": 1},
                {"date": "2026-11-12", "litres": 3}]
        self.run_case(rows, {"field": "litres", "goal": 2, "window": 7},
                      "2026-11-13", {"avg": 2, "sum": 4, "days": 2})

    def test_half_the_goal_over_the_window_is_fifty_percent(self):
        rows = [{"date": "2026-11-13", "litres": 7}]
        self.run_case(rows, {"field": "litres", "goal": 2, "window": 7},
                      "2026-11-13", {"goalPct": 50})

    def test_the_sparkline_has_one_point_per_day_in_the_window(self):
        rows = [{"date": "2026-11-13", "litres": 2}]
        self.run_case(rows, {"field": "litres", "goal": 2, "window": 7},
                      "2026-11-13", {"window": 7})
        src = derive_source() + """
const got = derive([{date:"2026-11-13",litres:2}], {field:"litres",goal:2,window:7}, "2026-11-13");
if (got.spark.length !== 7) { console.log("FAIL spark " + got.spark.length); process.exit(1); }
if (got.spark[6].v !== 2) { console.log("FAIL last point"); process.exit(1); }
console.log("PASS");
"""
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_no_rows_is_all_zeros(self):
        self.run_case([], {"field": "litres", "goal": 2, "window": 7},
                      "2026-11-13", {"streak": 0, "days": 0, "sum": 0, "avg": 0, "goalPct": 0})


class TestTrackerSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_loads_and_declares_a_tracker(self):
        s = specmod.load(SPEC, self.c)
        self.assertEqual("tracker", s["pattern"])
        self.assertEqual("litres", s["tracker"]["field"])

    def test_a_tracker_pointing_at_a_missing_field_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["tracker"] = {"field": "nope", "goal": 1}
        problems = specmod.validate(s, self.c, "tracker.md")
        self.assertTrue(any("not a field" in p for p in problems), problems)

    def test_a_tracker_pointing_at_a_text_field_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["tracker"] = {"field": "note", "goal": 1}
        problems = specmod.validate(s, self.c, "tracker.md")
        self.assertTrue(any("must be number" in p for p in problems), problems)

    def test_a_zero_goal_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["tracker"] = {"field": "litres", "goal": 0}
        problems = specmod.validate(s, self.c, "tracker.md")
        self.assertTrue(any("greater than zero" in p for p in problems), problems)

    def test_the_sample_satisfies_the_pattern(self):
        s = specmod.load(SPEC, self.c)
        res = verify.check_pattern(s, self.c)
        self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])

    def test_the_sample_builds_to_one_file_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-water-log"
            res = verify.build_and_check(SPEC, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            self.assertEqual(["index.html"], sorted(p.name for p in out.iterdir()))
            size = (out / "index.html").stat().st_size
            self.assertLessEqual(size, CEILING, f"{size} bytes exceeds the ceiling")

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
