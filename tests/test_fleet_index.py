"""The fleet index: every app in one file, installable, with one backup."""
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
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat   # noqa: E402
from kiln import fleet as fleetmod  # noqa: E402
from kiln import guards            # noqa: E402
from kiln import spec as specmod   # noqa: E402


class TestBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = cat.load()
        cls.files = fleetmod.build(cls.c)
        cls.html = cls.files["index.html"]

    def test_it_produces_three_files(self):
        self.assertEqual({"index.html", "manifest.webmanifest", "sw.js"}, set(self.files))

    def test_it_lists_every_spec(self):
        self.assertEqual(len(specmod.spec_paths(ROOT)), self.html.count('class="app"'))

    def test_every_app_is_inlined(self):
        for p in specmod.spec_paths(ROOT):
            s = specmod.load(p, self.c)
            self.assertIn(s["id"], self.html, p.name)

    def test_it_is_deterministic(self):
        self.assertEqual(self.html, fleetmod.build(self.c)["index.html"])

    def test_the_manifest_is_valid_json_with_a_start_url(self):
        doc = json.loads(self.files["manifest.webmanifest"])
        self.assertIn("start_url", doc)
        self.assertEqual("standalone", doc["display"])
        self.assertTrue(doc["icons"])

    def test_the_service_worker_caches_the_shell(self):
        sw = self.files["sw.js"]
        self.assertIn("./index.html", sw)
        self.assertIn("caches.open", sw)
        self.assertIn("manifest.webmanifest", sw)

    def test_it_carries_a_fleet_wide_backup(self):
        self.assertIn("Back up all data", self.html)
        self.assertIn("kiln:", self.html)          # the storage key prefix
        self.assertIn("Restore", self.html)

    def test_no_app_is_loaded_over_the_network(self):
        for bad in ('src="http', "<script src", "fetch(\"http"):
            self.assertNotIn(bad, self.html)


class TestInABrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = fleetmod.build(cat.load())["index.html"]

    def setUp(self):
        if not shutil.which("chromium"):
            self.skipTest("chromium is not on PATH")

    def test_the_page_lists_and_picks_and_backs_up(self):
        probe = """
<script>
window.addEventListener("load", function () {
  setTimeout(function () {
    var out = [];
    out.push("apps=" + document.querySelectorAll(".app").length);
    out.push("picked=" + ((document.querySelector("#view").srcdoc || "").length > 1000));
    localStorage.setItem("kiln:journal", '{"v":1,"rows":[{"id":"r1"}]}');
    document.querySelector("#backup").click();
    setTimeout(function () {
      out.push("status=" + /Backed up \\d+ of/.test(document.querySelector("#status").textContent));
      document.title = "DBG|" + out.join("|");
    }, 250);
  }, 350);
});
</script>"""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "index.html"
            p.write_text(self.html.replace("</body>", probe + "</body>"), encoding="utf-8")
            r = subprocess.run(["chromium", "--headless=new", "--disable-gpu", "--no-sandbox",
                                "--allow-file-access-from-files", "--virtual-time-budget=12000",
                                "--dump-dom", p.as_uri()], capture_output=True, text=True)
        title = re.search(r"<title>([^<]*)</title>", r.stdout)
        self.assertIsNotNone(title, r.stderr[:200])
        got = title.group(1)
        self.assertIn("apps=37", got)
        self.assertIn("picked=true", got)
        self.assertIn("status=true", got)


class TestGuard(unittest.TestCase):
    def test_the_committed_index_is_current(self):
        rows = guards.check_fleet(cat.load())
        self.assertFalse([r for r in rows if not r.ok], [r.detail for r in rows])


if __name__ == "__main__":
    unittest.main()
