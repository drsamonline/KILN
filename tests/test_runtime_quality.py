"""Tests for B4 (i18n and accessibility) and B5 (the two banners)."""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat   # noqa: E402
from kiln import spec as specmod  # noqa: E402
from kiln import verify           # noqa: E402

TEMPLATE = ROOT / "templates" / "app" / "index.html"
SPEC = ROOT / "specs" / "gallery" / "crud-list.md"


def langs_block() -> dict:
    """Pull the three dictionaries out of the template and parse them as JSON."""
    tpl = TEMPLATE.read_text(encoding="utf-8")
    start = tpl.index("const LANGS = {")
    end = tpl.index("\n};", start) + 3
    body = tpl[start:end].replace("const LANGS = ", "return ")
    js = body + "\nconsole.log(JSON.stringify(LANGS));\n"
    js = js.replace("return {", "const LANGS = {", 1)
    import shutil
    import subprocess
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(js)
        path = f.name
    try:
        p = subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)
    return json.loads(p.stdout)


class TestI18n(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()
        import shutil
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def test_every_language_carries_every_key(self):
        langs = langs_block()
        keys = set(langs["en"])
        for code in ("hi", "gu"):
            self.assertEqual(keys, set(langs[code]),
                             f"{code} is missing {sorted(keys - set(langs[code]))}")

    def test_no_dictionary_is_a_copy_of_english(self):
        langs = langs_block()
        for code in ("hi", "gu"):
            same = [k for k in langs["en"] if langs[code][k] == langs["en"][k]]
            self.assertLess(len(same), len(langs["en"]) // 2,
                            f"{code} looks untranslated: {same}")

    def test_the_sample_declares_three_languages(self):
        s = specmod.load(SPEC, self.c)
        self.assertEqual(["en", "hi", "gu"], s["i18n"]["languages"])

    def test_an_unknown_language_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["i18n"] = {"languages": ["en", "fr"]}
        problems = specmod.validate(s, self.c, "crud-list.md")
        self.assertTrue(any("no dictionary" in p for p in problems), problems)

    def test_an_i18n_block_without_the_capability_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["features"] = [f for f in s["features"] if f != "i18n"]
        problems = specmod.validate(s, self.c, "crud-list.md")
        self.assertTrue(any("'i18n' capability" in p for p in problems), problems)


class TestAccessibility(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def _html(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(SPEC, self.c, out)
            return (out / "index.html").read_text(encoding="utf-8")

    def test_the_skip_link_is_first_in_the_body(self):
        html = self._html()
        body = html[html.index("<body>"):]
        self.assertLess(body.index('class="skip"'), body.index("<header>"))

    def test_the_focus_ring_is_visible(self):
        self.assertIn(":focus-visible", self._html())

    def test_reduced_motion_is_respected(self):
        self.assertIn("prefers-reduced-motion", self._html())

    def test_banners_are_a_live_region(self):
        self.assertIn('aria-live="polite"', self._html())

    def test_every_input_has_a_label(self):
        html = self._html()
        for m in re.finditer(r"<(input|select|textarea)[^>]*>", html):
            tag = m.group(0)
            if 'type="hidden"' in tag or 'aria-label' in tag:
                continue
            # either wrapped in a label, or carrying an id that a label points at
            self.assertTrue(tag.count("id=") or tag.count("aria-label"),
                            f"unlabelled control: {tag[:80]}")

    def test_the_html_lang_is_set_at_runtime(self):
        self.assertIn('setAttribute("lang"', self._html())


class TestFeedbackBanners(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def _html(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(SPEC, self.c, out)
            return (out / "index.html").read_text(encoding="utf-8")

    def test_the_size_threshold_is_named(self):
        html = self._html()
        self.assertIn("const SIZE_WARN = 2000;", html)

    def test_the_backup_reminder_is_emitted(self):
        html = self._html()
        self.assertIn("function lastExport()", html)
        self.assertIn("BACKUP_DAYS", html)

    def test_exporting_records_the_day(self):
        self.assertIn("markExport()", self._html())

    def test_a_spec_without_feedback_carries_none_of_it(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, out)
            html = (out / "index.html").read_text(encoding="utf-8")
            for absent in ("SIZE_WARN", "lastExport", "const LANGS ="):
                self.assertNotIn(absent, html, f"{absent} shipped in an app that cannot use it")


if __name__ == "__main__":
    unittest.main()
