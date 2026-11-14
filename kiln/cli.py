"""Command line. No network, no key, no model, for every command except `llm`."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from . import adopt as adoptmod
from . import catalog as cat
from . import changelog as chlogmod
from . import report as reportmod
from . import completions as compmod
from . import sizes as sizesmod
from . import compose, demo as demomod, emit, explain as explainmod
from . import guards, guide as guidemod, intent
from . import licence as lic
from . import prose
from . import prompt as promptmod
from . import spec as specmod
from . import studio as studiomod
from . import verify

ROOT = Path(__file__).resolve().parent.parent


def _fail(e) -> int:
    problems = getattr(e, "problems", None)
    if problems:
        print("problems:")
        for p in problems:
            print("  - " + str(p))
    else:
        print(f"error: {e}")
    return 2


def _write_spec(s, catalog, dest) -> Path:
    specmod.validate(s, catalog, f"{s['id']}.md")
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    body = f"# {s['name']}\n\n```json kiln\n{json.dumps(s, indent=2)}\n```\n\n{prose.render(s, catalog)}"
    dest.write_text(body, encoding="utf-8")
    return dest


def _build(spec_path, catalog, out_root, quiet=False, tier=None, with_docs=False):
    s = specmod.load(spec_path, catalog)
    tier, licensee, source = lic.resolve(tier)
    if not quiet:
        print(f"  edition {tier} ({source})" + (f" for {licensee}" if licensee else ""))
        print(f"  layout  {'index.html plus docs' if with_docs else 'one file (index.html)'}")
    plan = compose.plan(s, catalog, tier=tier, licensee=licensee, with_docs=with_docs)
    out = Path(out_root) / s["id"]
    written = emit.write(plan, out)
    if not quiet:
        for path, size in written:
            print(f"  {size:>7}  {path}")
        print(f"\n{len(written)} files in {out}")
    res = verify.check_app(out, catalog)
    res.print(verbose=False)
    if res.failed:
        print(f"\n{len(res.failed)} checks failed")
        return s, out, False
    if not quiet:
        print("verified")
    return s, out, True


def cmd_intake(args, catalog) -> int:
    r = intent.parse(args.text, catalog)
    if args.json:
        print(json.dumps(r, indent=2))
        return 0
    print(f"confidence  {r['confidence']}")
    print(f"entity      {r['entity']['name']}")
    print(f"features    {', '.join(r['features'])}")
    print("fields      " + ", ".join(f"{f['name']}:{f['type']}" for f in r["fields"]))
    if r["reasons"]:
        print("why:")
        for x in r["reasons"]:
            print("  - " + x)
    if r["unmatched"]:
        print("unmatched   " + ", ".join(r["unmatched"]))
    return 0


def cmd_new(args, catalog) -> int:
    s = intent.to_spec(args.text, catalog, spec_id=args.id)
    pattern = getattr(args, "pattern", None)
    if pattern:
        pats = cat.patterns()
        if pattern not in pats:
            return _fail(cat.CatalogError([f"unknown pattern '{pattern}'; "
                                           f"have: {', '.join(sorted(pats)) or 'none'}"]))
        defaults = pats[pattern].get("spec_defaults", {})
        s["pattern"] = pattern
        for k in ("features", "tier"):
            if k in defaults:
                s[k] = defaults[k]
        s["tier"] = defaults.get("tier", s.get("tier", 1))
    reasons = s.pop("_intent", {}).get("reasons", [])
    dest = Path(args.out or ROOT / "specs") / f"{s['id']}.md"
    _write_spec(s, catalog, dest)
    body = dest.read_text(encoding="utf-8")
    filled = prose.fill(body, s, catalog, reasons)[0] if reasons else body
    if filled != body:
        dest.write_text(filled, encoding="utf-8")
    print(f"wrote {dest}")
    print("next: python3 -m kiln build " + str(dest))
    return 0


def cmd_compose(args, catalog) -> int:
    s = specmod.load(args.spec, catalog)
    plan = compose.plan(s, catalog)
    for item in plan:
        kind = "inline" if "inline" in item else item["template"]
        print(f"{item['path']:<44} <- {kind}")
    print(f"\n{len(plan)} files")
    return 0


def cmd_build(args, catalog) -> int:
    if args.all:
        bad = 0
        for f in specmod.spec_paths(ROOT):
            s, out, ok = _build(f, catalog, args.out or ROOT / "out", quiet=True,
                                tier=getattr(args, "tier", None),
                                with_docs=getattr(args, "with_docs", False))
            print(f"{'ok  ' if ok else 'FAIL'} {f.name:<24} {out}")
            bad += (not ok)
        print(f"\n{len(specmod.spec_paths(ROOT))} apps, {bad} failing")
        return 1 if bad else 0

    s, out, ok = _build(args.spec, catalog, args.out or ROOT / "out",
                        quiet=args.quiet, tier=getattr(args, "tier", None),
                        with_docs=getattr(args, "with_docs", False))
    if ok and not args.no_verify:
        verify.record({"cmd": "build", "spec": s["id"], "out": str(out), "result": "ok"})
    return 0 if ok else 1


def cmd_verify(args, catalog) -> int:
    if args.all:
        bad = 0
        for f in specmod.spec_paths(ROOT):
            with tempfile.TemporaryDirectory() as td:
                res = verify.build_and_check(f, catalog, td)
                fails = res.failed
                print(f"{'ok  ' if not fails else 'FAIL'} {f.name}  "
                      f"{len(res.rows)} checks, {len(fails)} failed")
                for r in fails:
                    print(f"     - {r['level']} {r['name']} {r['detail']}")
                bad += bool(fails)
        print(f"\n{len(specmod.spec_paths(ROOT))} specs, {bad} failing")
        return 1 if bad else 0
    res = verify.check_app(args.dir, catalog)
    if getattr(args, "golden", False) or getattr(args, "update_golden", False):
        g = verify.golden(args.dir, update=getattr(args, "update_golden", False))
        res.rows.extend(g.rows)
    if getattr(args, "json", False):
        report = {
            "app": str(args.dir),
            "ok": not res.failed,
            "counts": {
                "checks": len(res.rows),
                "passed": sum(1 for r in res.rows if r["ok"] and not r["skip"]),
                "failed": len(res.failed),
                "skipped": sum(1 for r in res.rows if r["skip"]),
            },
            "checks": res.rows,
        }
        print(json.dumps(report, indent=2))
        return 1 if res.failed else 0
    res.print(verbose=True)
    if res.failed:
        print(f"\n{len(res.failed)} of {len(res.rows)} checks failed")
        return 1
    print(f"\nall {len(res.rows)} checks pass")
    return 0


def cmd_prompt(args, catalog) -> int:
    text = promptmod.fill(**{
        "APP_IDEA": args.idea,
        "WHO_USES_IT": args.who,
        "WHAT_THEY_RECORD": args.record,
        "PLATFORM": args.platform,
        "MUST_NOT": args.must_not,
    })
    left = promptmod.unfilled(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
        if left:
            print("placeholders still to replace: " + ", ".join(left))
        return 0
    print(text)
    if left:
        print("\n# placeholders still to replace: " + ", ".join(left), file=sys.stderr)
    return 0


def cmd_adopt(args, catalog) -> int:
    s, rep, dest = adoptmod.adopt(args.file, catalog, outdir=args.out)
    if rep:
        print(f"{len(rep)} repair(s):")
        for r in rep:
            print("  - " + r)
    else:
        print("no repairs needed")
    print(f"\nwrote {dest}")
    if args.build:
        _, out, ok = _build(dest, catalog, args.out_dir or ROOT / "out")
        return 0 if ok else 1
    print("next: python3 -m kiln build " + str(dest))
    return 0


def cmd_explain(args, catalog) -> int:
    """What this spec will produce, measured on a real build."""
    e = explainmod.explain(args.spec, catalog, tier=getattr(args, "tier", "personal"))
    if args.json:
        print(json.dumps(e, indent=2))
    else:
        print(explainmod.render(e))
    return 0 if e.get("ok") else 1


def cmd_completions(args, catalog=None) -> int:
    """Generated from the parser that just ran, so it cannot describe a stale CLI."""
    parser = getattr(args, "_parser", None)
    if parser is None:
        print("completions needs the parser; run it from the command line")
        return 2
    try:
        print(compmod.build(args.shell, parser), end="")
    except ValueError as e:
        print(str(e))
        return 2
    return 0


def cmd_report(args, catalog) -> int:
    """Run every gate and write one page. Nothing on it is copied from a doc."""
    g = reportmod.gather(catalog, run_verify=not args.no_verify)
    if args.json:
        print(reportmod.as_json(g), end="")
        return 0 if g["guards_failed"] == 0 else 1
    if args.write:
        reportmod.TARGET.parent.mkdir(parents=True, exist_ok=True)
        reportmod.TARGET.write_text(reportmod.build(catalog, run_verify=False)
                                    if args.no_verify else reportmod.build(catalog),
                                    encoding="utf-8")
        print(f"wrote {reportmod.TARGET}")
    if args.badge:
        reportmod.BADGE.parent.mkdir(parents=True, exist_ok=True)
        reportmod.BADGE.write_text(reportmod.badge(g), encoding="utf-8")
        print(f"wrote {reportmod.BADGE}")
    print(f"  version   {g['version']}  {g['date']}")
    print(f"  guards    {g['guards_total'] - g['guards_failed'] - g['guards_skipped']} "
          f"of {g['guards_total']} pass, {g['guards_skipped']} skipped")
    for f in g["failures"]:
        print(f"    FAIL {f['name']}  {f['detail']}")
    ok = g["guards_failed"] == 0
    if not args.write:
        print("  (nothing written: pass --write to save docs/status.html)")
    return 0 if ok else 1


def cmd_changelog(args, catalog) -> int:
    """Render CHANGELOG.md as a printable page."""
    html = chlogmod.build(catalog)
    if args.write:
        chlogmod.TARGET.parent.mkdir(parents=True, exist_ok=True)
        chlogmod.TARGET.write_text(html, encoding="utf-8")
        versions = chlogmod.parse(chlogmod.SOURCE.read_text(encoding="utf-8"))
        print(f"wrote {chlogmod.TARGET.relative_to(Path.cwd()) if chlogmod.TARGET.is_relative_to(Path.cwd()) else chlogmod.TARGET}"
              f"  ({len(versions)} versions, {len(html) // 1024} KB)")
        print("print it: open it in a browser and use Print to PDF")
        return 0
    current = chlogmod.TARGET.read_text(encoding="utf-8") if chlogmod.TARGET.exists() else ""
    if current != html:
        print("docs/changelog.html is stale — run: python3 -m kiln changelog --write")
        return 1
    print("docs/changelog.html matches CHANGELOG.md")
    return 0


def cmd_sizes(args, catalog) -> int:
    """Measure the real sizes, and rewrite every doc that states one."""
    m = sizesmod.measure(catalog)
    if args.write:
        changed = []
        for rel in sizesmod.CLAIMS:
            p = Path(rel)
            if not p.exists():
                continue
            before = p.read_text(encoding="utf-8")
            after = sizesmod.rewrite(before, m)
            if after != before:
                p.write_text(after)
                changed.append(rel)
        print(sizesmod.table(m))
        print()
        print("rewrote: " + (", ".join(changed) if changed else "nothing, already current"))
        return 0
    bad = sizesmod.check(catalog)
    print(sizesmod.table(m))
    if bad:
        print()
        for rel, why in bad:
            print(f"  STALE {rel}: {why}")
        print()
        print("run: python3 -m kiln sizes --write")
        return 1
    print()
    print("every stated size matches the build")
    return 0


def cmd_guide(args, catalog) -> int:
    """Regenerate the two guides that are written from the catalogue."""
    if args.check:
        want = guidemod.build(catalog)
        stale = [n for n, text in want.items()
                 if not (ROOT / n).exists() or (ROOT / n).read_text(encoding="utf-8") != text]
        if stale:
            print("stale: " + ", ".join(stale))
            print("run: python3 -m kiln guide")
            return 1
        print(f"{len(want)} guides are current")
        return 0
    for p in guidemod.write(catalog):
        print(f"wrote {p.relative_to(ROOT)}  ({p.stat().st_size} bytes)")
    return 0


def cmd_studio(args, catalog) -> int:
    dest = Path(args.out or ROOT / "studio.html")
    studiomod.write(catalog, dest)
    size = dest.stat().st_size
    print(f"wrote {dest}  ({size / 1024:.1f} KB)")
    print("open it in any browser, on any device. It needs nothing else.")
    return 0


def cmd_demo(args, catalog) -> int:
    dest = Path(args.out or ROOT / "demo.html")
    demomod.write(catalog, dest)
    print(f"wrote {dest}  ({dest.stat().st_size / 1024:.1f} KB)")
    print("the app inside it is the one kiln build emits, inlined")
    return 0


def cmd_pipeline(args, catalog) -> int:
    """idea -> spec -> app -> verify -> zip, in one command."""
    s = intent.to_spec(args.text, catalog, spec_id=args.id)
    reasons = s.pop("_intent", {}).get("reasons", [])
    spec_path = Path(args.out or ROOT / "out") / f"{s['id']}.md"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    body = f"# {s['name']}\n\n```json kiln\n{json.dumps(s, indent=2)}\n```\n\n{prose.render(s, catalog, reasons)}"
    spec_path.write_text(body, encoding="utf-8")
    specmod.validate(s, catalog, spec_path.name)
    print(f"1. spec    {spec_path}")

    _, app_dir, ok = _build(spec_path, catalog, args.out or ROOT / "out", quiet=True,
                            tier=getattr(args, "tier", None))
    print(f"2. app     {app_dir}")
    if not ok:
        print("stopped: the app did not verify")
        return 1
    print("3. verify  passed")

    if args.zip:
        z = app_dir.parent / f"{s['id']}.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(app_dir.rglob("*")):
                if p.is_file():
                    zf.write(p, p.relative_to(app_dir))
        print(f"4. package {z}  ({z.stat().st_size / 1024:.1f} KB)")
    print("\nopen " + str(app_dir / "index.html"))
    return 0


def cmd_licence(args, catalog) -> int:
    action = args.action
    if action in (None, "status"):
        tier, licensee, source = lic.resolve()
        print(f"edition     {tier}  ({source})")
        if licensee:
            print(f"licensee    {licensee}")
        act = lic.active()
        if act:
            print(f"expires     {act.get('expires')}   id {act.get('id')}")
        else:
            print("expires     -")
        d = lic.describe(tier)
        print(f"sponsor     {'yes' if d['sponsor'] else 'no'}")
        print(f"attribution {d['attribution']}")
        print(f"features    {d['features']}")
        print(f"pinned key  {'yes' if lic.pinned() else 'no — run: kiln licence keygen'}")
        return 0

    if action == "tiers":
        print(f"{'edition':<12} {'sponsor':<9} attribution")
        for t_ in lic.TIERS:
            d = lic.describe(t_)
            print(f"{t_:<12} {('yes' if d['sponsor'] else 'no'):<9} {d['attribution']}")
        d = lic.describe("demo")
        print(f"{'(demo)':<12} {'yes':<9} {d['attribution']} — online demo only, not an edition")
        return 0

    if action == "list":
        rows = lic.ledger()
        if not rows:
            print("no keys have been issued from this machine")
            print(f"ledger: {lic.ledger_path()}")
            return 0
        if args.json:
            print(json.dumps(rows, indent=2))
            return 0
        print(f"{'id':<10} {'edition':<11} {'licensee':<26} {'issued':<11} {'expires':<11} status")
        for r in rows:
            print(f"{r.get('id',''):<10} {r.get('tier',''):<11} {str(r.get('licensee',''))[:25]:<26} "
                  f"{r.get('issued',''):<11} {r.get('expires',''):<11} {lic.status_of(r)}")
        print(f"\n{len(rows)} key(s), ledger {lic.ledger_path()}")
        return 0

    if action == "keygen":
        out = lic.keygen(pin=not args.no_pin)
        print("private key  " + out["private"] + "   (chmod 600, never commit this)")
        print("public key   " + out["public"])
        if out["pinned"]:
            print("pinned in    " + out["pinned"] + "   (commit this file)")
        print("\nissue a licence with: kiln licence issue --to \"Name\" --tier commercial")
        return 0

    if action == "issue":
        key = lic.issue(args.tier, args.to or "unnamed", days=args.days, note=args.note or "")
        if args.out:
            Path(args.out).write_text(key + "\n", encoding="utf-8")
            print(f"wrote {args.out}")
        else:
            print(key)
        return 0

    if action == "verify":
        try:
            payload = lic.decode(args.key)
        except lic.LicenceError as e:
            return _fail(e)
        print(json.dumps(payload, indent=2))
        return 0

    if action == "activate":
        try:
            payload = lic.activate(args.key)
        except lic.LicenceError as e:
            return _fail(e)
        print(f"activated {payload['tier']} for {payload['licensee']}, expires {payload['expires']}")
        return 0

    print(f"unknown action: {action}")
    return 2


def cmd_catalog(args, catalog) -> int:
    if getattr(args, "registry", False):
        reg = cat.registry()
        want = args.family
        rows = [e for e in reg.values() if not want or e["family"] == want]
        print(f"{'id':<26} {'family':<7} {'status':<9} note")
        for e in sorted(rows, key=lambda x: (x["family"], x["id"])):
            print(f"{e['id']:<26} {e['family']:<7} {e['status']:<9} {e.get('note','')}")
        print(f"\n{len(rows)} entries; "
              f"{sum(1 for e in rows if e['status']=='emitted')} emitted, "
              f"{sum(1 for e in rows if e['status']=='planned')} planned")
        return 0

    if args.feature:
        f = catalog["features"].get(args.feature)
        if not f:
            print(f"unknown feature: {args.feature}")
            return 2
        print(json.dumps(f, indent=2))
        return 0
    print(f"{'feature':<10} {'kit':<14} assertion")
    for fid, kit, assertion in cat.coverage(catalog):
        print(f"{fid:<10} {kit:<14} {assertion[:60]}")
    print(f"\n{len(catalog['features'])} features, {len(catalog['kits'])} kits, all bundled")
    return 0


def cmd_audit(args, catalog) -> int:
    rows = guards.audit(catalog, write=args.write)
    return guards.report(rows)


def cmd_preflight(args, catalog) -> int:
    return guards.report(guards.preflight())


def cmd_heartbeat(args, catalog) -> int:
    print(json.dumps(guards.heartbeat(), indent=2))
    return 0


def cmd_doctor(args, catalog) -> int:
    """What this machine can do, with nothing installed."""
    rows = [
        ("python", sys.version.split()[0]),
        ("node (optional, js syntax check)", shutil.which("node") or "absent"),
        ("git (optional, read-at-sha)", shutil.which("git") or "absent"),
        ("network needed", "no"),
        ("features", str(len(catalog["features"]))),
        ("kits bundled", str(len(catalog["kits"]))),
        ("templates", str(len(list((ROOT / "templates").rglob("*.*"))))),
    ]
    for k, v in rows:
        print(f"{k:<34} {v}")
    print("\nready" if True else "")
    return 0


def cmd_llm(args, catalog) -> int:
    """Optional. Never touches out/. Drafts a spec only."""
    print("KILN works without this, and this command calls nothing.")
    print("To use a model, use the copy-paste bridge instead:")
    print("  python3 -m kiln prompt --idea \"a tea log with tags\"")
    print("  ... paste into any chat window ...")
    print("  python3 -m kiln adopt reply.md --build")
    print("\nNo key is stored, no endpoint is called, nothing leaves this machine.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="kiln", description="Spec in. Finished app out.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("intake", help="phrase -> spec patch")
    p.add_argument("text")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_intake)

    p = sub.add_parser("new", help="phrase -> spec file")
    p.add_argument("text")
    p.add_argument("--id")
    p.add_argument("--pattern", help="an archetype from catalogue/patterns/")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("prompt", help="print the prompt to paste into any model")
    p.add_argument("--idea")
    p.add_argument("--who")
    p.add_argument("--record")
    p.add_argument("--platform")
    p.add_argument("--must-not")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_prompt)

    p = sub.add_parser("adopt", help="take a model's reply and make it a spec")
    p.add_argument("file")
    p.add_argument("--out")
    p.add_argument("--build", action="store_true")
    p.add_argument("--out-dir")
    p.set_defaults(fn=cmd_adopt)

    p = sub.add_parser("compose", help="spec -> file plan")
    p.add_argument("spec")
    p.set_defaults(fn=cmd_compose)

    p = sub.add_parser("build", help="spec -> app")
    p.add_argument("spec", nargs="?")
    p.add_argument("-o", "--out")
    p.add_argument("--all", action="store_true")
    p.add_argument("--no-verify", action="store_true")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--tier", choices=["personal", "commercial"],
                   help="what the build carries; paid editions need a licence")
    p.add_argument("--with-docs", action="store_true",
                   help="also emit README, app.json, CHANGELOG, LICENSE, workflow, smoke test")
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("pipeline", help="idea -> spec -> app -> verify -> zip")
    p.add_argument("text")
    p.add_argument("--id")
    p.add_argument("-o", "--out")
    p.add_argument("--zip", action="store_true")
    p.add_argument("--tier", choices=["personal", "commercial"])
    p.set_defaults(fn=cmd_pipeline)

    p = sub.add_parser("verify", help="check an emitted app")
    p.add_argument("dir", nargs="?")
    p.add_argument("--all", action="store_true")
    p.add_argument("--golden", action="store_true", help="compare with the accepted build")
    p.add_argument("--update-golden", action="store_true", help="accept this build as the baseline")
    p.add_argument("--json", action="store_true", help="evidence report, machine-readable")
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("demo", help="build demo.html, a real app inlined in a page")
    p.add_argument("-o", "--out")
    p.set_defaults(fn=cmd_demo)

    p = sub.add_parser("explain", help="what a spec will produce, before you trust it")
    p.add_argument("spec")
    p.add_argument("--tier", choices=["personal", "commercial"], default="personal")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_explain)

    p = sub.add_parser("completions", help="shell completions for bash, zsh or fish")
    p.add_argument("shell", choices=sorted(compmod.SHELLS))
    p.set_defaults(fn=cmd_completions)

    p = sub.add_parser("report", help="run every gate and write one status page")
    p.add_argument("--write", action="store_true")
    p.add_argument("--no-verify", action="store_true",
                   help="skip building the specs (faster, less evidence)")
    p.add_argument("--json", action="store_true", help="machine-readable summary")
    p.add_argument("--badge", action="store_true", help="write docs/badge.json")
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("changelog", help="render CHANGELOG.md as a printable page")
    p.add_argument("--write", action="store_true")
    p.set_defaults(fn=cmd_changelog)

    p = sub.add_parser("sizes", help="measure the real sizes and rewrite the docs")
    p.add_argument("--write", action="store_true")
    p.set_defaults(fn=cmd_sizes)

    p = sub.add_parser("guide", help="regenerate the generated guides")
    p.add_argument("--check", action="store_true", help="fail if a guide is stale")
    p.set_defaults(fn=cmd_guide)

    p = sub.add_parser("studio", help="build studio.html, the browser version")
    p.add_argument("-o", "--out")
    p.set_defaults(fn=cmd_studio)

    p = sub.add_parser("licence", help="tiers, keys, and what a build carries")
    p.add_argument("action", nargs="?",
                   choices=["status", "tiers", "keygen", "issue", "list", "verify", "activate"])
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("key", nargs="?")
    p.add_argument("--to", help="licensee name, for issue")
    p.add_argument("--tier", default="commercial", choices=["commercial"], help="the only edition that needs a key")
    p.add_argument("--days", type=int, default=365)
    p.add_argument("--note")
    p.add_argument("--out")
    p.add_argument("--no-pin", action="store_true", help="do not write the public key")
    p.set_defaults(fn=cmd_licence)

    p = sub.add_parser("catalogue", aliases=["catalog"], help="capabilities, kits, registry")
    p.add_argument("--feature")
    p.add_argument("--registry", action="store_true", help="the F1-F15 feature registry")
    p.add_argument("--family", help="filter the registry, e.g. F2")
    p.set_defaults(fn=cmd_catalog)

    p = sub.add_parser("audit", help="run the Forge-defect guards")
    p.add_argument("--write", action="store_true", help="regenerate INDEX.md")
    p.set_defaults(fn=cmd_audit)

    p = sub.add_parser("preflight", help="credential check, 404 vs permission")
    p.set_defaults(fn=cmd_preflight)

    p = sub.add_parser("heartbeat", help="write a dated heartbeat")
    p.set_defaults(fn=cmd_heartbeat)

    p = sub.add_parser("doctor", help="what this machine can do")
    p.set_defaults(fn=cmd_doctor)

    p = sub.add_parser("llm", help="where the optional model path went")
    p.add_argument("action", nargs="?", default="on")
    p.set_defaults(fn=cmd_llm)

    args = ap.parse_args(argv)
    args._parser = ap
    try:
        catalog = cat.load()
    except cat.CatalogError as e:
        return _fail(e)

    if args.cmd == "verify" and not args.all and not args.dir:
        ap.error("verify needs a directory, or --all")
    if args.cmd == "build" and not args.all and not args.spec:
        ap.error("build needs a spec, or --all")

    try:
        return args.fn(args, catalog)
    except (specmod.SpecError, adoptmod.AdoptError, lic.LicenceError) as e:
        return _fail(e)
    except (cat.CatalogError, emit.EmitError, ValueError) as e:
        return _fail(e)


if __name__ == "__main__":
    sys.exit(main())
