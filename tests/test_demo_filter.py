"""The demo gallery must be searchable, and its filter must be honest."""
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

from kiln import catalog as cat   # noqa: E402
from kiln import demo as demomod  # noqa: E402


def run_js(src: str) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        return subprocess.run(["node", path], capture_output=True, text=True)
    finally:
        Path(path).unlink(missing_ok=True)


def matches_src(html: str) -> str:
    start = html.index("function matches(")
    end = html.index("\nfunction categories(", start)
    return html[start:end]


class TestFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = demomod.build(cat.load())

    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def js(self, app, q, c):
        src = matches_src(self.html) + (
            "const app = %s;\n"
            "console.log(matches(app, %s, %s) ? 'yes' : 'no');\n"
            % (json.dumps(app), json.dumps(q), json.dumps(c)))
        p = run_js(src)
        self.assertEqual(0, p.returncode, p.stderr)
        return p.stdout.strip() == "yes"

    APP = {"id": "app-tea-log", "name": "Tea Log", "pitch": "a log of teas you drink",
           "features": ["crud", "search"], "category": "personal"}

    def test_an_empty_query_matches_everything(self):
        self.assertTrue(self.js(self.APP, "", ""))

    def test_the_name_matches(self):
        self.assertTrue(self.js(self.APP, "tea", ""))

    def test_the_pitch_matches(self):
        self.assertTrue(self.js(self.APP, "drink", ""))

    def test_a_capability_matches(self):
        self.assertTrue(self.js(self.APP, "search", ""))

    def test_every_word_must_match(self):
        self.assertTrue(self.js(self.APP, "tea log", ""))
        self.assertFalse(self.js(self.APP, "tea quiz", ""))

    def test_a_category_filter_excludes_others(self):
        self.assertTrue(self.js(self.APP, "", "personal"))
        self.assertFalse(self.js(self.APP, "", "clinical"))

    def test_case_is_ignored(self):
        self.assertTrue(self.js(self.APP, "TEA", ""))


class TestThePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = demomod.build(cat.load())

    def test_it_has_a_search_box(self):
        self.assertIn('id="q"', self.html)
        self.assertIn('type="search"', self.html)

    def test_it_has_category_chips(self):
        self.assertIn('id="chips"', self.html)
        self.assertIn("function categories(", self.html)

    def test_it_says_how_many_are_shown(self):
        self.assertIn('id="count"', self.html)
        self.assertIn('aria-live="polite"', self.html)

    def test_it_has_an_empty_state_that_offers_a_way_out(self):
        self.assertIn('id="noresults"', self.html)
        self.assertIn('id="clearq"', self.html)

    def test_the_search_is_above_the_preview(self):
        self.assertLess(self.html.index('id="q"'), self.html.index('id="view"'))

    def test_the_keyboard_can_reach_the_search(self):
        self.assertIn('e.key === "/"', self.html)

    def test_it_does_not_overflow_a_phone(self):
        self.assertIn("main>*{min-width:0}", self.html)

    def test_it_is_still_deterministic(self):
        self.assertEqual(self.html, demomod.build(cat.load()))


if __name__ == "__main__":
    unittest.main()
