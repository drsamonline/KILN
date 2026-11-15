"""The fleet specs are the absorption test: they must keep building."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat   # noqa: E402
from kiln import spec as specmod  # noqa: E402
from kiln import verify           # noqa: E402

FLEET = ROOT / "specs" / "fleet"


class TestFleetSpecs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = cat.load()
        cls.paths = sorted(FLEET.glob("*.md"))

    def test_there_are_fleet_specs(self):
        self.assertGreaterEqual(len(self.paths), 3)

    def test_spec_paths_sees_them(self):
        seen = [p.name for p in specmod.spec_paths(ROOT) if "fleet" in str(p)]
        for p in self.paths:
            self.assertIn(p.name, seen, "spec_paths does not reach specs/fleet")

    def test_each_one_builds_and_verifies(self):
        for p in self.paths:
            with self.subTest(spec=p.name), tempfile.TemporaryDirectory() as td:
                res = verify.build_and_check(p, self.c, Path(td) / "app")
                failed = [(r["level"], r["name"]) for r in res.failed]
                self.assertEqual([], failed, p.name)

    def test_each_one_names_the_repository_it_came_from(self):
        for p in self.paths:
            text = p.read_text(encoding="utf-8")
            self.assertIn("github.com/drsamonline/", text,
                          f"{p.name} does not credit the fleet repo it came from")

    def test_each_one_says_what_it_does_not_do(self):
        for p in self.paths:
            self.assertIn("## What it must NOT do", p.read_text(encoding="utf-8"), p.name)

    def test_the_docs_page_lists_every_fleet_spec(self):
        page = (ROOT / "docs" / "FLEET-SPECS.md").read_text(encoding="utf-8")
        for p in self.paths:
            self.assertIn(p.name, page, f"{p.name} is not in docs/FLEET-SPECS.md")


if __name__ == "__main__":
    unittest.main()
