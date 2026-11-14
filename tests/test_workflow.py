"""The CI workflow is code: its shape can be checked before it runs."""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

WF = ROOT / ".github" / "workflows" / "kiln.yml"


class TestWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WF.read_text(encoding="utf-8")
        try:
            import yaml
            cls.doc = yaml.safe_load(cls.text)
        except ImportError:
            cls.doc = None

    def test_it_parses(self):
        if self.doc is None:
            self.skipTest("pyyaml is not installed")
        self.assertIn("jobs", self.doc)

    def test_every_job_has_a_name_and_runs_on(self):
        if self.doc is None:
            self.skipTest("pyyaml is not installed")
        for name, job in self.doc["jobs"].items():
            self.assertIn("runs-on", job, name)
            self.assertTrue(job.get("steps"), name)

    def test_only_the_publishing_job_may_write(self):
        if self.doc is None:
            self.skipTest("pyyaml is not installed")
        self.assertEqual("read", self.doc["permissions"]["contents"])
        writers = [n for n, j in self.doc["jobs"].items()
                   if (j.get("permissions") or {}).get("contents") == "write"]
        self.assertEqual(["publish-status"], writers)

    def test_publishing_never_runs_on_a_pull_request(self):
        if self.doc is None:
            self.skipTest("pyyaml is not installed")
        cond = self.doc["jobs"]["publish-status"]["if"]
        self.assertIn("github.event_name == 'push'", cond)
        self.assertIn("refs/heads/main", cond)

    def test_the_publish_push_targets_a_branch_that_is_not_main(self):
        self.assertIn("status-publish:status", self.text)
        self.assertNotIn("push --force origin status-publish:main", self.text)

    def test_every_shell_block_is_valid_bash(self):
        blocks = re.findall(r"run: \|\n((?:          .*\n|\n)+)", self.text)
        self.assertTrue(blocks, "no shell blocks found")
        for i, block in enumerate(blocks):
            script = "\n".join(l[10:] for l in block.splitlines())
            with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as f:
                f.write(script)
                path = f.name
            try:
                p = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
                self.assertEqual(0, p.returncode, f"block {i}: {p.stderr}")
            finally:
                Path(path).unlink(missing_ok=True)

    def test_it_does_not_pin_a_third_party_action_to_a_branch(self):
        """A floating tag is a supply-chain risk; every action is version-pinned."""
        for line in self.text.splitlines():
            if "uses:" in line:
                ref = line.split("uses:")[1].strip()
                self.assertRegex(ref, r"@v\d+", line)

    def test_the_status_feed_is_documented(self):
        docs = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("status.json", docs)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("status json", readme)


if __name__ == "__main__":
    unittest.main()
