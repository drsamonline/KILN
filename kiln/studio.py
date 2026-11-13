"""Build studio.html: the same compiler, in a browser, for a phone.

One file. No network. The catalog and the runtime template are inlined, so the
studio cannot drift from the CLI: both are generated from the same sources.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import __version__

ROOT = Path(__file__).resolve().parent.parent
STUDIO = ROOT / "templates" / "studio" / "index.html"
APP = ROOT / "templates" / "app" / "index.html"

KEYS = ["VERSION", "KILN_VERSION", "LICENCE", "CATALOG_JSON", "TPL_JS",
        "PATTERNS_JSON", "GALLERY_JSON"]


def payload(catalog) -> dict:
    feats = {}
    for fid, d in catalog["features"].items():
        feats[fid] = {
            "label": d["label"],
            "aliases": d["aliases"],
            "requires": d.get("requires", []),
            "assertion": d["assertion"],
            "kit": d["kit"],
        }
    return {"features": feats, "licence": catalog["licence"]["badge"]}


def _gallery() -> list[dict]:
    """The sample specs, embedded so the browser can load them without a filesystem."""
    from . import spec as specmod
    out = []
    for f in sorted((ROOT / "specs" / "gallery").glob("*.md")):
        try:
            s = specmod.load(f, None) if False else specmod.parse_only(f)
        except Exception:
            continue
        out.append({"file": f.name, "name": s.get("name", f.stem),
                    "pattern": s.get("pattern", ""), "spec": s})
    return out


def _patterns() -> list[dict]:
    import json
    from . import catalog as cat
    pats = []
    for pid, p in sorted(cat.patterns().items()):
        pats.append({"id": pid, "name": p.get("name", pid),
                     "archetype": p.get("archetype"), "status": p.get("status"),
                     "requires": p.get("requires_capabilities", []),
                     "requires_fields": p.get("requires_fields", []),
                     "requires_keys": p.get("requires_keys", []),
                     "defaults": p.get("spec_defaults", {}),
                     "descriptor": p.get("descriptor", "")})
    return pats


def build(catalog) -> str:
    tpl = STUDIO.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    # "</" must not appear inside a JS string in an HTML document
    app_js = json.dumps(app, ensure_ascii=False).replace("</", "<\\/")
    ctx = {
        "VERSION": "1.0",
        "KILN_VERSION": __version__,
        "LICENCE": catalog["licence"]["badge"],
        "CATALOG_JSON": json.dumps(payload(catalog), ensure_ascii=False,
                                   separators=(",", ":")),
        "TPL_JS": app_js,
        "PATTERNS_JSON": json.dumps(_patterns(), ensure_ascii=False, separators=(",", ":")),
        "GALLERY_JSON": json.dumps(_gallery(), ensure_ascii=False, separators=(",", ":")),
    }
    out = tpl
    for k in KEYS:
        out = out.replace("{{" + k + "}}", str(ctx[k]))
    for k in KEYS:
        if "{{" + k + "}}" in tpl:
            continue
        raise ValueError(f"studio template does not use {{{{{k}}}}}")
    return out


def write(catalog, dest) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(build(catalog), encoding="utf-8")
    return dest
