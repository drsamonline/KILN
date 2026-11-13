"""Verify: read the artifact, print evidence, exit non-zero on a defect.

Levels (see PLAN.md):
  L1 spec      L2 features   L3 plan     L4 js parse
  L5 smoke     L6 golden     L7 read-at-sha
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import catalog as cat
from . import compose, emit, spec as specmod

REQUIRED_FILES = [
    "index.html", "app.json", "README.md", "LICENSE", "CHANGELOG.md",
    "tests/smoke.py", ".github/workflows/build-apps.yml",
]
# The app may link out from About; it may never load anything from anywhere.
EXTERNAL = ['src="http', "src='http", "url(http", "@import", "fetch(", "XMLHttpRequest",
            "<script src", 'rel="stylesheet" href="http', "import(", "//cdn"]
STUBS = ["TODO", "FIXME", "lorem ipsum", "placeholder text", "<your"]


class Result:
    def __init__(self):
        self.rows = []

    def add(self, level, name, ok, detail="", skip=False):
        self.rows.append({"level": level, "name": name,
                          "ok": ok, "detail": detail, "skip": skip})

    @property
    def failed(self):
        return [r for r in self.rows if not r["ok"] and not r["skip"]]

    def print(self, verbose=True):
        for r in self.rows:
            if r["skip"]:
                tag = "SKIP"
            elif r["ok"]:
                tag = "ok  "
            else:
                tag = "FAIL"
            if verbose or tag != "ok  ":
                line = f"  {tag} {r['level']}  {r['name']}"
                if r["detail"]:
                    line += f"  ({r['detail']})"
                print(line)


def extract_model(html):
    m = re.search(r"const MODEL = (\{.*?\n\});", html, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def check_wiring(model, html, res=None) -> Result:
    """Every declared entity, field and namespace must appear in the artifact."""
    res = res or Result()
    for ent in model["entities"]:
        for fld in ent["fields"]:
            res.add("L3", f"field {ent['name']}.{fld['name']} is wired", fld["name"] in html)
    res.add("L3", "storage namespace is wired", model["namespace"] in html)
    res.add("L3", "entity label is wired", model["entities"][0]["label"].lower() in html.lower())
    return res


def check_app(d, catalog, res=None, run_smoke=True) -> Result:
    d = Path(d)
    res = res or Result()

    for f in REQUIRED_FILES:
        p = d / f
        res.add("L3", f"file {f}", p.exists() and p.stat().st_size > 0,
                "missing or empty" if not p.exists() else "")
    if not (d / "index.html").exists():
        return res

    html = (d / "index.html").read_text(encoding="utf-8")

    model = extract_model(html)
    res.add("L4", "embedded model parses", model is not None)
    if model is None:
        return res

    man = None
    if (d / "app.json").exists():
        try:
            man = json.loads((d / "app.json").read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            man = None
    res.add("L3", "app.json parses", man is not None)
    if man:
        res.add("L3", "manifest and model agree", man["id"] == model["id"],
                f"{man.get('id')} vs {model.get('id')}")
        res.add("L3", "manifest features match model",
                man["features"] == model["features"])

    unknown = [f for f in model["features"] if f not in catalog["features"]]
    res.add("L2", "every feature is in the catalog", not unknown, ", ".join(unknown))

    for f in model["features"]:
        if f in catalog["features"]:
            res.add("L2", f"feature {f} has an assertion",
                    bool(catalog["features"][f]["assertion"]))

    for bad in EXTERNAL:
        res.add("L5", f"no external reference: {bad}", bad not in html)
    for bad in STUBS:
        res.add("L5", f"no stub marker: {bad}", bad.lower() not in html.lower())

    check_wiring(model, html, res)
    res.add("L5", "corrupt state is handled", "corrupt" in html)
    res.add("L5", "quota failure is handled", "Storage is full" in html)
    res.add("L5", "offline is handled", "offline" in html.lower())
    res.add("L5", "escape helper exists", ("esc =" in html) or ("function esc" in html))

    # provenance: a build that lost its watermark is not a build we made
    build = None
    m = re.search(r"const BUILD = (\{.*?\n\});", html, re.S)
    if m:
        try:
            build = json.loads(m.group(1))
        except json.JSONDecodeError:
            build = None
    res.add("L5", "build record parses", build is not None)
    if build:
        res.add("L5", "fingerprint is 16 hex", bool(re.fullmatch(r"[0-9a-f]{16}", build.get("fp", ""))))
        res.add("L5", "tier is named", build.get("tier") in ("personal", "commercial", "demo"))
        res.add("L5", "the fingerprint in the head matches the record",
                f'content="{build["fp"]}"' in html)
        res.add("L5", "sponsor block matches the tier",
                bool(build.get("sponsor")) == (build.get("tier") in ("personal", "demo")))
        res.add("L5", "a generator comment is present", "generated by KILN" in html)
        if build.get("tier") == "demo":
            res.add("L5", "demo build says it is a demo", "Demo build." in html)

    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    res.add("L4", "exactly one inline script", len(scripts) == 1, str(len(scripts)))

    node = shutil.which("node")
    if node and scripts:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as t:
            t.write(scripts[0])
            tmp = t.name
        try:
            p = subprocess.run([node, "--check", tmp], capture_output=True, text=True)
            res.add("L4", "emitted javascript parses", p.returncode == 0,
                    (p.stderr or "").strip().splitlines()[0] if p.returncode else "")
        finally:
            Path(tmp).unlink(missing_ok=True)
    else:
        res.add("L4", "emitted javascript parses", False, "node not on PATH", skip=True)

    if run_smoke and (d / "tests/smoke.py").exists():
        p = subprocess.run([sys.executable, str(d / "tests/smoke.py")],
                           capture_output=True, text=True)
        res.add("L5", "the app's own smoke assertions", p.returncode == 0,
                (p.stdout or p.stderr).strip().splitlines()[-1] if p.stdout or p.stderr else "")
    return res


def build_and_check(spec_path, catalog, outdir, tier="personal", licensee="") -> Result:
    s = specmod.load(spec_path, catalog)
    plan = compose.plan(s, catalog, tier=tier, licensee=licensee)
    emit.write(plan, outdir)
    return check_app(outdir, catalog)


def read_at(sha, path, repo="."):
    """L7: read the file as it is at the commit, not in the working tree."""
    p = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"cannot read {path} at {sha}: {p.stderr.strip()}")
    return p.stdout


def record(entry, path="RUNS.jsonl"):
    """A completion is a command and its output. Nothing else counts."""
    import datetime
    row = dict(entry)
    row["at"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return row
