"""Tests for the pages, the legal set and the documentation links."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat   # noqa: E402
from kiln import demo as demomod  # noqa: E402
from kiln import guards           # noqa: E402


class TestDemo(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_build_is_deterministic(self):
        self.assertEqual(demomod.build(self.c), demomod.build(self.c))

    def test_inlines_a_real_app(self):
        html = demomod.build(self.c)
        self.assertIn("const MODEL =", html)
        self.assertIn("kiln:", html)

    def test_loads_nothing_remote(self):
        html = demomod.build(self.c)
        for bad in ('src="http', "<script src", "url(http"):
            self.assertNotIn(bad, html)

    def test_committed_demo_is_current(self):
        p = ROOT / "demo.html"
        self.assertTrue(p.exists(), "run: python3 -m kiln demo")
        self.assertEqual(demomod.build(self.c), p.read_text(encoding="utf-8"),
                         "demo.html is stale: run python3 -m kiln demo")


class TestPages(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_landing_exists_and_links_the_products(self):
        p = ROOT / "index.html"
        self.assertTrue(p.exists())
        html = p.read_text(encoding="utf-8")
        for need in ("studio.html", "demo.html", "assets/screenshot-app.png"):
            self.assertIn(need, html)

    def test_landing_loads_nothing_remote(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for bad in ('src="http', "<script src", "url(http"):
            self.assertNotIn(bad, html)

    def test_screenshots_are_real_files(self):
        for shot in ("assets/screenshot-app.png", "assets/screenshot-studio.png"):
            p = ROOT / shot
            self.assertTrue(p.exists(), shot)
            self.assertGreater(p.stat().st_size, 2000, shot)

    def test_metadata_files_parse(self):
        import json
        for f in ("MANIFEST.json", "PAGES.json", "manifest.webmanifest"):
            json.loads((ROOT / f).read_text(encoding="utf-8"))
        self.assertIn("<svg", (ROOT / "icon.svg").read_text(encoding="utf-8"))


class TestGuardResults(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_site_guards_pass(self):
        bad = [r.name for r in guards.check_site(self.c) if not r.ok]
        self.assertEqual([], bad)

    def test_legal_set_is_complete(self):
        bad = [r.name for r in guards.check_legal_set() if not r.ok]
        self.assertEqual([], bad)

    def test_every_relative_link_resolves(self):
        bad = [r.name + " " + r.detail for r in guards.check_links() if not r.ok]
        self.assertEqual([], bad)

    def test_support_block_is_present_and_consistent(self):
        bad = [r.name + " " + r.detail for r in guards.check_support() if not r.ok]
        self.assertEqual([], bad)

    def test_support_reaches_the_landing_page(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for need in ("drsohilboi@ybl", "ko-fi.com/matneo", "sponsors/drsamonline",
                     "paypal.me/drsohilmomin", "amazon.com/stores/author"):
            self.assertIn(need, html)

    def test_readme_states_the_licence_in_words(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(self.c["licence"]["badge"], text)


if __name__ == "__main__":
    unittest.main()
