"""The browser compiler must agree with the CLI, or it is a second product."""
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
from kiln import emit             # noqa: E402
from kiln import studio as studiomod  # noqa: E402

SAMPLE = """\
/* @only alpha */
one
/* @end only */
two
/* @only beta */
three
/* @end only */
<!-- @only alpha -->
four
<!-- @end only -->
five
"""


class TestStudioCarriesItsSources(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()
        self.html = studiomod.build(self.c)

    def test_it_embeds_every_archetype(self):
        for pid in cat.patterns():
            self.assertIn(f'"{pid}"', self.html, pid)

    def test_it_embeds_every_gallery_spec(self):
        names = [p.stem for p in (ROOT / "specs" / "gallery").glob("*.md")]
        self.assertGreaterEqual(len(names), 10)
        for stem in names:
            self.assertIn(stem, self.html, stem)

    def test_it_carries_the_strip(self):
        self.assertIn("function stripUnused(", self.html)
        self.assertIn("@end only", self.html)

    def test_it_previews_the_app_it_builds(self):
        self.assertIn('id="prev"', self.html)
        self.assertIn("function showPreview(", self.html)
        self.assertIn("frame.srcdoc = html", self.html)

    def test_the_preview_frame_is_sandboxed(self):
        import re
        tag = re.search(r"<iframe[^>]*>", self.html)
        self.assertIsNotNone(tag)
        self.assertIn("sandbox=", tag.group(0))
        self.assertNotIn("allow-same-origin", tag.group(0))

    def test_the_preview_reports_its_size_and_what_was_left_out(self):
        self.assertIn('id="prevsize"', self.html)
        self.assertIn('id="prevnote"', self.html)
        self.assertIn("capabilities left out", self.html)

    def test_the_feature_grid_scrolls_so_the_build_button_stays_reachable(self):
        self.assertIn("#features{max-height", self.html)

    def test_it_says_which_edition_it_builds(self):
        self.assertIn("Personal edition", self.html)

    def test_it_loads_nothing_remote(self):
        for bad in ('src="http', "<script src", "url(http", "fetch("):
            self.assertNotIn(bad, self.html, bad)

    def test_it_is_deterministic(self):
        self.assertEqual(self.html, studiomod.build(self.c))


class TestStripParity(unittest.TestCase):
    """The JS strip and the Python strip must drop the same blocks."""

    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")
        self.html = studiomod.build(cat.load())

    def _js_strip(self, features):
        start = self.html.index("const ONLY_LINE")
        end = self.html.index("\nfunction download(", start)
        src = self.html[start:end] + (
            "\nconst [text, dropped] = stripUnused(%s, %s);\n"
            "console.log(JSON.stringify({text, dropped}));\n"
            % (json.dumps(SAMPLE), json.dumps(features)))
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(src)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
        finally:
            Path(path).unlink(missing_ok=True)
        self.assertEqual(0, p.returncode, p.stderr)
        return json.loads(p.stdout)

    def test_same_output_when_a_capability_is_kept(self):
        js = self._js_strip(["alpha"])
        py, dropped = emit.strip_unused(SAMPLE, ["alpha"])
        self.assertEqual(py.strip(), js["text"].strip())

    def test_same_output_when_nothing_is_kept(self):
        js = self._js_strip([])
        py, _ = emit.strip_unused(SAMPLE, [])
        self.assertEqual(py.strip(), js["text"].strip())

    def test_same_dropped_list(self):
        js = self._js_strip(["alpha"])
        _, py_dropped = emit.strip_unused(SAMPLE, ["alpha"])
        self.assertEqual(sorted(py_dropped), sorted(js["dropped"]))


if __name__ == "__main__":
    unittest.main()
