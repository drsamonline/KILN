"""Explain what a spec will produce, before you trust it.

The numbers are not estimates: the spec is built into a temporary directory and
measured, so an explanation that says 41 KB is an explanation of a real build.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from . import catalog as cat
from . import compose, spec as specmod, verify


def explain(spec_path, catalog, tier: str = "personal") -> dict:
    """Never raises for a bad spec: explaining the failure is the job."""
    try:
        s = specmod.load(spec_path, catalog)
    except specmod.SpecError as e:
        return {"spec": str(spec_path), "ok": False,
                "problems": getattr(e, "problems", [str(e)])}
    problems = specmod.validate(s, catalog, str(spec_path))
    if problems:
        return {"spec": str(spec_path), "ok": False, "problems": problems}

    declared = list(s["features"])
    expanded = cat.expand(declared, catalog)
    added = [f for f in expanded if f not in declared]
    pattern = cat.patterns().get(s.get("pattern") or "", {})
    fields = [{"entity": e["name"], "field": f["name"], "type": f["type"]}
              for e in s["entities"] for f in (e.get("fields") or [])]

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / s["id"]
        res = verify.build_and_check(spec_path, catalog, out, tier=tier)
        size = (out / "index.html").stat().st_size if (out / "index.html").exists() else 0
        failed = [{"level": r["level"], "check": r["name"], "detail": r["detail"]}
                  for r in res.failed]
        passed = sum(1 for r in res.rows if r["ok"] and not r["skip"])

    return {
        "spec": str(spec_path),
        "ok": not failed,
        "id": s["id"],
        "name": s["name"],
        "pattern": pattern.get("id", s.get("pattern")),
        "pattern_status": pattern.get("status", "none"),
        "features_declared": declared,
        "features_added_by_requires": added,
        "features_emitted": expanded,
        "fields": fields,
        "files": 1,
        "checks_run": passed + len(failed),
        "checks_failed": failed,
        "size_bytes": size,
        "size_kb": round(size / 1024, 1),
    }


def render(e: dict) -> str:
    if not e.get("ok") and e.get("problems"):
        return ("this spec would not build:\n" +
                "\n".join(f"  - {p}" for p in e["problems"]))
    lines = [
        f"{e['name']}  ({e['id']})",
        f"  pattern     {e['pattern']}  [{e['pattern_status']}]",
        f"  capabilities {', '.join(e['features_emitted'])}",
    ]
    if e["features_added_by_requires"]:
        lines.append(f"  added by requires  {', '.join(e['features_added_by_requires'])}")
    if e["fields"]:
        lines.append("  fields")
        for f in e["fields"]:
            lines.append(f"    {f['entity']}.{f['field']:<16} {f['type']}")
    else:
        lines.append("  fields      none (this archetype has no entity)")
    lines += [
        f"  output      {e['files']} file, {e['size_kb']} KB",
        f"  checks      {e['checks_run']} run, {len(e['checks_failed'])} failed",
    ]
    for f in e["checks_failed"]:
        lines.append(f"    FAIL {f['level']} {f['check']}  {f['detail']}")
    return "\n".join(lines)
