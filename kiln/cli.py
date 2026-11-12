"""Command line. No network, no key, no model, for every command except `llm`."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from . import catalog as cat
from . import compose, emit, guards, intent, spec as specmod, verify

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


def _prose(s: dict, intent_rows=None) -> str:
    job = []
    for f in s["features"]:
        job.append(f"- {f}")
    reasons = ""
    if intent_rows:
        reasons = "\n".join(f"- {r}" for r in intent_rows)
    failure = {
        "bad input": "the form refuses to save and names the field that is wrong",
        "no network": "everything keeps working; a note says the network is not needed",
        "storage full": "the change stays in memory, a banner says it will not survive a reload, export is offered",
        "corrupt state": "the bad state is copied aside under a :corrupt: key and the app resets",
    }
    return f"""## Pitch

{s['pitch']}

## The job

{chr(10).join(job)}

## The mechanic

One model, one list, one file. The entity is declared once and the list, the form,
the search index and the export all read from it, so nothing can drift.

## What it must NOT do

{chr(10).join('- ' + n for n in s['not'])}

## What it does when things go wrong

{chr(10).join(f"- **{k}** — {v}" for k, v in failure.items())}

## Done means

{chr(10).join('- ' + d for d in s['done_means'])}

## The data

Stored in `localStorage` under `kiln:{s['storage']['namespace']}`. Nothing leaves the device.
{f'## How this spec was derived{chr(10)}{chr(10)}{reasons}{chr(10)}' if reasons else ''}"""


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
    rows = s.pop("_intent", {}).get("reasons", [])
    specmod.validate(s, catalog, f"specs/{s['id']}.md")
    dest = Path(args.out or ROOT / "specs") / f"{s['id']}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    body = f"# {s['name']}\n\n```json kiln\n{json.dumps(s, indent=2)}\n```\n\n{_prose(s, rows)}"
    dest.write_text(body, encoding="utf-8")
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
    s = specmod.load(args.spec, catalog)
    plan = compose.plan(s, catalog)
    out = Path(args.out) / s["id"] if args.out else ROOT / "out" / s["id"]
    written = emit.write(plan, out)
    for path, size in written:
        print(f"  {size:>7}  {path}")
    print(f"\n{len(written)} files in {out}")
    if not args.no_verify:
        res = verify.check_app(out, catalog)
        res.print(verbose=False)
        if res.failed:
            print(f"\n{len(res.failed)} checks failed")
            return 1
        print("verified")
        verify.record({"cmd": "build", "spec": s["id"], "out": str(out),
                       "files": len(written), "result": "ok"})
    return 0


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
    print(f"\n{len(catalog['features'])} features, {len(catalog['kits'])} kits")
    return 0


def cmd_audit(args, catalog) -> int:
    rows = guards.audit(catalog, write=args.write)
    return guards.report(rows)


def cmd_preflight(args, catalog) -> int:
    return guards.report(guards.preflight())


def cmd_heartbeat(args, catalog) -> int:
    print(json.dumps(guards.heartbeat(), indent=2))
    return 0


def cmd_llm(args, catalog) -> int:
    """Optional. Never touches out/. Drafts a spec only."""
    print("KILN works without this. To enable spec drafting:")
    print("  1. put an OpenAI-compatible base URL and key in ~/.kiln/config.json")
    print('     {"base_url": "https://api.openai.com/v1", "model": "...", "key": "..."}')
    print("  2. run: kiln llm draft \"<phrase>\" --out specs/")
    print("\nThe model may only write into specs/. It cannot write out/.")
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

    p = sub.add_parser("compose", help="spec -> file plan")
    p.add_argument("spec")
    p.set_defaults(fn=cmd_compose)

    p = sub.add_parser("build", help="spec -> app")
    p.add_argument("spec")
    p.add_argument("-o", "--out")
    p.add_argument("--no-verify", action="store_true")
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("verify", help="check an emitted app")
    p.add_argument("dir", nargs="?")
    p.add_argument("--all", action="store_true")
    p.set_defaults(fn=cmd_verify)

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

    p = sub.add_parser("llm", help="optional BYOK spec drafting")
    p.add_argument("action", nargs="?", default="on")
    p.set_defaults(fn=cmd_llm)

    args = ap.parse_args(argv)
    try:
        catalog = cat.load()
    except cat.CatalogError as e:
        return _fail(e)

    if args.cmd == "verify" and not args.all and not args.dir:
        ap.error("verify needs a directory, or --all")

    try:
        return args.fn(args, catalog)
    except specmod.SpecError as e:
        return _fail(e)
    except (cat.CatalogError, emit.EmitError) as e:
        return _fail(e)


if __name__ == "__main__":
    sys.exit(main())
