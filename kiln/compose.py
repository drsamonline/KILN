"""Compose: spec -> file plan. No writes, no side effects, no model."""
from __future__ import annotations

import datetime
import json
from pathlib import Path

from . import __version__, catalog as cat, licence as lic

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates" / "app"


def fnv1a64(text: str) -> str:
    """The same hash the runtime recomputes. Cheap, deterministic, both sides."""
    h = 0xCBF29CE484222325
    for byte in text.encode("utf-8"):
        h ^= byte
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return format(h, "016x")


def canonical(model) -> str:
    return json.dumps(model, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def plan(spec, catalog, tier="personal", licensee="", with_docs=False) -> list[dict]:
    """The full file plan. Deterministic: same spec and tier, same plan, byte for byte."""
    features = cat.expand(spec["features"], catalog)
    if tier == "demo":
        # the online demo is deliberately less capable than the real build
        features = [f for f in features if f in lic.DEMO_FEATURES]
        if "crud" not in features and "crud" in catalog["features"]:
            features = ["crud"] + features
    kits = cat.resolve_kits(features, catalog)
    ent = spec["entities"][0] if spec["entities"] else {"name": "value", "label": "Value", "fields": []}
    today = datetime.date.today().isoformat()

    model = {
        "id": spec["id"],
        "name": spec["name"],
        "namespace": spec["storage"]["namespace"],
        "version": 1,
        "accent": spec.get("accent", "#7c9cff"),
        "currency": spec.get("currency", "\u20b9"),
        "tracker": spec.get("tracker"),
        "progress": spec.get("progress"),
        "calculator": spec.get("calculator"),
        "i18n": spec.get("i18n"),
        "converter": spec.get("converter"),
        "wizard": spec.get("wizard"),
        "detail": spec.get("detail"),
        "totals": spec.get("totals"),
        "board": spec.get("board"),
        "calendar": spec.get("calendar"),
        "features": features,
        "entities": spec["entities"],
        "assertions": [catalog["features"][f]["assertion"] for f in features],
        "not": spec["not"],
    }

    canon = canonical(model)
    build = {
        "tier": tier,
        "version": __version__,
        "fp": fnv1a64(canon),
        "spec": spec["id"],
        "licensee": licensee or "",
        "licence": catalog["licence"]["badge"],
        "licence_url": "https://polyformproject.org/licenses/noncommercial/1.0.0/",
        "home": "https://github.com/drsamonline/KILN",
        "sponsor": dict(lic.SPONSOR) if tier in ("personal", "demo") else {},
    }

    ctx = {
        "TITLE": spec["name"],
        "ID": spec["id"],
        "PITCH": spec["pitch"],
        "DATE": today,
        "ACCENT": spec.get("accent", "#7c9cff"),
        "MODEL_JSON": json.dumps(model, indent=2),
        "FEATURES": ", ".join(features),
        "KITS": ", ".join(sorted(kits)),
        "ENTITY": ent["label"],
        "ENTITY_PLURAL": _plural(ent["label"]),
        "NAMESPACE": spec["storage"]["namespace"],
        "ASSERTIONS": "\n".join(f"- {catalog['features'][f]['assertion']}" for f in features),
        "NOT": "\n".join(f"- {n}" for n in spec["not"]),
        "LICENCE": catalog["licence"]["badge"],
        "LICENCE_ID": catalog["licence"]["id"],
        "SPEC_PATH": Path(spec.get("_path", f"specs/{spec['id']}.md")).name,
        "KILN_VERSION": __version__,
        "TIER": tier,
        "FINGERPRINT": build["fp"],
        "YEAR": today[:4],
        "OWNER": "Dr Sohil Momin",
        "LICENCE_URL": build["licence_url"],
        "BUILD_JSON": json.dumps(build, indent=2),
        "MODEL_CANON": json.dumps(canon).replace("</", "<\\/"),
    }

    app = [{"path": "index.html", "template": "index.html", "ctx": ctx,
            "strip": features}]
    if not with_docs:
        # §1.3: the output is one file. Everything else is optional furniture.
        return app
    return app + [
        {"path": "README.md", "template": "README.md", "ctx": ctx},
        {"path": "app.json", "inline": json.dumps(model, indent=2) + "\n", "ctx": ctx},
        {"path": "CHANGELOG.md", "template": "CHANGELOG.md", "ctx": ctx},
        {"path": "LICENSE", "inline": _licence_text(catalog), "ctx": ctx},
        {"path": ".github/workflows/build-apps.yml", "template": "build-apps.yml", "ctx": ctx},
        {"path": "tests/smoke.py", "template": "smoke.py", "ctx": ctx},
    ]


def _plural(label):
    if label.endswith("y") and len(label) > 1:
        return label[:-1] + "ies"
    if label.endswith(("s", "sh", "ch", "x")):
        return label + "es"
    return label + "s"


def _licence_text(catalog):
    lic = catalog["licence"]
    return (f"{lic['badge']}\n\n"
            f"Licence id: {lic['id']}\n\n"
            "This application is source-available under the PolyForm Noncommercial\n"
            "licence. Read the full text at\n"
            "https://polyformproject.org/licenses/noncommercial/1.0.0/\n\n"
            "Generated by KILN. The generated application is yours to modify;\n"
            "the spec it came from is the source of truth.\n")
