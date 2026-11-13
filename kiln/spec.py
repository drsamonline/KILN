"""Spec loading, validation and the falsifiability lint.

One shape. A second shape is a validation error, never a warning.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

BLOCK = re.compile(r"```json\s+kiln\s*\n(.*?)\n```", re.S)
FIELD_TYPES = {"text", "longtext", "number", "date", "bool", "select", "tags",
               "currency_cents"}
REQUIRED_KEYS = ["id", "name", "tier", "category", "pitch", "features",
                 "entities", "storage", "done_means", "not"]
OPTIONAL_KEYS = ["pattern", "accent", "currency", "tracker"]

# A done-means must name something a person can watch happen.
# Stems, not inflections: "reloading" must match "reload".
VERBS = {"show", "hide", "save", "reload", "export", "import", "return",
         "refuse", "block", "count", "sort", "filter", "delete",
         "restore", "open", "print", "render", "persist", "replace", "draw"}

# A done-means must not be able to certify anything and everything.
VAGUE = ["works as expected", "works correctly", "does what it says",
         "does its job", "as described", "user-friendly", "properly",
         "and so on", "etc.", "good ux", "intuitive"]

FAILURE_KEYS = ["bad_input", "no_network", "storage_full", "corrupt_state"]
PROSE_REQUIRED = ["## Pitch", "## The job", "## The mechanic",
                  "## What it must NOT do",
                  "## What it does when things go wrong",
                  "## Done means", "## The data"]


class SpecError(Exception):
    """Raised with every problem found, not just the first."""

    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("\n".join(f"  - {p}" for p in self.problems))


def split(path) -> tuple[str, str]:
    """Return (machine block text, prose text)."""
    text = Path(path).read_text(encoding="utf-8")
    m = BLOCK.search(text)
    if not m:
        raise SpecError([f"{path}: no ```json kiln block found. See SPEC-SHAPE.md"])
    return m.group(1), text


def load(path, catalog=None) -> dict:
    raw, text = split(path)
    try:
        spec = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SpecError([f"{path}: machine block is not valid JSON: {e}"])
    problems = validate(spec, catalog, path)
    problems += lint_prose(text)
    if problems:
        raise SpecError(problems)
    spec["_path"] = str(path)
    return spec


def validate(spec, catalog=None, path="<spec>") -> list[str]:
    p: list[str] = []
    if not isinstance(spec, dict):
        return [f"{path}: machine block must be an object"]

    for k in REQUIRED_KEYS:
        if k not in spec:
            p.append(f"missing required key: {k}")
    if p:
        return p

    if not re.fullmatch(r"app-[a-z0-9][a-z0-9-]*", str(spec["id"])):
        p.append("id must look like app-<slug>")
    stem = Path(path).stem
    if path != "<spec>" and stem.startswith("app-") and stem != spec["id"]:
        p.append(f"id '{spec['id']}' does not match filename '{stem}'")
    if not 1 <= len(str(spec["name"])) <= 40:
        p.append("name must be 1-40 characters")
    if spec["tier"] not in (1, 2, 3):
        p.append("tier must be 1, 2 or 3")
    if not 10 <= len(str(spec["pitch"])) <= 140:
        p.append("pitch must be 10-140 characters")

    if catalog is not None:
        known = catalog["features"]
        unknown = [f for f in spec["features"] if f not in known]
        if unknown:
            p.append(f"features not in catalog: {', '.join(unknown)}")
    if len(set(spec["features"])) != len(spec["features"]):
        p.append("features contains duplicates")

    ents = spec["entities"]
    if not isinstance(ents, list) or not ents:
        p.append("entities must be a non-empty list")
        ents = []
    seen_ent = set()
    for e in ents:
        for k in ("name", "label", "fields"):
            if k not in e:
                p.append(f"entity missing key: {k}")
        if e.get("name") in seen_ent:
            p.append(f"duplicate entity name: {e.get('name')}")
        seen_ent.add(e.get("name"))
        fields = e.get("fields") or []
        if not fields:
            p.append(f"entity '{e.get('name')}' has no fields")
        seen_f = set()
        for f in fields:
            if f.get("type") not in FIELD_TYPES:
                p.append(f"field '{f.get('name')}' has unknown type '{f.get('type')}'")
            if f.get("name") in seen_f:
                p.append(f"duplicate field '{f.get('name')}' in '{e.get('name')}'")
            seen_f.add(f.get("name"))
            if f.get("type") == "select" and len(f.get("options") or []) < 2:
                p.append(f"select field '{f.get('name')}' needs at least two options")

    st = spec["storage"]
    if st.get("kind") != "localstorage":
        p.append("storage.kind must be 'localstorage'")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(st.get("namespace", ""))):
        p.append("storage.namespace must be lowercase letters, digits and hyphens")

    if "tracker" in spec:
        tr = spec["tracker"]
        if not isinstance(tr, dict):
            p.append("tracker must be an object")
        else:
            types = {f["name"]: f["type"] for e in ents for f in (e.get("fields") or [])}
            fld = tr.get("field")
            if fld not in types:
                p.append(f"tracker.field '{fld}' is not a field on any entity")
            elif types[fld] not in ("number", "currency_cents"):
                p.append(f"tracker.field '{fld}' must be number or currency_cents")
            goal = tr.get("goal")
            if not isinstance(goal, (int, float)) or isinstance(goal, bool) or goal <= 0:
                p.append("tracker.goal must be a number greater than zero")
            win = tr.get("window", 7)
            if not isinstance(win, int) or isinstance(win, bool) or not 1 <= win <= 90:
                p.append("tracker.window must be a whole number from 1 to 90")

    if "pattern" in spec and not re.fullmatch(r"[a-z][a-z0-9-]*", str(spec["pattern"])):
        p.append("pattern must be a slug, e.g. crud-list")
    if "currency" in spec and not (isinstance(spec["currency"], str) and 1 <= len(spec["currency"]) <= 3):
        p.append("currency must be a short symbol, e.g. \u20b9")
    if "accent" in spec and not re.fullmatch(r"#[0-9a-fA-F]{6}", str(spec["accent"])):
        p.append("accent must be #rrggbb")

    if not spec["not"]:
        p.append("'not' must list at least one thing the app refuses to do")

    p += lint_done_means(spec["done_means"], path)
    return p


def lint_done_means(entries, path="<spec>") -> list[str]:
    """The F-71 guard: a done-means that certifies nothing fails the build."""
    p = []
    if not entries:
        return ["done_means must have at least one entry"]
    for i, e in enumerate(entries):
        low = str(e).lower()
        if len(low) < 12:
            p.append(f"done_means[{i}] is too short to check")
            continue
        if not any(v in low for v in VERBS):
            p.append(f"done_means[{i}] names no observable outcome (needs one of: "
                     f"{', '.join(sorted(VERBS))})")
        for v in VAGUE:
            if v in low:
                p.append(f"done_means[{i}] uses a phrase that certifies nothing: '{v}'")
    return p


def lint_prose(text) -> list[str]:
    return [f"prose section missing: {h}" for h in PROSE_REQUIRED if h not in text]


def sections(text) -> dict:
    """Split the prose into {heading: body}."""
    out, cur, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = line[3:].strip(), []
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return out


def spec_paths(root=None) -> list[Path]:
    """Every spec in the repository, gallery included. One list, used everywhere."""
    from pathlib import Path as _P
    base = _P(root) if root else _P(__file__).resolve().parent.parent
    out = sorted(base.glob("specs/*.md")) + sorted(base.glob("specs/gallery/*.md"))
    return [f for f in out if f.name.lower() != "readme.md"]


def load_all(spec_dir, catalog=None) -> list[dict]:
    """Every spec in a directory. A broken spec is an error, not a skip."""
    specs, problems = [], []
    for f in sorted(Path(spec_dir).glob("*.md")):
        try:
            specs.append(load(f, catalog))
        except SpecError as e:
            problems += [f"{f.name}: {x}" for x in e.problems]
    if problems:
        raise SpecError(problems)
    return specs
