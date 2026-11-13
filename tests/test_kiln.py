"""Tests for the compiler. Run: python3 -m unittest discover -s tests -v"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat          # noqa: E402
from kiln import compose, emit, guards, intent, spec as specmod, verify  # noqa: E402


class TestCatalog(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_features_and_kits(self):
        self.assertGreaterEqual(len(self.c["features"]), 10)
        for fid, f in self.c["features"].items():
            self.assertIn(f["kit"], self.c["kits"], f"{fid} names a missing kit")
            self.assertTrue(f["assertion"], f"{fid} has no assertion")

    def test_expand_closes_over_requires(self):
        got = cat.expand(["tags"], self.c)
        self.assertIn("crud", got)

    def test_unknown_feature_is_fatal(self):
        with self.assertRaises(cat.CatalogError):
            cat.expand(["telepathy"], self.c)

    def test_resolve_kits(self):
        kits = cat.resolve_kits(["crud", "search"], self.c)
        self.assertIn("web-kit", kits)
        self.assertIn("search-kit", kits)


class TestSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_every_spec_loads(self):
        specs = specmod.load_all(ROOT / "specs", self.c)
        self.assertEqual(len(specs), len(list((ROOT / "specs").glob("app-*.md"))))
        for s in specs:
            self.assertTrue(s["done_means"])

    def test_vague_done_means_is_rejected(self):
        bad = {"id": "app-x", "name": "X", "tier": 1, "category": "utility",
               "pitch": "A test app that exists.", "features": ["crud"],
               "entities": [{"name": "item", "label": "Item",
                             "fields": [{"name": "title", "label": "T", "type": "text"}]}],
               "storage": {"kind": "localstorage", "namespace": "x"},
               "done_means": ["it works as expected"], "not": ["network"]}
        problems = specmod.validate(bad, self.c, "app-x.md")
        self.assertTrue(any("certifies nothing" in p for p in problems), problems)

    def test_done_means_without_verb_is_rejected(self):
        bad = {"id": "app-x", "name": "X", "tier": 1, "category": "utility",
               "pitch": "A test app that exists.", "features": ["crud"],
               "entities": [{"name": "item", "label": "Item",
                             "fields": [{"name": "title", "label": "T", "type": "text"}]}],
               "storage": {"kind": "localstorage", "namespace": "x"},
               "done_means": ["a record is a thing that exists"], "not": ["network"]}
        problems = specmod.validate(bad, self.c, "app-x.md")
        self.assertTrue(any("observable outcome" in p for p in problems), problems)

    def test_missing_failure_path_is_rejected(self):
        s = specmod.load(ROOT / "specs" / "app-notes.md", self.c)
        s["features"] = ["crud", "nope"]
        problems = specmod.validate(s, self.c, "app-notes.md")
        self.assertTrue(any("not in catalog" in p for p in problems), problems)

    def test_filename_must_match_id(self):
        s = specmod.load(ROOT / "specs" / "app-notes.md", self.c)
        problems = specmod.validate(s, self.c, "app-other.md")
        self.assertTrue(any("does not match filename" in p for p in problems), problems)


class TestComposeEmit(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()
        self.spec = specmod.load(ROOT / "specs" / "app-notes.md", self.c)

    def test_plan_is_complete_and_stable(self):
        a = compose.plan(self.spec, self.c)
        b = compose.plan(self.spec, self.c)
        self.assertEqual([x["path"] for x in a], [x["path"] for x in b])
        # §1.3: one file by default
        self.assertEqual([x["path"] for x in a], ["index.html"])

    def test_with_docs_adds_the_furniture(self):
        plan = compose.plan(self.spec, self.c, with_docs=True)
        self.assertEqual(len(plan), 7)
        self.assertIn("app.json", [x["path"] for x in plan])

    def test_no_empty_file(self):
        with tempfile.TemporaryDirectory() as td:
            written = emit.write(compose.plan(self.spec, self.c), td)
            for path, size in written:
                self.assertGreater(size, 0, path)

    def test_unknown_template_variable_is_fatal(self):
        with self.assertRaises(emit.EmitError):
            emit.render("{{NOPE}}", {})


class TestBuildAndVerify(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_generated_app_is_complete(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-notes"
            res = verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out)
            self.assertEqual([], [(r["level"], r["name"], r["detail"]) for r in res.failed])
            self.assertEqual(["index.html"], sorted(p.name for p in out.iterdir()))

    def test_with_docs_emits_the_furniture(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-notes"
            res = verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out,
                                         with_docs=True)
            self.assertEqual([], res.failed)
            self.assertTrue((out / "tests" / "smoke.py").exists())

    def test_tampered_app_fails(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-notes"
            verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            (out / "index.html").write_text(
                html.replace("const MODEL =", "const NOT_MODEL ="), encoding="utf-8")
            res = verify.check_app(out, self.c)
            self.assertTrue(res.failed)

    def test_external_reference_fails(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-notes"
            verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            (out / "index.html").write_text(
                html.replace("</head>", '<link href="https://cdn.example/x.css">\n</head>'),
                encoding="utf-8")
            res = verify.check_app(out, self.c)
            self.assertTrue(any("external reference" in r["name"] for r in res.failed))

    def test_all_specs_build(self):
        for f in sorted((ROOT / "specs").glob("app-*.md")):
            with tempfile.TemporaryDirectory() as td:
                res = verify.build_and_check(f, self.c, td)
                self.assertEqual([], res.failed, f"{f.name}: {[r['name'] for r in res.failed]}")


class TestDeterminism(unittest.TestCase):
    """§1.1: the same spec produces byte-identical output, on any day, on any machine."""

    def setUp(self):
        self.c = cat.load()

    def test_two_builds_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a"
            b = Path(td) / "b"
            verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, a)
            verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, b)
            self.assertEqual((a / "index.html").read_bytes(), (b / "index.html").read_bytes())

    def test_no_build_date_in_the_output(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-notes"
            verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("{{", html)
            self.assertNotIn("built:", html)
            import datetime
            self.assertNotIn(datetime.date.today().isoformat(), html)

    def test_no_wall_clock_or_random_in_emitted_code(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-notes"
            verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            for bad in ("Date.now(", "Math.random(", "crypto.randomUUID"):
                self.assertNotIn(bad, html, f"{bad} reached the emitted code")

    def test_the_fingerprint_is_stable(self):
        s = specmod.load(ROOT / "specs" / "app-notes.md", self.c)
        one = compose.plan(s, self.c)[0]["ctx"]["FINGERPRINT"]
        two = compose.plan(s, self.c)[0]["ctx"]["FINGERPRINT"]
        self.assertEqual(one, two)


class TestGolden(unittest.TestCase):
    """L6: a build is compared with the one that was accepted."""

    def setUp(self):
        self.c = cat.load()

    def _build(self, td):
        out = Path(td) / "app-notes"
        verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out)
        return out

    def test_first_run_writes_a_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._build(td)
            res = verify.golden(out)
            self.assertEqual([], res.failed)
            self.assertTrue(verify.golden_path(out).exists())

    def test_an_unchanged_build_passes(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._build(td)
            verify.golden(out)
            self.assertEqual([], verify.golden(out).failed)

    def test_a_changed_file_fails(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._build(td)
            verify.golden(out)
            f = out / "index.html"
            f.write_text(f.read_text(encoding="utf-8") + "\n<!-- edited -->\n", encoding="utf-8")
            res = verify.golden(out)
            self.assertTrue(res.failed)
            self.assertTrue(any("no file changed" in r["name"] for r in res.failed))

    def test_a_removed_file_fails(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app-notes"
            verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out, with_docs=True)
            verify.golden(out)
            (out / "CHANGELOG.md").unlink()
            res = verify.golden(out)
            self.assertTrue(any("no file removed" in r["name"] for r in res.failed))

    def test_update_accepts_the_change(self):
        with tempfile.TemporaryDirectory() as td:
            out = self._build(td)
            verify.golden(out)
            (out / "index.html").write_text("changed", encoding="utf-8")
            self.assertTrue(verify.golden(out).failed)
            verify.golden(out, update=True)
            self.assertEqual([], verify.golden(out).failed)


class TestIntent(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_phrase_to_features(self):
        r = intent.parse("a notes app with tags, search and export", self.c)
        for f in ("crud", "search", "tags", "export"):
            self.assertIn(f, r["features"])
        self.assertGreater(r["confidence"], 0.3)

    def test_entity_and_fields(self):
        r = intent.parse("track visits with a due date and a rating", self.c)
        self.assertEqual("visit", r["entity"]["name"])
        types = {f["type"] for f in r["fields"]}
        self.assertIn("date", types)
        self.assertIn("number", types)

    def test_spec_from_phrase_is_valid(self):
        s = intent.to_spec("a notes app with tags and search", self.c)
        s.pop("_intent")
        self.assertEqual([], specmod.validate(s, self.c, "specs/app-note.md"))

    def test_deterministic(self):
        a = intent.parse("a reading log with tags", self.c)
        b = intent.parse("a reading log with tags", self.c)
        self.assertEqual(a, b)


class TestGuards(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_audit_references_resolve(self):
        rows = guards.check_audit_map()
        bad = [r for r in rows if not r.ok and not r.skip]
        self.assertEqual([], bad, [r.name for r in bad])

    def test_licence_consistent(self):
        rows = guards.check_licence(self.c)
        self.assertEqual([], [r for r in rows if not r.ok and not r.skip])

    def test_workflows_lint(self):
        rows = guards.check_workflows()
        self.assertEqual([], [r for r in rows if not r.ok and not r.skip],
                         [r.detail for r in rows])

    def test_index_is_current(self):
        rows = guards.check_index(self.c)
        self.assertEqual([], [r for r in rows if not r.ok and not r.skip],
                         "run: python3 -m kiln audit --write")


if __name__ == "__main__":
    unittest.main()
