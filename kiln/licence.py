"""Licence tiers, and the attribution each one puts in a generated app.

| edition | what the generated app carries |
|---|---|
| `personal` | licence line, "Built with KILN", the sponsor block, the build fingerprint |
| `commercial` | one line: "Built with KILN", hyperlinked. No sponsor block, no sponsor page |
| `demo` | the personal edition, capped and without export — the online demo only |

A key is Ed25519-signed and verified against a pinned public key, offline, with
no packages. This is a deterrent and an evidence trail, not DRM: the compiler is
source-available, so anyone can edit it. SECURITY.md says so in those words.
"""
from __future__ import annotations

import base64
import datetime
import json
import os
import secrets
from pathlib import Path

from . import ed25519

ROOT = Path(__file__).resolve().parent.parent
PIN = ROOT / "catalogue" / "licence-key.json"
HOME = Path(os.environ.get("KILN_HOME", Path.home() / ".kiln"))
STORE = HOME / "licence.json"
PRIVATE = HOME / "private.key"

PREFIX = "KILN1"
LEDGER = "issued.jsonl"
TIERS = ("personal", "commercial")
PAID = ("commercial",)
ALIASES = {"free": "personal", "personal": "personal", "commercial": "commercial"}
DEMO_FEATURES = {"crud", "search", "theme", "sort"}
EDITIONS = TIERS

SPONSOR = {
    "upi": "drsohilboi@ybl",
    "sponsors": "https://github.com/sponsors/drsamonline",
    "kofi": "https://ko-fi.com/matneo",
    "books": "https://www.amazon.com/stores/author/B08ZT331LY/allbooks",
    "site": "https://drsamonline.github.io/KILN/",
}


class LicenceError(Exception):
    def __init__(self, problems):
        self.problems = problems if isinstance(problems, list) else [problems]
        super().__init__("\n".join(f"  - {p}" for p in self.problems))


# ------------------------------------------------------------------ the key
def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def pinned() -> bytes | None:
    if not PIN.exists():
        return None
    try:
        raw = json.loads(PIN.read_text(encoding="utf-8")).get("public_key", "")
        return bytes.fromhex(raw) if raw else None
    except (json.JSONDecodeError, ValueError):
        return None


def keygen(pin: bool = True) -> dict:
    """Create a signing pair. The private half never enters the repository."""
    HOME.mkdir(parents=True, exist_ok=True)
    if PRIVATE.exists() and not pin:
        raise LicenceError([f"{PRIVATE} already exists; refusing to overwrite it"])
    secret = secrets.token_bytes(32)
    pub = ed25519.public_key(secret)
    PRIVATE.write_bytes(secret)
    try:
        PRIVATE.chmod(0o600)
    except OSError:
        pass
    if pin:
        PIN.parent.mkdir(parents=True, exist_ok=True)
        PIN.write_text(json.dumps({
            "public_key": pub.hex(),
            "note": "The public half of the licence signing key. Commit this. "
                    "The private half stays in ~/.kiln/private.key and is never shared.",
        }, indent=2) + "\n", encoding="utf-8")
    return {"private": str(PRIVATE), "public": pub.hex(), "pinned": str(PIN) if pin else None}


def ledger_path() -> Path:
    """Follows KILN_HOME, so a test or a second machine keeps its own list."""
    return HOME / LEDGER


def _append_ledger(payload: dict, key: str) -> None:
    """The owner's record of what was issued. Never in the repository."""
    try:
        HOME.mkdir(parents=True, exist_ok=True)
        with ledger_path().open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(dict(payload, key=key)) + "\n")
        ledger_path().chmod(0o600)
    except OSError:
        pass          # a licence that was issued is still issued


def ledger() -> list[dict]:
    path = ledger_path()
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def status_of(payload: dict) -> str:
    try:
        expires = datetime.date.fromisoformat(payload.get("expires", ""))
    except ValueError:
        return "unknown"
    return "expired" if expires < datetime.date.today() else "valid"


