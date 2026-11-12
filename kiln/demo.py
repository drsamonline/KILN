"""Build demo.html: a real generated app, running inside the page.

Nothing is a mock. The app in the frame is the same file `kiln build` emits,
and `kiln audit` fails if the demo drifts from the spec it claims to show.
"""
from __future__ import annotations

import html
import json
import tempfile
from pathlib import Path

from . import compose, emit, spec as specmod

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates" / "demo" / "index.html"
SPEC = ROOT / "specs" / "app-notes.md"


def build(catalog, spec_path=None) -> str:
    s = specmod.load(spec_path or SPEC, catalog)
    plan = compose.plan(s, catalog)
    with tempfile.TemporaryDirectory() as td:
        emit.write(plan, td)
        app = (Path(td) / "index.html").read_text(encoding="utf-8")
    tpl = TPL.read_text(encoding="utf-8")
    ctx = {
        "APP_SRCDOC": html.escape(app, quote=True),
        "APP_SOURCE": html.escape(app, quote=False),
        "SPEC_JSON": html.escape(json.dumps(
            {k: v for k, v in s.items() if not k.startswith("_")}, indent=2), quote=False),
        "APP_NAME": s["name"],
        "APP_ID": s["id"],
        "PITCH": s["pitch"],
        "FEATURES": ", ".join(s["features"]),
        "SIZE": f"{len(app.encode('utf-8')) / 1024:.1f} KB",
        "FIELDS": ", ".join(f["name"] for f in s["entities"][0]["fields"]),
    }
    for k, v in ctx.items():
        tpl = tpl.replace("{{" + k + "}}", str(v))
    return tpl


def write(catalog, dest) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(build(catalog), encoding="utf-8")
    return dest
