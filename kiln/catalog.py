"""The catalog: features, kits, categories. Bounded on purpose."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = ROOT / "catalog"


class CatalogError(Exception):
    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("\n".join(f"  - {p}" for p in self.problems))


def _read(name):
    return json.loads((CATALOG_DIR / name).read_text(encoding="utf-8"))


def load() -> dict:
    feats = _read("features.json")["features"]
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


def coverage(catalog) -> list[tuple[str, str, str]]:
    """(feature, kit, assertion) for the README table."""
    return [(f, d["kit"], d["assertion"]) for f, d in catalog["features"].items()]
