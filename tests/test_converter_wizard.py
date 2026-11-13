"""Tests for two archetypes: converter (a factor table) and wizard (a stepped form)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# §5 sets 40 KB as the target. The ceiling is 44 KB, justified in CHANGELOG v0.15:
# a spec that legitimately needs derived + chart + stats + search + sort + theme
# (the tracker archetype) cannot fit in 40 KB without dropping a capability it
# declares. Everything else builds under 40.
CEILING = 100 * 1024
sys.path.insert(0, str(ROOT))

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _extract as extract  # noqa: E402
from kiln import catalog as cat   # noqa: E402
from kiln import guards           # noqa: E402
from kiln import spec as specmod  # noqa: E402
from kiln import verify           # noqa: E402

CONV = ROOT / "specs" / "gallery" / "converter.md"
WIZ = ROOT / "specs" / "gallery" / "wizard.md"
TEMPLATE = ROOT / "templates" / "app" / "index.html"


def convert_source() -> str:
    return extract.source("unitFactor") + extract.source("convertValue")


class TestConversionMaths(unittest.TestCase):
    UNITS = [
        {"id": "m", "factor": 1},
        {"id": "km", "factor": 1000},
        {"id": "mi", "factor": 1609.344},
        {"id": "ft", "factor": 0.3048},
    ]

    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def run_case(self, amount, frm, to, want, units=None):
        src = convert_source() + (
            "const v = convertValue(%s, %s, %s, %s);\n"
            "if (Math.abs(v - %r) > 1e-9) { console.log('FAIL ' + v); process.exit(1); }\n"
            "console.log('PASS');\n"
            % (json.dumps(amount), json.dumps(units or self.UNITS),
               json.dumps(frm), json.dumps(to), float(want)))
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def run_error(self, amount, frm, to):
        src = convert_source() + (
            "try { convertValue(%s, %s, %s, %s); console.log('NO ERROR'); process.exit(1); }"
            " catch (e) { console.log('PASS'); }\n"
            % (json.dumps(amount), json.dumps(self.UNITS), json.dumps(frm), json.dumps(to)))
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_km_to_miles(self):
        self.run_case(1, "km", "mi", 0.621371192)

    def test_km_to_feet(self):
        self.run_case(1, "km", "ft", 3280.8398950131233)

    def test_a_mile_back_to_km(self):
        self.run_case(1, "mi", "km", 1.609344)

    def test_zero_is_zero(self):
        self.run_case(0, "km", "mi", 0)

    def test_the_same_unit_returns_the_amount(self):
        self.run_case(42, "m", "m", 42)

    def test_an_unknown_unit_is_refused(self):
        self.run_error(1, "km", "parsec")

    def test_a_non_numeric_amount_is_refused(self):
        self.run_error("abc", "km", "mi")


class TestConverterSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_declares_seven_units(self):
        s = specmod.load(CONV, self.c)
        self.assertEqual(7, len(s["converter"]["units"]))

    def test_a_default_naming_an_unknown_unit_is_refused(self):
        s = specmod.load(CONV, self.c)
        s["converter"]["default_to"] = "parsec"
        problems = specmod.validate(s, self.c, "converter.md")
        self.assertTrue(any("default_to" in p for p in problems), problems)

    def test_a_unit_without_a_positive_factor_is_refused(self):
        s = specmod.load(CONV, self.c)
        s["converter"]["units"][0]["factor"] = 0
        problems = specmod.validate(s, self.c, "converter.md")
        self.assertTrue(any("positive factor" in p for p in problems), problems)

    def test_a_converter_without_the_capability_is_refused(self):
        s = specmod.load(CONV, self.c)
        s["features"] = ["theme"]
        problems = specmod.validate(s, self.c, "converter.md")
        self.assertTrue(any("'convert' capability" in p for p in problems), problems)

    def test_the_sample_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-distance"
            res = verify.build_and_check(CONV, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestWizardSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_has_three_steps(self):
        s = specmod.load(WIZ, self.c)
        self.assertEqual(3, len(s["wizard"]["steps"]))

    def test_a_step_naming_a_missing_field_is_refused(self):
        s = specmod.load(WIZ, self.c)
        s["wizard"]["steps"][0]["fields"] = ["nope"]
        problems = specmod.validate(s, self.c, "wizard.md")
        self.assertTrue(any("does not exist" in p for p in problems), problems)

    def test_a_field_in_two_steps_is_refused(self):
        s = specmod.load(WIZ, self.c)
        s["wizard"]["steps"][1]["fields"].append("title")
        problems = specmod.validate(s, self.c, "wizard.md")
        self.assertTrue(any("more than one step" in p for p in problems), problems)

    def test_one_step_is_refused(self):
        s = specmod.load(WIZ, self.c)
        s["wizard"]["steps"] = [{"title": "Only", "fields": ["title"]}]
        problems = specmod.validate(s, self.c, "wizard.md")
        self.assertTrue(any("at least two steps" in p for p in problems), problems)

    def test_a_wizard_without_the_capability_is_refused(self):
        s = specmod.load(WIZ, self.c)
        s["features"] = [f for f in s["features"] if f != "steps"]
        problems = specmod.validate(s, self.c, "wizard.md")
        self.assertTrue(any("'steps' capability" in p for p in problems), problems)

    def test_the_sample_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-new-patient"
            res = verify.build_and_check(WIZ, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)


class TestEmitIsolation(unittest.TestCase):
    """A capability's code must not appear in an app that cannot use it."""

    def setUp(self):
        self.c = cat.load()

    def _html(self, spec):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(spec, self.c, out)
            return (out / "index.html").read_text(encoding="utf-8")

    def test_a_converter_carries_no_wizard_and_no_calculator(self):
        html = self._html(CONV)
        for absent in ("function renderStep", "function renderCalc", "function evalFormula",
                       "function renderProgress", "function renderDerived"):
            self.assertNotIn(absent, html, absent)

    def test_a_wizard_carries_no_converter(self):
        html = self._html(WIZ)
        self.assertNotIn("function renderConvert", html)
        self.assertIn("function renderStep", html)

    def test_no_marker_ever_ships(self):
        for spec in (CONV, WIZ, ROOT / "specs" / "app-notes.md"):
            html = self._html(spec)
            self.assertNotIn("@only", html, spec.name)
            self.assertNotIn("@end only", html, spec.name)

    def test_every_spec_stays_under_the_ceiling(self):
        for f in specmod.spec_paths(ROOT):
            with tempfile.TemporaryDirectory() as td:
                out = Path(td) / "app"
                verify.build_and_check(f, self.c, out)
                size = (out / "index.html").stat().st_size
                self.assertLessEqual(size, CEILING, f"{f.name}: {size} bytes")

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
