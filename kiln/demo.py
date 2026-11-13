"""Build demo.html: every spec in the gallery, some of them runnable.

The apps in the frame are built at `demo` tier — features capped, export and
import off, a banner that says so. What you can click here is deliberately less
than what the compiler produces, and the page says which is which and why.
"""
from __future__ import annotations

import html
import json
import tempfile
from pathlib import Path

from . import compose, emit, spec as specmod

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates" / "demo" / "index.html"
SPEC_DIR = ROOT / "specs"

# A clinical log holds patient data. It is not going to run in a public page.
EXCLUDE = {"clinical", "health"}
# how many apps the public page actually runs. The rest are listed with their spec.
LIVE_MAX = 4


def gallery(catalog) -> list[dict]:
    """Every spec, with a demo build where that is allowed."""
    out = []
    files = sorted(SPEC_DIR.glob("app-*.md")) + sorted((SPEC_DIR / "gallery").glob("*.md"))
    for f in files:
        s = specmod.load(f, catalog)
        # every spec is listed; only a few are run live, and the page says so
        runnable = s["category"] not in EXCLUDE and len([a for a in out if a["runnable"]]) < LIVE_MAX
        entry = {
            "id": s["id"],
            "name": s["name"],
            "pitch": s["pitch"],
            "category": s["category"],
            "tier": s["tier"],
            "features": s["features"],
            "runnable": runnable,
            "reason": "" if runnable else (
                f"holds {s['category']} data, so it is not run in a public page"
                if s["category"] in EXCLUDE else
                "not run here: the page runs a capped few. It builds locally in one command"),
            "html": "",
            "size": "",
            "spec": json.dumps({k: v for k, v in s.items() if not k.startswith("_")}, indent=2),
        }
        if runnable:
            plan = compose.plan(s, catalog, tier="demo")
            with tempfile.TemporaryDirectory() as td:
                emit.write(plan, td)
                app = (Path(td) / "index.html").read_text(encoding="utf-8")
            entry["html"] = app
            entry["size"] = f"{len(app.encode('utf-8')) / 1024:.1f} KB"
            entry["demo_features"] = [x for x in s["features"] if x in ("crud", "search", "theme", "sort")]
        out.append(entry)
    return out


def build(catalog) -> str:
    apps = gallery(catalog)
    runnable = [a for a in apps if a["runnable"]]
    payload = json.dumps({
        "apps": apps,
        "runnable": len(runnable),
        "total": len(apps),
    }, ensure_ascii=False)
    tpl = TPL.read_text(encoding="utf-8")
    ctx = {
        "PAYLOAD": payload.replace("</", "<\\/"),
        "TOTAL": str(len(apps)),
        "RUNNABLE": str(len(runnable)),
        "BLOCKED": str(len(apps) - len(runnable)),
        "FIRST_ID": runnable[0]["id"] if runnable else "",
        "FIRST_HTML": html.escape(runnable[0]["html"], quote=True) if runnable else "",
    }
    for k, v in ctx.items():
        tpl = tpl.replace("{{" + k + "}}", str(v))
    return tpl


def write(catalog, dest) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(build(catalog), encoding="utf-8")
    return dest
