"""Tests for the first relation: a lookup field and a master-detail view."""
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
SPEC = ROOT / "specs" / "gallery" / "master-detail.md"

MODEL_STUB = {
    "entities": [
        {"name": "patient", "label": "Patient",
         "fields": [{"name": "title", "type": "text"}]},
        {"name": "visit", "label": "Visit",
         "fields": [{"name": "title", "type": "text"},
                    {"name": "patient", "type": "lookup", "entity": "patient"}]},
    ]
}
DB_STUB = {
    "patient": [{"id": "p1", "title": "Meera Patel"},
                {"id": "p2", "title": "Arjun Shah"}],
    "visit": [{"id": "v1", "title": "First", "patient": "p1"},
              {"id": "v2", "title": "Follow-up", "patient": "p1"},
              {"id": "v3", "title": "Acute", "patient": "p2"},
              {"id": "v4", "title": "Orphan", "patient": ""}],
}


class TestPointer(unittest.TestCase):
    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def run_js(self, body):
        src = ("const MODEL = %s;\nconst DB = %s;\n"
               % (json.dumps(MODEL_STUB), json.dumps(DB_STUB)) +
               extract.source("titleFieldOf") + extract.source("labelOf") +
               extract.source("childrenOf") + body)
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            return subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_the_title_field_is_the_first_field(self):
        p = self.run_js('console.log(titleFieldOf("visit"));\n')
        self.assertEqual("title", p.stdout.strip())

    def test_an_id_resolves_to_a_title(self):
        p = self.run_js('console.log(labelOf("patient", "p1"));\n')
        self.assertEqual("Meera Patel", p.stdout.strip())

    def test_an_unknown_id_resolves_to_nothing(self):
        p = self.run_js('console.log(JSON.stringify(labelOf("patient", "nope")));\n')
        self.assertEqual('""', p.stdout.strip())

    def test_an_empty_id_resolves_to_nothing(self):
        p = self.run_js('console.log(JSON.stringify(labelOf("patient", "")));\n')
        self.assertEqual('""', p.stdout.strip())

    def test_children_are_only_the_matching_ones(self):
        p = self.run_js('console.log(childrenOf("visit", "patient", "p1").length);\n')
        self.assertEqual("2", p.stdout.strip())

    def test_a_parent_with_no_children_is_zero(self):
        p = self.run_js('console.log(childrenOf("visit", "patient", "p9").length);\n')
        self.assertEqual("0", p.stdout.strip())


class TestMasterDetailSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_the_sample_points_a_visit_at_a_patient(self):
        s = specmod.load(SPEC, self.c)
        self.assertEqual("patient", s["master_detail"]["master"])
        self.assertEqual("patient", s["master_detail"]["field"])

    def test_a_lookup_at_a_missing_entity_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["entities"][1]["fields"][1]["entity"] = "nope"
        problems = specmod.validate(s, self.c, "master-detail.md")
        self.assertTrue(any("points at an entity that does not exist" in p for p in problems),
                        problems)

    def test_a_lookup_at_its_own_entity_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["entities"][1]["fields"][1]["entity"] = "visit"
        problems = specmod.validate(s, self.c, "master-detail.md")
        self.assertTrue(any("points at its own entity" in p for p in problems), problems)

    def test_a_master_detail_field_that_is_not_a_lookup_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["master_detail"]["field"] = "title"
        problems = specmod.validate(s, self.c, "master-detail.md")
        self.assertTrue(any("must be a lookup" in p for p in problems), problems)

    def test_a_master_detail_whose_pointer_names_another_entity_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["master_detail"]["master"] = "visit"
        problems = specmod.validate(s, self.c, "master-detail.md")
        self.assertTrue(any("must point at the master" in p for p in problems), problems)

    def test_it_builds_to_one_file_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            res = verify.build_and_check(SPEC, self.c, out)
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (out / "index.html").read_text(encoding="utf-8")
            for needed in ('f.type === "lookup"', "function labelOf(", "function childrenOf("):
                self.assertIn(needed, html)
            self.assertLessEqual((out / "index.html").stat().st_size, CEILING)

    def test_a_single_entity_app_carries_no_pointer(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("function labelOf(", html)

    def test_the_pattern_guard_passes(self):
        bad = [r.name + " " + r.detail for r in guards.check_patterns(self.c)
               if not r.ok and not r.skip]
        self.assertEqual([], bad)


if __name__ == "__main__":
    unittest.main()
