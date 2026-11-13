"""One measurement, written into every doc that states a size.

The numbers in the docs drifted: the README said a generated app was 21 KB when it
was 50, and the studio was called 50 KB when it was 208. This module measures the
real sizes and rewrites the claims, so the only way a doc can be wrong is if nobody
ran `kiln sizes --write` — and guard C20 fails the audit when that happens.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from . import catalog as cat
from . import compose, emit

ROOT = Path(__file__).resolve().parent.parent
CEILING_KB = 100

# every doc that states a size, and the phrasing it uses
CLAIMS = {
    "README.md": [
        (r"generated%20app-(\d+)%20KB", "app"),
        (r"one `index\.html` \(~(\d+) KB\)", "app"),
        (r"KILN Studio — (\d+) KB", "studio"),
        (r"typically \d+–\d+ KB", "band"),
    ],
    "index.html": [
        (r"A generated app — (\d+) KB", "app"),
    ],
    "INSTALL.md": [
        (r"copy `studio\.html` \((\d+) KB\)", "studio"),
    ],
    "docs/FAQ.md": [
        (r"About (\d+) KB\. Under (\d+) KB is the enforced budget\.", "faq"),
    ],
    "docs/PORTABILITY.md": [
        (r"The studio is (\d+) KB", "studio"),
        (r"\| `index\.html` \(generated app\) \| under (\d+) KB \| (\d+) KB \|", "portability_app"),
        (r"\| `studio\.html` \| under (\d+) KB \| (\d+) KB \|", "portability_studio"),
    ],
}


def _build_kb(spec_path: Path, catalog) -> int:
    s = spec_mod_load(spec_path, catalog)
    with tempfile.TemporaryDirectory() as td:
        plan = compose.plan(s, catalog, tier="personal")
        emit.write(plan, td)
        p = Path(td) / "index.html"
        return round(p.stat().st_size / 1024)


def spec_mod_load(path, catalog):
    from . import spec as specmod
    return specmod.load(path, catalog)


def measure(catalog) -> dict:
    specs = sorted((ROOT / "specs").glob("app-*.md")) + \
        sorted((ROOT / "specs" / "gallery").glob("*.md"))
    sizes = []
    for f in specs:
        try:
            sizes.append(_build_kb(f, catalog))
        except Exception:
            continue
    app = _build_kb(ROOT / "specs" / "app-notes.md", catalog)
    studio = round((ROOT / "studio.html").stat().st_size / 1024)
    demo = round((ROOT / "demo.html").stat().st_size / 1024)
    return {
        "app": app,
        "smallest": min(sizes) if sizes else app,
        "largest": max(sizes) if sizes else app,
        "band": (min(sizes), max(sizes)) if sizes else (app, app),
        "studio": studio,
        "demo": demo,
        "ceiling": CEILING_KB,
        "specs": len(specs),
    }


def rewrite(text: str, m: dict) -> str:
    import re
    lo, hi = m["band"]
    subs = [
        (r"generated%20app-\d+%20KB", f"generated%20app-{m['app']}%20KB"),
        (r"one `index\.html` \(~\d+ KB\)", f"one `index.html` (~{m['app']} KB)"),
        (r"KILN Studio — \d+ KB", f"KILN Studio — {m['studio']} KB"),
        (r"typically \d+–\d+ KB", f"typically {lo}–{hi} KB"),
        (r"A generated app — \d+ KB", f"A generated app — {m['app']} KB"),
        (r"copy `studio\.html` \(\d+ KB\)", f"copy `studio.html` ({m['studio']} KB)"),
        (r"About \d+ KB\. Under \d+ KB is the enforced budget\.",
         f"About {m['app']} KB. Under {m['ceiling']} KB is the enforced budget."),
        (r"The studio is \d+ KB", f"The studio is {m['studio']} KB"),
        (r"\| `index\.html` \(generated app\) \| under \d+ KB \| \d+ KB \|",
         f"| `index.html` (generated app) | under {m['ceiling']} KB | {m['app']} KB |"),
        (r"\| `studio\.html` \| under \d+ KB \| \d+ KB \|",
         f"| `studio.html` | under {m['ceiling'] * 3} KB | {m['studio']} KB |"),
    ]
    out = text
    for pat, rep in subs:
        out = re.sub(pat, rep, out)
    return out


def check(catalog) -> list[tuple[str, str]]:
    """Every stated size that disagrees with the measurement."""
    import re
    m = measure(catalog)
    bad = []
    for rel, patterns in CLAIMS.items():
        p = ROOT / rel
        if not p.exists():
            bad.append((rel, "missing"))
            continue
        text = p.read_text(encoding="utf-8")
        for pat, kind in patterns:
            if kind == "band":
                if not re.search(pat, text):
                    bad.append((rel, f"no size band: {pat}"))
                continue
            if not re.search(pat, text):
                bad.append((rel, f"claim vanished: {pat}"))
                continue
            fixed = re.sub(pat, lambda _m: _m.group(0), text)
            if rewrite(fixed, m) != fixed:
                bad.append((rel, f"stale size for {kind}: {pat}"))
    return bad


def table(m: dict) -> str:
    return "\n".join([
        f"generated app      {m['app']} KB  (a plain notes app)",
        f"smallest app       {m['smallest']} KB",
        f"largest app        {m['largest']} KB",
        f"studio.html        {m['studio']} KB",
        f"demo.html          {m['demo']} KB",
        f"enforced ceiling   {m['ceiling']} KB",
        f"specs measured     {m['specs']}",
    ])
