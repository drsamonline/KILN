"""The demo page must list every spec, and say how many it actually runs."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat  # noqa: E402
from kiln import demo as demomod  # noqa: E402
from kiln import spec as specmod  # noqa: E402


class TestEverySpecIsListed(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()
        self.html = demomod.build(self.c)

    def test_the_page_carries_one_entry_per_spec_on_disk(self):
        on_disk = sorted((ROOT / "specs").glob("app-*.md")) + \
            sorted((ROOT / "specs" / "gallery").glob("*.md"))
        payload = re.search(r"const DATA = (\{.*?\});\n", self.html, re.S)
        self.assertIsNotNone(payload, "the page no longer embeds its payload")
        data = json.loads(payload.group(1))
        self.assertEqual(len(on_disk), len(data["apps"]))
        self.assertEqual(len(on_disk), data["total"])

    def test_every_gallery_spec_by_name_is_present(self):
        payload = re.search(r"const DATA = (\{.*?\});\n", self.html, re.S)
        data = json.loads(payload.group(1))
        names = {a["name"] for a in data["apps"]}
        for f in sorted((ROOT / "specs" / "gallery").glob("*.md")):
            s = specmod.load(f, self.c)
            self.assertIn(s["name"], names, f.name)

    def test_only_a_few_are_run_and_the_rest_say_why(self):
        payload = re.search(r"const DATA = (\{.*?\});\n", self.html, re.S)
        data = json.loads(payload.group(1))
        runnable = [a for a in data["apps"] if a["runnable"]]
        self.assertLessEqual(len(runnable), demomod.LIVE_MAX)
        self.assertGreater(len(runnable), 0)
        for a in data["apps"]:
            if not a["runnable"]:
                self.assertTrue(a["reason"], a["id"])

    def test_the_page_states_the_ratio(self):
        self.assertIn("run here", self.html)
        self.assertIn("all build locally", self.html)

    def test_no_clinical_app_is_run(self):
        payload = re.search(r"const DATA = (\{.*?\});\n", self.html, re.S)
        data = json.loads(payload.group(1))
        for a in data["apps"]:
            if a["category"] in demomod.EXCLUDE:
                self.assertFalse(a["runnable"], a["id"])

    def test_it_is_deterministic(self):
        self.assertEqual(self.html, demomod.build(self.c))


class TestMasterDetailNeedsDetail(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()
        self.spec = ROOT / "specs" / "gallery" / "master-detail.md"

    def test_the_sample_has_both(self):
        s = specmod.load(self.spec, self.c)
        self.assertIn("detail", s["features"])

    def test_dropping_detail_is_refused(self):
        s = specmod.load(self.spec, self.c)
        s["features"] = [f for f in s["features"] if f != "detail"]
        problems = specmod.validate(s, self.c, "master-detail.md")
        self.assertTrue(any("needs the 'detail' capability" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
