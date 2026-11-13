"""Tests for the licence tiers, the signature check and the watermark.

The signature is the one piece of cryptography in the repository, so it is tested
against the RFC's own vector, not just against itself.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kiln import catalog as cat     # noqa: E402
from kiln import compose            # noqa: E402
from kiln import ed25519            # noqa: E402
from kiln import licence as lic     # noqa: E402
from kiln import spec as specmod    # noqa: E402
from kiln import verify             # noqa: E402


class TestEd25519(unittest.TestCase):
    """RFC 8032 section 7.1, test vector 1: empty message."""

    SK = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    PK = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
    SIG = bytes.fromhex(
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc"
        "61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b")

    def test_public_key_matches_the_rfc(self):
        self.assertEqual(self.PK, ed25519.public_key(self.SK))

    def test_signature_matches_the_rfc(self):
        self.assertEqual(self.SIG, ed25519.sign(b"", self.SK, self.PK))

    def test_verify_accepts_the_rfc_vector(self):
        self.assertTrue(ed25519.verify(self.SIG, b"", self.PK))

    def test_verify_rejects_a_changed_message(self):
        self.assertFalse(ed25519.verify(self.SIG, b"x", self.PK))

    def test_verify_rejects_a_wrong_key(self):
        self.assertFalse(ed25519.verify(self.SIG, b"", ed25519.public_key(bytes(32))))

    def test_verify_rejects_garbage(self):
        self.assertFalse(ed25519.verify(bytes(64), b"m", self.PK))
        self.assertFalse(ed25519.verify(b"short", b"m", self.PK))


class TestLicenceKeys(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.home = Path(self.td.name)
        self._saved = (lic.HOME, lic.STORE, lic.PRIVATE, lic.PIN)
        lic.HOME = self.home
        lic.STORE = self.home / "licence.json"
        lic.PRIVATE = self.home / "private.key"
        lic.PIN = self.home / "pin.json"
        lic.keygen()

    def tearDown(self):
        lic.HOME, lic.STORE, lic.PRIVATE, lic.PIN = self._saved
        self.td.cleanup()

    def test_keygen_writes_a_private_key_outside_the_repo(self):
        self.assertTrue(lic.PRIVATE.exists())
        self.assertEqual(32, len(lic.PRIVATE.read_bytes()))
        self.assertTrue(lic.PIN.exists())
        self.assertEqual(32, len(lic.pinned()))  # raw bytes; 64 hex characters on disk

    def test_issue_and_decode_round_trip(self):
        key = lic.issue("commercial", "Acme Clinic", days=30)
        self.assertTrue(key.startswith("KILN1."))
        payload = lic.decode(key)
        self.assertEqual("commercial", payload["tier"])
        self.assertEqual("Acme Clinic", payload["licensee"])

    def test_a_tampered_payload_is_rejected(self):
        key = lic.issue("commercial", "Acme", days=30)
        head, body, sig = key.split(".")
        forged = json.dumps({"v": 1, "tier": "corporate", "licensee": "Someone",
                             "expires": "2099-01-01", "issued": "2026-01-01", "id": "x"},
                            sort_keys=True, separators=(",", ":")).encode()
        bad = f"{head}.{lic._b64e(forged)}.{sig}"
        with self.assertRaises(lic.LicenceError):
            lic.decode(bad)

    def test_a_key_signed_by_another_pair_is_rejected(self):
        other = Path(self.td.name) / "other.key"
        other.write_bytes(bytes(range(32)))
        good = lic.PRIVATE.read_bytes()
        lic.PRIVATE = other
        foreign = lic.issue("commercial", "Not You", days=30)
        lic.PRIVATE = Path(self.td.name) / "private.key"
        lic.PRIVATE.write_bytes(good)
        with self.assertRaises(lic.LicenceError):
            lic.decode(foreign)

    def test_an_expired_key_is_rejected(self):
        key = lic.issue("commercial", "Acme", days=-1)
        with self.assertRaises(lic.LicenceError):
            lic.decode(key)

    def test_a_personal_edition_needs_no_key(self):
        with self.assertRaises(lic.LicenceError):
            lic.issue("personal", "Acme")

    def test_activate_then_resolve(self):
        key = lic.issue("commercial", "BigCo", days=30)
        lic.activate(key)
        tier, licensee, source = lic.resolve()
        self.assertEqual("commercial", tier)
        self.assertEqual("BigCo", licensee)
        self.assertEqual("licence", source)

    def test_no_licence_means_personal(self):
        tier, licensee, source = lic.resolve()
        self.assertEqual(("personal", "", "default"), (tier, licensee, source))

    def test_a_paid_tier_without_a_licence_is_refused(self):
        with self.assertRaises(lic.LicenceError):
            lic.resolve("commercial")

    def test_a_paid_flag_with_the_right_licence_is_accepted(self):
        lic.activate(lic.issue("commercial", "Acme", days=30))
        tier, licensee, _ = lic.resolve("commercial")
        self.assertEqual(("commercial", "Acme"), (tier, licensee))


class TestAttribution(unittest.TestCase):
    def setUp(self):
        self.c = cat.load()
        self.s = specmod.load(ROOT / "specs" / "app-notes.md", self.c)

    def _html(self, tier, licensee=""):
        plan = compose.plan(self.s, self.c, tier=tier, licensee=licensee)
        return plan[0]["ctx"], plan

    def test_personal_carries_the_sponsor_block(self):
        ctx, _ = self._html("personal")
        build = json.loads(ctx["BUILD_JSON"])
        self.assertTrue(build["sponsor"])
        self.assertIn("drsohilboi@ybl", json.dumps(build))

    def test_commercial_carries_no_sponsor(self):
        ctx, _ = self._html("commercial", "Acme")
        build = json.loads(ctx["BUILD_JSON"])
        self.assertEqual({}, build["sponsor"])
        self.assertEqual("Acme", build["licensee"])

    def test_every_tier_carries_a_fingerprint(self):
        for tier in ("personal", "commercial", "demo"):
            ctx, _ = self._html(tier)
            self.assertRegex(ctx["FINGERPRINT"], r"^[0-9a-f]{16}$")

    def test_the_fingerprint_is_the_model_hash(self):
        ctx, _ = self._html("personal")
        model = json.loads(ctx["MODEL_JSON"])
        self.assertEqual(compose.fnv1a64(compose.canonical(model)), ctx["FINGERPRINT"])

    def test_editing_the_model_changes_the_fingerprint(self):
        ctx, _ = self._html("personal")
        model = json.loads(ctx["MODEL_JSON"])
        model["features"] = model["features"] + ["print"]
        self.assertNotEqual(compose.fnv1a64(compose.canonical(model)), ctx["FINGERPRINT"])

    def test_demo_caps_the_features(self):
        ctx, _ = self._html("demo")
        model = json.loads(ctx["MODEL_JSON"])
        self.assertTrue(set(model["features"]) <= lic.DEMO_FEATURES)
        self.assertIn("crud", model["features"])

    def test_a_built_app_verifies_with_its_watermark(self):
        with tempfile.TemporaryDirectory() as td:
            res = verify.build_and_check(ROOT / "specs" / "app-notes.md", self.c, td,
                                         tier="commercial", licensee="Acme")
            self.assertEqual([], [(r["level"], r["name"]) for r in res.failed])
            html = (Path(td) / "index.html").read_text(encoding="utf-8")
            self.assertIn("generated by KILN", html)
            self.assertIn('name="kiln-fingerprint"', html)
            self.assertNotIn("drsohilboi@ybl", html)


if __name__ == "__main__":
    unittest.main()
