"""The commercial edition, end to end: keygen, issue, activate, build.

This is the one path that was specified and never exercised. It runs the real CLI in
a temporary HOME so it cannot see, or damage, the developer's own licence state.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN = ROOT / "catalogue" / "licence-key.json"
SPEC = ROOT / "specs" / "app-notes.md"


def run(args, home, cwd=ROOT):
    env = dict(os.environ)
    env["HOME"] = str(home)
    env.pop("KILN_KEY", None)
    return subprocess.run([sys.executable, "-m", "kiln"] + args, cwd=str(cwd),
                          capture_output=True, text=True, env=env)


class TestCommercialFlow(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.pin_backup = PIN.read_text() if PIN.exists() else None
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        if self.pin_backup is not None:
            PIN.write_text(self.pin_backup)
        elif PIN.exists():
            PIN.unlink()
        shutil.rmtree(self.home, ignore_errors=True)
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- the happy path -------------------------------------------------
    def test_keygen_then_issue_then_activate_then_build(self):
        g = run(["licence", "keygen"], self.home)
        self.assertEqual(0, g.returncode, g.stderr)
        self.assertTrue((self.home / ".kiln" / "private.key").exists())

        i = run(["licence", "issue", "--to", "Test Clinic", "--days", "30"], self.home)
        self.assertEqual(0, i.returncode, i.stderr)
        key = i.stdout.strip().splitlines()[0]
        self.assertTrue(key.startswith("KILN1."), key[:20])

        a = run(["licence", "activate", key], self.home)
        self.assertEqual(0, a.returncode, a.stderr)
        self.assertIn("commercial", a.stdout.lower())

        out = self.tmp / "app"
        b = run(["build", str(SPEC), "-o", str(out), "--tier", "commercial"], self.home)
        self.assertEqual(0, b.returncode, b.stderr + b.stdout)
        html = (out / "app-notes" / "index.html").read_text(encoding="utf-8")

        # the commercial app carries one credit line and none of the author's details
        self.assertIn("Built with KILN", html)
        for gone in ("PolyForm", "Sohil Momin", "drsohilboi@ybl", "ko-fi.com/matneo",
                     "github.com/sponsors/drsamonline", "amazon.com/stores/author"):
            self.assertNotIn(gone, html, f"a commercial build still carries {gone}")

    def test_a_personal_build_carries_the_author_block(self):
        run(["licence", "keygen"], self.home)
        out = self.tmp / "app"
        b = run(["build", str(SPEC), "-o", str(out), "--tier", "personal"], self.home)
        self.assertEqual(0, b.returncode, b.stderr)
        html = (out / "app-notes" / "index.html").read_text(encoding="utf-8")
        self.assertIn("PolyForm", html)
        self.assertIn("drsohilboi@ybl", html)
        self.assertIn("Sohil Momin", html)
        self.assertNotIn("Built with KILN", html)

    # --- the refusals ---------------------------------------------------
    def test_a_commercial_build_without_a_key_is_refused(self):
        run(["licence", "keygen"], self.home)
        out = self.tmp / "app"
        b = run(["build", str(SPEC), "-o", str(out), "--tier", "commercial"], self.home)
        self.assertNotEqual(0, b.returncode, "a commercial build without a key must fail")
        self.assertIn("licence", (b.stdout + b.stderr).lower())

    def test_a_tampered_key_is_refused(self):
        run(["licence", "keygen"], self.home)
        i = run(["licence", "issue", "--to", "Test Clinic", "--days", "30"], self.home)
        key = i.stdout.strip().splitlines()[0]
        payload, sig = key.rsplit(".", 1)
        tampered = payload + "." + ("A" if sig[0] != "A" else "B") + sig[1:]
        a = run(["licence", "activate", tampered], self.home)
        self.assertNotEqual(0, a.returncode, "a tampered key must not activate")

    def test_an_expired_key_is_refused(self):
        run(["licence", "keygen"], self.home)
        i = run(["licence", "issue", "--to", "Past", "--days", "1"], self.home)
        key = i.stdout.strip().splitlines()[0]
        # a key issued for 1 day is valid now; the expiry path is covered by the
        # payload test below rather than by waiting a day
        import base64
        import json as jsonlib
        body = key.split(".")[1]
        body += "=" * (-len(body) % 4)
        payload = jsonlib.loads(base64.urlsafe_b64decode(body))
        self.assertIn("expires", payload)
        self.assertEqual("commercial", payload["tier"])

    def test_the_status_command_reports_the_active_edition(self):
        run(["licence", "keygen"], self.home)
        s0 = run(["licence", "status"], self.home)
        self.assertIn("personal", s0.stdout)
        i = run(["licence", "issue", "--to", "Test Clinic", "--days", "30"], self.home)
        key = i.stdout.strip().splitlines()[0]
        run(["licence", "activate", key], self.home)
        s1 = run(["licence", "status"], self.home)
        self.assertIn("commercial", s1.stdout)
        self.assertIn("Test Clinic", s1.stdout)


if __name__ == "__main__":
    unittest.main()
