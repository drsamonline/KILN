"""The catalogue's size is a file count, so no document may remember it wrongly."""
from __future__ import annotations

import inspect
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import guards  # noqa: E402


def _tree(tmp: Path, patterns: int, docs: dict[str, str]) -> Path:
    """A miniature repository: N pattern files and the documents that describe them."""
    d = tmp / "catalogue" / "patterns"
    d.mkdir(parents=True)
    for i in range(patterns):
        (d / f"p{i:02d}.json").write_text("{}", encoding="utf-8")
    for name, text in docs.items():
        (tmp / name).write_text(text, encoding="utf-8")
    return tmp


class TestStatedArchetypes(unittest.TestCase):
    def test_the_guard_passes_on_this_tree(self):
        rows = guards.check_stated_archetypes()
        self.assertFalse([r for r in rows if not r.ok], [r.detail for r in rows])
        real = len(sorted((ROOT / "catalogue" / "patterns").glob("*.json")))
        self.assertIn(str(real), rows[0].detail)

    def test_a_wrong_total_fails_and_names_the_document(self):
        with tempfile.TemporaryDirectory() as td:
            root = _tree(Path(td), 30,
                         {"CHANGELOG.md": "1.0.0: **all 24 archetypes emitted**\n"})
            rows = guards.check_stated_archetypes(root)
        bad = [r for r in rows if not r.ok]
        self.assertTrue(bad, "a stated 24 against 30 files must fail")
        self.assertIn("CHANGELOG.md", bad[0].detail)
        self.assertIn("30", bad[0].detail)

    def test_every_phrasing_of_a_total_is_checked(self):
        docs = {
            "RELEASE.md": "It has since settled: 24 archetypes, 50 capabilities.\n",
            "HANDOVER.md": "| `catalogue/` | 50 capabilities, 24 pattern descriptors |\n",
            "README.md": "the 24-archetype catalogue complete\n",
        }
        with tempfile.TemporaryDirectory() as td:
            root = _tree(Path(td), 30, docs)
            bad = [r for r in guards.check_stated_archetypes(root) if not r.ok]
        self.assertTrue(bad)
        for name in docs:
            self.assertIn(name, bad[0].detail)

    def test_a_subset_is_not_a_total(self):
        """A line about one old studio build is not a claim about the catalogue."""
        docs = {
            "CHANGELOG.md": "| Size | studio.html 118 KB, carrying 10 gallery specs "
                            "and 10 archetypes |\n| A3 archetype | `crud-list` |\n",
        }
        with tempfile.TemporaryDirectory() as td:
            root = _tree(Path(td), 30, docs)
            bad = [r for r in guards.check_stated_archetypes(root) if not r.ok]
        self.assertFalse(bad, [r.detail for r in bad])

    def test_an_empty_catalogue_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = _tree(Path(td), 0, {})
            rows = guards.check_stated_archetypes(root)
        self.assertFalse(rows[0].ok, "no pattern files must not read as ok")

    def test_it_is_wired_into_the_audit(self):
        self.assertIn("check_stated_archetypes", inspect.getsource(guards.audit))


if __name__ == "__main__":
    unittest.main()
