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
from . import compose, demo as demomod, emit, guards, intent, prose
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


def _build(spec_path, catalog, out_root, quiet=False):
    s = specmod.load(spec_path, catalog)
    plan = compose.plan(s, catalog)
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
        for f in sorted((ROOT / "specs").glob("app-*.md")):
            s, out, ok = _build(f, catalog, args.out or ROOT / "out", quiet=True)
            print(f"{'ok  ' if ok else 'FAIL'} {f.name:<24} {out}")
            bad += (not ok)
        print(f"\n{len(list((ROOT / 'specs').glob('app-*.md')))} apps, {bad} failing")
        return 1 if bad else 0

    s, out, ok = _build(args.spec, catalog, args.out or ROOT / "out", quiet=args.quiet)
    if ok and not args.no_verify:
        verify.record({"cmd": "build", "spec": s["id"], "out": str(out), "result": "ok"})
    return 0 if ok else 1


def cmd_verify(args, catalog) -> int:
    if args.all:
        bad = 0
        for f in sorted((ROOT / "specs").glob("app-*.md")):
            with tempfile.TemporaryDirectory() as td:
                res = verify.build_and_check(f, catalog, td)
                fails = res.failed
                print(f"{'ok  ' if not fails else 'FAIL'} {f.name}  "
                      f"{len(res.rows)} checks, {len(fails)} failed")
                for r in fails:
                    print(f"     - {r['level']} {r['name']} {r['detail']}")
                bad += bool(fails)
        print(f"\n{len(list((ROOT / 'specs').glob('app-*.md')))} specs, {bad} failing")
        return 1 if bad else 0
    res = verify.check_app(args.dir, catalog)
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

    _, app_dir, ok = _build(spec_path, catalog, args.out or ROOT / "out", quiet=True)
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


def cmd_catalog(args, catalog) -> int:
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
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("pipeline", help="idea -> spec -> app -> verify -> zip")
    p.add_argument("text")
    p.add_argument("--id")
    p.add_argument("-o", "--out")
    p.add_argument("--zip", action="store_true")
    p.set_defaults(fn=cmd_pipeline)

    p = sub.add_parser("verify", help="check an emitted app")
    p.add_argument("dir", nargs="?")
    p.add_argument("--all", action="store_true")
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("demo", help="build demo.html, a real app inlined in a page")
    p.add_argument("-o", "--out")
    p.set_defaults(fn=cmd_demo)

    p = sub.add_parser("studio", help="build studio.html, the browser version")
    p.add_argument("-o", "--out")
    p.set_defaults(fn=cmd_studio)

    p = sub.add_parser("catalog", help="features and kits")
    p.add_argument("--feature")
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
    except (specmod.SpecError, adoptmod.AdoptError) as e:
        return _fail(e)
    except (cat.CatalogError, emit.EmitError, ValueError) as e:
        return _fail(e)


if __name__ == "__main__":
    sys.exit(main())
