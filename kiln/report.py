"""One command, every gate, one page.

A status page is only worth reading if it cannot lie. Every number here is produced
by running the gate, not by copying a claim from a document. The date comes from the
last commit rather than the clock, so the same tree produces the same page.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from . import __version__
from . import changelog as chlogmod
from . import guards, sizes, spec as specmod, verify

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "docs" / "status.html"


def _git(*args) -> str:
    try:
        out = subprocess.run(["git"] + list(args), cwd=str(ROOT),
                             capture_output=True, text=True)
        return out.stdout.strip()
    except Exception:
        return ""


def gather(catalog, run_verify: bool = True) -> dict:
    """Run every gate and collect the result. Nothing here is copied from a doc."""
    rows = guards.audit(catalog)
    failed = [r for r in rows if not r.ok and not r.skip]
    skipped = [r for r in rows if r.skip]

    specs = []
    if run_verify:
        for f in specmod.spec_paths(ROOT):
            with tempfile.TemporaryDirectory() as td:
                res = verify.build_and_check(f, catalog, td)
                specs.append({"name": f.name, "checks": len(res.rows),
                              "failed": len(res.failed)})

    m = sizes.measure(catalog)
    versions = chlogmod.parse(chlogmod.SOURCE.read_text(encoding="utf-8"))
    # the page must not contain anything that changes when the page is committed:
    # no commit hash, no commit count. The date comes from the version's own
    # changelog entry, which is fixed for that version.
    dated = next((v["date"] for v in versions if v["version"] == f"v{__version__}"), "")
    return {
        "version": __version__,
        "date": dated or _git("log", "-1", "--format=%cs") or "",
        "guards_total": len(rows),
        "guards_failed": len(failed),
        "guards_skipped": len(skipped),
        "failures": [{"name": r.name, "detail": r.detail} for r in failed],
        "skips": [{"name": r.name, "detail": r.detail} for r in skipped],
        "specs": specs,
        "specs_failed": len([s for s in specs if s["failed"]]),
        "sizes": m,
        "versions": len(versions),
    }


CSS = """
:root{--bg:#0f1116;--panel:#171a21;--line:#262b36;--ink:#e7ebf3;--muted:#98a2b3;
  --ok:#4ade80;--bad:#ff6b6b;--warn:#f59e0b}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:900px;margin:0 auto;padding:28px 20px 60px}
h1{font-size:26px;margin:0 0 4px}
.sub{color:var(--muted);margin:0 0 22px;font-size:13px}
.verdict{display:flex;gap:14px;align-items:center;padding:16px 18px;border-radius:12px;
  border:1px solid var(--line);background:var(--panel);margin:0 0 20px}
.verdict b{font-size:22px}
.verdict.pass{border-color:var(--ok)} .verdict.fail{border-color:var(--bad)}
table{border-collapse:collapse;width:100%;margin:0 0 20px;font-size:13.5px}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:var(--panel);font-weight:600;color:var(--muted);font-size:12px;
  text-transform:uppercase;letter-spacing:.05em}
td.n{text-align:right;font-variant-numeric:tabular-nums}
.ok{color:var(--ok)} .bad{color:var(--bad)} .muted{color:var(--muted)}
code{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;background:var(--panel);
  padding:1px 5px;border-radius:4px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);
  margin:26px 0 10px}
"""


def build(catalog, run_verify: bool = True) -> str:
    g = gather(catalog, run_verify)
    ok = g["guards_failed"] == 0 and g["specs_failed"] == 0
    verdict = ("Everything passes" if ok else "Something fails")
    m = g["sizes"]

    fail_rows = "".join(
        f'<tr><td class="bad">{f["name"]}</td><td class="muted">{f["detail"]}</td></tr>'
        for f in g["failures"]) or (
        '<tr><td class="ok">none</td><td class="muted">every guard passed</td></tr>')
    skip_rows = "".join(
        f'<tr><td class="muted">{s["name"]}</td><td class="muted">{s["detail"]}</td></tr>'
        for s in g["skips"]) or '<tr><td class="muted">none</td><td></td></tr>'
    spec_rows = "".join(
        f'<tr><td>{s["name"]}</td><td class="n">{s["checks"]}</td>'
        f'<td class="n {"ok" if not s["failed"] else "bad"}">{s["failed"]}</td></tr>'
        for s in g["specs"]) or '<tr><td class="muted">not run</td><td></td><td></td></tr>'

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KILN status</title><style>{CSS}</style></head>
<body><main>
<h1>KILN status</h1>
<p class="sub">v{g['version']} · {g['date']} · every number below was produced by
running the gate, and none is copied from a document</p>

<div class="verdict {'pass' if ok else 'fail'}">
  <b class="{'ok' if ok else 'bad'}">{'PASS' if ok else 'FAIL'}</b>
  <span>{verdict}: {g['guards_total'] - g['guards_failed'] - g['guards_skipped']} of
  {g['guards_total']} guards, {len(g['specs']) - g['specs_failed']} of {len(g['specs'])}
  specs.</span>
</div>

<h2>Gates</h2>
<table><tbody>
<tr><td>guards</td><td class="n {'ok' if not g['guards_failed'] else 'bad'}">{g['guards_failed']} failed</td><td class="n">{g['guards_total']} run</td></tr>
<tr><td>specs</td><td class="n {'ok' if not g['specs_failed'] else 'bad'}">{g['specs_failed']} failed</td><td class="n">{len(g['specs'])} built</td></tr>
<tr><td>skipped</td><td class="n muted">{g['guards_skipped']}</td><td class="muted">a skipped gate is a decision, not a pass</td></tr>
<tr><td>changelog versions</td><td class="n">{g['versions']}</td><td class="muted">one entry per release</td></tr>
</tbody></table>

<h2>Every failure</h2>
<table><thead><tr><th>Guard</th><th>Detail</th></tr></thead><tbody>{fail_rows}</tbody></table>

<h2>Every skip</h2>
<table><thead><tr><th>Guard</th><th>Detail</th></tr></thead><tbody>{skip_rows}</tbody></table>

<h2>Sizes, measured</h2>
<table><tbody>
<tr><td>a plain notes app</td><td class="n">{m['app']} KB</td></tr>
<tr><td>smallest of {m['specs']}</td><td class="n">{m['smallest']} KB</td></tr>
<tr><td>largest of {m['specs']}</td><td class="n">{m['largest']} KB</td></tr>
<tr><td>studio.html</td><td class="n">{m['studio']} KB</td></tr>
<tr><td>demo.html</td><td class="n">{m['demo']} KB</td></tr>
<tr><td>enforced ceiling</td><td class="n">{m['ceiling']} KB</td></tr>
</tbody></table>

<h2>Specs built</h2>
<table><thead><tr><th>Spec</th><th class="n">checks</th><th class="n">failed</th></tr></thead>
<tbody>{spec_rows}</tbody></table>

<p class="sub">Generated by <code>kiln report</code>. It carries no commit hash and no
commit count: either would change the moment the page was committed, and a page that
cannot match its own tree is worse than none.</p>
</main></body></html>
"""
