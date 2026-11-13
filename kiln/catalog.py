"""The catalog: features, kits, categories. Bounded on purpose."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "catalogue"


class CatalogError(Exception):
    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("\n".join(f"  - {p}" for p in self.problems))


def _read(name):
    return json.loads((CATALOG_DIR / name).read_text(encoding="utf-8"))


def load() -> dict:
    feats = _read("capabilities.json")["features"]
    kits = _read("kits.json")["kits"]
    cats = _read("categories.json")
    problems = []
    for fid, f in feats.items():
        if f.get("kit") not in kits:
            problems.append(f"feature '{fid}' names unknown kit '{f.get('kit')}'")
        for req in f.get("requires", []):
            if req not in feats:
                problems.append(f"feature '{fid}' requires unknown feature '{req}'")
        if not f.get("assertion"):
            problems.append(f"feature '{fid}' has no assertion")
    if problems:
        raise CatalogError(problems)
    return {"features": feats, "kits": kits,
            "categories": cats["categories"], "licence": cats["licence"]}


def expand(features, catalog) -> list[str]:
    """Close over `requires`, detect unknown and conflicting features.

    Returns the features in catalog order so output is byte-identical between runs.
    """
    known = catalog["features"]
    problems = []
    unknown = [f for f in features if f not in known]
    if unknown:
        problems.append(f"unknown features: {', '.join(unknown)}")
    if problems:
        raise CatalogError(problems)

    want, stack = set(), list(features)
    while stack:
        f = stack.pop()
        if f in want:
            continue
        want.add(f)
        stack.extend(known[f].get("requires", []))

    for f in want:
        for c in known[f].get("conflicts", []):
            if c in want:
                problems.append(f"feature '{f}' conflicts with '{c}'")
    if problems:
        raise CatalogError(sorted(set(problems)))
    return [f for f in known if f in want]


def resolve_kits(features, catalog) -> dict:
    """feature -> kit, grouped as kit -> [features]. Unknown kit is fatal."""
    out = {}
    for f in features:
        kit = catalog["features"][f]["kit"]
        if kit not in catalog["kits"]:
            raise CatalogError([f"feature '{f}' names unknown kit '{kit}'"])
        out.setdefault(kit, []).append(f)
    return out


REGISTRY_DIR = CATALOG_DIR / "features"
FAMILIES = {
    "F1": "entity", "F2": "field", "F3": "validate", "F4": "view", "F5": "table",
    "F6": "form", "F7": "dashboard", "F8": "nav", "F9": "data-ops", "F10": "schedule",
    "F11": "users", "F12": "feedback", "F13": "settings", "F14": "a11y-i18n",
    "F15": "help-integrity",
}
REQUIRED_KEYS = ["id", "family", "name", "spec_keys", "emitter_hook",
                 "verify_check", "docs_anchor", "status"]


def registry() -> dict:
    """catalogue/features/<id>.json, loaded. A broken entry raises, never skips."""
    out, problems = {}, []
    if not REGISTRY_DIR.exists():
        return {}
    for f in sorted(REGISTRY_DIR.glob("*.json")):
        try:
            e = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{f.name}: not JSON ({exc})")
            continue
        missing = [k for k in REQUIRED_KEYS if k not in e]
        if missing:
            problems.append(f"{f.name}: missing {', '.join(missing)}")
            continue
        if e["id"] != f.stem:
            problems.append(f"{f.name}: id '{e['id']}' does not match the filename")
        if e["family"] not in FAMILIES:
            problems.append(f"{f.name}: unknown family '{e['family']}'")
        if e["status"] not in ("emitted", "planned"):
            problems.append(f"{f.name}: status must be emitted or planned")
        out[e["id"]] = e
    if problems:
        raise CatalogError(problems)
    return out


PATTERN_DIR = CATALOG_DIR / "patterns"


def patterns() -> dict:
    """catalogue/patterns/<id>.json — an archetype, with the checks it implies."""
    out = {}
    if not PATTERN_DIR.exists():
        return out
    for f in sorted(PATTERN_DIR.glob("*.json")):
        e = json.loads(f.read_text(encoding="utf-8"))
        if e.get("id") != f.stem:
            raise CatalogError([f"{f.name}: id does not match the filename"])
        out[e["id"]] = e
    return out


def emitted_types(reg) -> set:
    """Runtime field types that a registry entry claims, and that exist."""
    return {e["runtime_type"] for e in reg.values()
            if e["family"] == "F2" and e["status"] == "emitted" and e.get("runtime_type")}


def coverage(catalog) -> list[tuple[str, str, str]]:
    """(feature, kit, assertion) for the README table."""
    return [(f, d["kit"], d["assertion"]) for f, d in catalog["features"].items()]
