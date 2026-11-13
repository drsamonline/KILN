"""The page must stay linear: a derived figure is computed once per render."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat  # noqa: E402
from kiln import guards          # noqa: E402
from kiln import verify          # noqa: E402

TEMPLATE = ROOT / "templates" / "app" / "index.html"


def row_loop_bodies(src: str) -> list[str]:
    lines = src.splitlines()
    out = []
    for s, l in enumerate(lines):
        if "for (const r of items) {" not in l:
            continue
        depth = 0
        for i in range(s, len(lines)):
            depth += lines[i].count("{") - lines[i].count("}")
            if depth == 0 and i > s:
                out.append("\n".join(lines[s:i + 1]))
                break
    return out


class TestRenderIsLinear(unittest.TestCase):
    def setUp(self):
        self.src = TEMPLATE.read_text(encoding="utf-8")

    def test_no_derived_figure_is_computed_inside_a_row_loop(self):
        for body in row_loop_bodies(self.src):
            for fn in guards.DERIVED:
                for line in body.splitlines():
                    if fn in line and "cached(" not in line:
                        prev = body.splitlines()[max(0, body.splitlines().index(line) - 1)]
                        if "cached(" not in prev:
                            self.fail(f"{fn} runs inside the row loop: {line.strip()}")

    def test_the_cache_is_reset_every_render(self):
        self.assertIn("let RENDER_CACHE = {};", self.src)
        m = re.search(r"function render\(\) \{\n\s+RENDER_CACHE = \{\};", self.src)
        self.assertIsNotNone(m, "render() must clear the cache first")

    def test_the_guard_is_part_of_the_audit(self):
        rows = guards.check_row_loop_is_linear(cat.load())
        self.assertFalse([r for r in rows if not r.ok], [r.detail for r in rows])

    def test_the_built_app_carries_the_cache(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "app"
            verify.build_and_check(ROOT / "specs" / "gallery" / "register.md",
                                   cat.load(), out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("function cached(", html)
            self.assertIn('cached("running"', html)

    def test_the_cache_is_a_cheap_shared_utility(self):
        """It is base code, like the metric strip: six capabilities use it, so gating
        it behind one of them would be a lie. It must stay small instead."""
        start = self.src.index("let RENDER_CACHE = {};")
        end = self.src.index("/* cache:end */")
        size = len(self.src[start:end].encode("utf-8"))
        self.assertLess(size, 400, f"the cache block grew to {size} bytes")


if __name__ == "__main__":
    unittest.main()
