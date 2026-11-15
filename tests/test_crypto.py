"""Encryption at rest: the emitted code, run for real.

The browser cannot be trusted to finish WebCrypto inside a virtual clock, so the
helpers are extracted from the built app and run in Node, where they resolve. That
tests the code that ships, not a copy of it.
"""
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

from kiln import catalog as cat    # noqa: E402
from kiln import spec as specmod   # noqa: E402
from kiln import verify            # noqa: E402

SPEC = ROOT / "specs" / "gallery" / "encrypted-log.md"


def extract_fn(js: str, name: str) -> str:
    for prefix in ("async function ", "function "):
        needle = prefix + name + "("
        if needle in js:
            i = js.index(needle)
            depth, started = 0, False
            for j in range(i, len(js)):
                if js[j] == "{":
                    depth += 1
                    started = True
                elif js[j] == "}":
                    depth -= 1
                    if started and depth == 0:
                        return js[i:j + 1]
    raise AssertionError(f"{name} not found in the emitted app")


class TestEmittedCrypto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        out = Path(cls.tmp.name) / "app"
        res = verify.build_and_check(SPEC, cat.load(), out)
        cls.failed = [(r["level"], r["name"]) for r in res.failed]
        cls.html = (out / "index.html").read_text(encoding="utf-8")
        cls.js = re.findall(r"<script>(.*?)</script>", cls.html, re.S)[0]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        if not shutil.which("node"):
            self.skipTest("node is not on PATH")

    def test_the_spec_builds_and_verifies(self):
        self.assertEqual([], self.failed)

    def test_the_unlock_screen_is_emitted(self):
        self.assertIn('id="unlock"', self.html)
        self.assertIn('type="password"', self.html)

    def test_the_primitives_are_the_ones_named(self):
        self.assertIn("PBKDF2", self.html)
        self.assertIn("AES-GCM", self.html)
        self.assertIn("deriveKey", self.html)
        self.assertNotIn("eval(", self.html)

    def test_the_passphrase_is_never_written_to_storage(self):
        # the only setItem calls are the sealed blob and the salt
        sets = re.findall(r"localStorage\.setItem\(([^,]+),", self.html)
        self.assertTrue(sets, "no storage writes found")
        for target in sets:
            self.assertIn("KEY", target, f"an unexpected storage key: {target}")
        self.assertNotIn("passphrase", " ".join(
            l for l in self.html.splitlines() if "setItem" in l).lower())

    def _run(self, body: str) -> str:
        helpers = "\n\n".join(extract_fn(self.js, n) for n in
                              ("b64e", "b64d", "deriveKey", "sealJson", "openSealed"))
        prelude = (
            'import { webcrypto as crypto } from "node:crypto";\n'
            'const btoa = (s) => Buffer.from(s, "binary").toString("base64");\n'
            'const atob = (s) => Buffer.from(s, "base64").toString("binary");\n'
            'const MODEL = {version: 1, crypto: {iterations: 100000}};\n'
            'let CRYPTO_KEY = null;\nconst KDF_ITERATIONS = 100000;\n')
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(prelude + helpers + "\n" + body)
            path = f.name
        try:
            p = subprocess.run(["node", path], capture_output=True, text=True)
            self.assertEqual(0, p.returncode, p.stderr)
            return p.stdout.strip()
        finally:
            Path(path).unlink(missing_ok=True)

    def test_a_roundtrip_restores_the_payload_exactly(self):
        out = self._run("""
(async () => {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const key = await deriveKey("correct horse battery", salt);
  const payload = {v: 1, rows: [{id: "r1", title: "Meera Patel"}]};
  const blob = await sealJson(payload, key, salt);
  const back = await openSealed(blob, key);
  console.log(JSON.stringify(back) === JSON.stringify(payload) ? "yes" : "no");
})();
""")
        self.assertEqual("yes", out)

    def test_the_ciphertext_does_not_contain_the_record(self):
        out = self._run("""
(async () => {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const key = await deriveKey("correct horse battery", salt);
  const blob = await sealJson({v: 1, rows: [{title: "Meera Patel"}]}, key, salt);
  const json = JSON.stringify(blob);
  console.log(json.indexOf("Meera") >= 0 ? "leaks" : "clean");
})();
""")
        self.assertEqual("clean", out)

    def test_a_wrong_passphrase_is_refused(self):
        out = self._run("""
(async () => {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const key = await deriveKey("correct horse battery", salt);
  const blob = await sealJson({v: 1, rows: []}, key, salt);
  const other = await deriveKey("correct horse batterY", salt);
  try { await openSealed(blob, other); console.log("opened"); }
  catch (e) { console.log("refused"); }
})();
""")
        self.assertEqual("refused", out)

    def test_the_same_plaintext_with_a_new_salt_is_different_ciphertext(self):
        out = self._run("""
(async () => {
  const payload = {v: 1, rows: [{title: "x"}]};
  const s1 = crypto.getRandomValues(new Uint8Array(16));
  const s2 = crypto.getRandomValues(new Uint8Array(16));
  const b1 = await sealJson(payload, await deriveKey("p", s1), s1);
  const b2 = await sealJson(payload, await deriveKey("p", s2), s2);
  console.log(b1.data !== b2.data ? "different" : "same");
})();
""")
        self.assertEqual("different", out)


class TestCryptoSpec(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()

    def test_an_iteration_count_below_the_floor_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["crypto"]["iterations"] = 1000
        problems = specmod.validate(s, self.c, "encrypted-log.md")
        self.assertTrue(any("at least 100000" in p for p in problems), problems)

    def test_an_absurd_iteration_count_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["crypto"]["iterations"] = 9000000
        problems = specmod.validate(s, self.c, "encrypted-log.md")
        self.assertTrue(any("denial" in p for p in problems), problems)

    def test_crypto_without_crud_is_refused(self):
        s = specmod.load(SPEC, self.c)
        s["features"] = [f for f in s["features"] if f != "crud"]
        problems = specmod.validate(s, self.c, "encrypted-log.md")
        self.assertTrue(any("needs the 'crud'" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