def issue(tier: str, licensee: str, days: int = 365, note: str = "") -> str:
    if tier not in PAID:
        raise LicenceError([f"cannot issue a '{tier}' key; choose one of {', '.join(PAID)}"])
    if not PRIVATE.exists():
        raise LicenceError([f"no signing key at {PRIVATE}; run: kiln licence keygen"])
    today = datetime.date.today()
    payload = {
        "v": 1,
        "tier": tier,
        "licensee": licensee.strip() or "unnamed",
        "issued": today.isoformat(),
        "expires": (today + datetime.timedelta(days=days)).isoformat(),
        "id": secrets.token_hex(4),
    }
    if note:
        payload["note"] = note[:80]
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    sig = ed25519.sign(raw, PRIVATE.read_bytes())
    key = f"{PREFIX}.{_b64e(raw)}.{_b64e(sig)}"
    _append_ledger(payload, key)
    return key


def decode(key: str) -> dict:
    """Verify a key string. Returns the payload, or raises with the reason."""
    key = (key or "").strip()
    if not key.startswith(PREFIX + "."):
        raise LicenceError(["not a KILN licence key (expected it to start with KILN1.)"])
    parts = key.split(".")
    if len(parts) != 3:
        raise LicenceError(["a KILN key has three parts: KILN1.<payload>.<signature>"])
    pub = pinned()
    if not pub:
        raise LicenceError([
            "no public key is pinned in catalogue/licence-key.json",
            "the owner must run: kiln licence keygen",
        ])
    try:
        raw = _b64d(parts[1])
        sig = _b64d(parts[2])
    except (ValueError, base64.binascii.Error):
        raise LicenceError(["the key is not valid base64"])
    if not ed25519.verify(sig, raw, pub):
        raise LicenceError(["the signature does not verify against the pinned public key"])
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise LicenceError(["the payload is not JSON"])
    if payload.get("tier") not in PAID:
        raise LicenceError([f"the payload names an unknown tier: {payload.get('tier')}"])
    try:
        expires = datetime.date.fromisoformat(payload.get("expires", ""))
    except ValueError:
        raise LicenceError(["the payload has no usable expiry date"])
    if expires < datetime.date.today():
        raise LicenceError([f"this licence expired on {expires.isoformat()}"])
    return payload


def activate(key: str, path: Path | None = None) -> dict:
    payload = decode(key)
    dest = Path(path or STORE)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"key": key.strip(), **payload}, indent=2) + "\n",
                    encoding="utf-8")
    return payload


def active() -> dict | None:
    for path in (STORE, ROOT / "kiln.licence"):
        if not path.exists():
            continue
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        key = blob.get("key")
        if not key:
            continue
        try:
            return decode(key)
        except LicenceError:
            continue
    return None


# ---------------------------------------------------------------- resolution
def resolve(cli_tier: str | None = None) -> tuple[str, str, str]:
    """(tier, licensee, source). The explicit flag wins, then the environment,
    then a valid licence, then free."""
    lic = active()
    env = os.environ.get("KILN_TIER", "").strip().lower()

    if cli_tier:
        tier = ALIASES.get(cli_tier.strip().lower(), "")
        if not tier:
            raise LicenceError([f"unknown edition '{cli_tier}'; choose from {', '.join(TIERS)}"])
        if tier in PAID:
            if not lic or lic.get("tier") != tier:
                raise LicenceError([
                    f"--tier {tier} needs an active {tier} licence",
                    "run: kiln licence activate <key>",
                    "free builds need no key, and carry the sponsor block",
                ])
            return tier, lic.get("licensee", ""), "flag + licence"
        return tier, "", "flag"

    if env in PAID:
        if lic and lic.get("tier") == env:
            return env, lic.get("licensee", ""), "KILN_TIER + licence"
        raise LicenceError([f"KILN_TIER={env} needs an active {env} licence"])
    if env in ("free", "personal"):
        return "personal", "", "KILN_TIER"
    if env == "demo":
        return "demo", "", "KILN_TIER"

    if lic:
        return lic["tier"], lic.get("licensee", ""), "licence"
    return "personal", "", "default"


def describe(tier: str) -> dict:
    """What this tier puts into a generated app. Used by docs and by the build."""
    return {
        "personal": {"sponsor": True, "sponsor_page": True,
                     "attribution": "Built with KILN, hyperlinked, plus the author block",
                     "watermark": True, "features": "full"},
        "commercial": {"sponsor": False, "sponsor_page": False,
                       "attribution": "one line: Built with KILN",
                       "watermark": True, "features": "full, unlocked"},
        "demo": {"sponsor": True, "sponsor_page": True,
                 "attribution": "Built with KILN, hyperlinked",
                 "watermark": True, "features": "capped: " + ", ".join(sorted(DEMO_FEATURES))},
    }[tier]
