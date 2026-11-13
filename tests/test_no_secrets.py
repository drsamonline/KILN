"""No private key, and no orphan pinned key, may reach the repository."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestNoSecrets(unittest.TestCase):
    def test_no_private_key_is_tracked(self):
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
        tracked = out.stdout.splitlines()
        for bad in ("private.key", ".kiln/", "licence-private"):
            hits = [f for f in tracked if bad in f]
            self.assertEqual([], hits, f"a private key is tracked: {hits}")

    def test_the_pinned_key_is_ignored_until_the_owner_commits_it(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("catalogue/licence-key.json", gitignore)

    def test_the_pinned_key_is_not_in_the_tree(self):
        out = subprocess.run(["git", "ls-files", "catalogue/licence-key.json"],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual("", out.stdout.strip(),
                         "a pinned key is committed: its private half must exist somewhere")

    def test_the_command_says_so_when_nothing_is_pinned(self):
        from kiln import licence as lic
        # pinned() reads the repo file; with none present it must say so, not raise
        self.assertIn(lic.pinned(), (None, b""))


if __name__ == "__main__":
    unittest.main()
