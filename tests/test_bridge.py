"""Tests for the prompt bridge, the adopt repair engine and the browser studio."""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import adopt as adoptmod   # noqa: E402
from kiln import catalog as cat      # noqa: E402
from kiln import prompt as promptmod  # noqa: E402
from kiln import spec as specmod     # noqa: E402
from kiln import studio as studiomod  # noqa: E402
from kiln import verify              # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "reply-sloppy.md"


class TestPrompt(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_body_is_extracted_from_the_doc(self):
        body = promptmod.body()
        self.assertIn("KILN specification", body)
        self.assertIn("json kiln", body)
        self.assertNotIn("```markdown", body)

    def test_fill_substitutes_named_placeholders(self):
        out = promptmod.fill(APP_IDEA="a tea log", MUST_NOT="network calls")
        self.assertIn("a tea log", out)
        self.assertIn("network calls", out)
        self.assertNotIn("[[APP_IDEA]]", out)
        self.assertNotIn("[[MUST_NOT]]", out)

    def test_unfilled_lists_what_is_left(self):
        left = promptmod.unfilled(promptmod.body())
        self.assertIn("APP_IDEA", left)

    def test_prompt_lists_every_catalogue_feature(self):
        body = promptmod.body()
        for fid in self.c["features"]:
            self.assertIn(fid, body, f"{fid} missing from PROMPT.md")


class TestAdopt(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_sloppy_reply_becomes_a_valid_spec(self):
        with tempfile.TemporaryDirectory() as td:
            s, rep, dest = adoptmod.adopt(FIXTURE, self.c, outdir=td)
            self.assertTrue(dest.exists())
            self.assertGreater(len(rep), 10)
            loaded = specmod.load(dest, self.c)
            self.assertEqual(loaded["id"], s["id"])
            self.assertTrue(s["id"].startswith("app-tea"))

    def test_unknown_feature_is_dropped_not_passed_through(self):
        s, rep, _ = adoptmod.adopt(FIXTURE, self.c, write=False)
        self.assertNotIn("telepathy", s["features"])
        self.assertTrue(any("telepathy" in r for r in rep))

    def test_requires_are_closed_over(self):
        s, _, _ = adoptmod.adopt(FIXTURE, self.c, write=False)
        if "filters" in s["features"]:
            self.assertIn("search", s["features"])
            self.assertIn("crud", s["features"])

    def test_types_are_mapped(self):
        s, _, _ = adoptmod.adopt(FIXTURE, self.c, write=False)
        types = {f["name"]: f["type"] for f in s["entities"][0]["fields"]}
        self.assertEqual("text", types["name"])
        self.assertEqual("longtext", types["notes"])
        self.assertEqual("number", types["steep_time"])
        self.assertEqual("date", types["tried_on"])
        self.assertEqual("bool", types["would_rebuy"])
        self.assertEqual("select", types["strength"])

    def test_select_keeps_its_choices(self):
        s, _, _ = adoptmod.adopt(FIXTURE, self.c, write=False)
        strength = [f for f in s["entities"][0]["fields"] if f["name"] == "strength"][0]
        self.assertEqual(["light", "medium", "strong"], strength["options"])

    def test_vague_done_means_are_replaced(self):
        s, rep, _ = adoptmod.adopt(FIXTURE, self.c, write=False)
        for d in s["done_means"]:
            self.assertEqual([], specmod.lint_done_means([d]), d)
        self.assertTrue(any("unverifiable" in r for r in rep))

    def test_the_adopted_spec_builds_and_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, dest = adoptmod.adopt(FIXTURE, self.c, outdir=td)
            res = verify.build_and_check(dest, self.c, Path(td) / "app")
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])

    def test_adopting_its_own_output_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, dest = adoptmod.adopt(FIXTURE, self.c, outdir=td)
            s2, rep2, dest2 = adoptmod.adopt(dest, self.c, outdir=td)
            self.assertEqual([], rep2, rep2)
            self.assertEqual(dest.read_text(encoding="utf-8"),
                             dest2.read_text(encoding="utf-8"))

    def test_a_document_with_no_spec_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "junk.md"
            p.write_text("I cannot help with that request.", encoding="utf-8")
            with self.assertRaises(adoptmod.AdoptError):
                adoptmod.adopt(p, self.c, write=False)

    def test_trailing_commas_and_smart_quotes_are_survivable(self):
        text = ('here you go\n```json kiln\n{"name": \u201cQuote\u201d, "pitch": '
                '"an app that survives bad json", "features": ["crud",],}\n```\n')
        obj, span, rep = adoptmod.extract(text)
        self.assertEqual("Quote", obj["name"])
        self.assertTrue(any("smart quote" in r for r in rep))


class TestStudio(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_build_is_deterministic(self):
        self.assertEqual(studiomod.build(self.c), studiomod.build(self.c))

    def test_no_external_reference(self):
        html = studiomod.build(self.c)
        for bad in ("http://", "https://", "fetch(", "//cdn"):
            self.assertNotIn(bad, html)

    def test_carries_the_catalogue_and_the_runtime(self):
        html = studiomod.build(self.c)
        self.assertIn('"features"', html)
        self.assertIn("const TPL =", html)
        for fid in self.c["features"]:
            self.assertIn(fid, html)

    def test_the_runtime_template_survives_escaping(self):
        html = studiomod.build(self.c)
        m = re.search(r"const TPL = (\"(?:[^\"\\]|\\.)*\");", html, re.S)
        self.assertIsNotNone(m, "the runtime template is not a parseable JS string")
        tpl = json.loads(m.group(1))
        self.assertIn("{{TITLE}}", tpl)
        self.assertIn("</script>", tpl)

    def test_committed_studio_is_current(self):
        p = ROOT / "studio.html"
        self.assertTrue(p.exists(), "run: python3 -m kiln studio")
        self.assertEqual(studiomod.build(self.c), p.read_text(encoding="utf-8"),
                         "studio.html is stale: run python3 -m kiln studio")


if __name__ == "__main__":
    unittest.main()
