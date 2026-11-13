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

ROOT = Path(__file__).resolve().parent.parent

# §1.3: the output is one file. The rest is optional furniture, emitted with --with-docs.
REQUIRED_FILES = ["index.html"]
DOCS_FILES = ["app.json", "README.md", "LICENSE", "CHANGELOG.md",
              "tests/smoke.py", ".github/workflows/build-apps.yml"]
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
    if model["entities"]:
        res.add("L3", "entity label is wired",
                model["entities"][0]["label"].lower() in html.lower())
    else:
        res.add("L3", "no entity, as the pattern declares", True, "calculator shape")
    return res


def check_pattern(spec, catalog, res=None) -> Result:
    """A spec that names a pattern must satisfy what that pattern promises."""
    res = res or Result()
    pid = spec.get("pattern")
    if not pid:
        return res
    pats = cat.patterns()
    if pid not in pats:
        res.add("L2", f"pattern {pid} exists", False, "catalogue/patterns/")
        return res
    pat = pats[pid]
    res.add("L2", f"pattern {pid} is emitted", pat.get("status") == "emitted")
    missing = [f for f in pat.get("requires_capabilities", []) if f not in spec["features"]]
    res.add("L2", f"pattern {pid}: required features present", not missing, ", ".join(missing))
    types = {f["type"] for e in spec["entities"] for f in e["fields"]}
    need = [t for t in pat.get("requires_fields", []) if t not in types]
    res.add("L2", f"pattern {pid}: required field types present", not need, ", ".join(need))
    sample = ROOT / pat.get("sample", "")
    res.add("L2", f"pattern {pid}: the sample spec exists", sample.exists(), str(pat.get("sample")))
    shot = ROOT / pat.get("screenshot", "")
    res.add("L2", f"pattern {pid}: the screenshot exists", shot.exists(), str(pat.get("screenshot")))
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

    files = sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file())
    if (d / "app.json").exists():
        for f in DOCS_FILES:
            p = d / f
            res.add("L3", f"docs file {f}", p.exists() and p.stat().st_size > 0)
        res.add("L3", "layout: single file plus docs", True, f"{len(files)} files")
    else:
        res.add("L3", "layout: exactly one file", files == ["index.html"],
                ", ".join(files))

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

    if "derived" in model["features"]:
        res.add("L5", "derived: a derive function is emitted", "function derive(" in html)
        res.add("L5", "derived: the panel is emitted", 'id="derived"' in html)
        res.add("L5", "derived: the tracker config reached the model",
                bool(model.get("tracker", {}).get("field")))
    if model.get("calculator"):
        res.add("L5", "calculator: the parser is emitted", "function evalFormula(" in html)
        res.add("L5", "calculator: eval and Function are not used",
                "eval(" not in html and "new Function(" not in html)
        res.add("L5", "calculator: the screen is emitted", 'id="calc"' in html)
        res.add("L5", "calculator: the formula reached the model",
                bool(model["calculator"].get("formula")))
        res.add("L5", "calculator: no entity, as the pattern declares",
                model.get("entities") == [])
    if "balance" in model["features"]:
        res.add("L5", "balance: the balance maths is emitted", "function balanceOf(" in html)
        res.add("L5", "balance: the reorder flag is emitted", "to reorder" in html)
        res.add("L5", "balance: the config reached the model",
                bool((model.get("balance") or {}).get("field")))
    if "timeline" in model["features"]:
        res.add("L5", "timeline: the grouping is emitted", "function groupByMonth(" in html)
        res.add("L5", "timeline: the view is emitted", "function renderTimeline(" in html)
        res.add("L5", "timeline: the config reached the model",
                bool((model.get("timeline") or {}).get("field")))
    if "relation" in model["features"]:
        res.add("L5", "relation: the lookup select is emitted",
                'f.type === "lookup"' in html)
        res.add("L5", "relation: a pointer resolves to a title",
                "function labelOf(" in html)
        res.add("L5", "relation: children can be listed", "function childrenOf(" in html)
        res.add("L5", "relation: the lookup reached the model",
                any(f.get("type") == "lookup"
                    for e in model.get("entities", []) for f in e.get("fields", [])))
    if "multi" in model["features"]:
        res.add("L5", "multi: more than one entity reached the model",
                len(model.get("entities", [])) >= 2)
        res.add("L5", "multi: the switcher is emitted", "function setEntity(" in html)
        res.add("L5", "multi: storage carries a set of lists", "data: DB" in html)
    if "dashboard" in model["features"]:
        res.add("L5", "dashboard: the metric maths is emitted", "function metricOf(" in html)
        res.add("L5", "dashboard: the panel is emitted", 'id="dash"' in html)
        res.add("L5", "dashboard: the cards reached the model",
                len((model.get("dashboard") or {}).get("cards", [])) >= 1)
    if "directory" in model["features"]:
        res.add("L5", "directory: the view is emitted", "function renderDirectory(" in html)
        res.add("L5", "directory: match highlighting is emitted", "function highlight(" in html)
        res.add("L5", "directory: the search box is enlarged and focused",
                'classList.add("big")' in html and ".focus()" in html)
        res.add("L5", "directory: the config reached the model",
                isinstance(model.get("directory"), dict))
    if "comparison" in model["features"]:
        res.add("L5", "comparison: the table is emitted", "function renderComparison(" in html)
        res.add("L5", "comparison: the best-value maths is emitted",
                "function columnBest(" in html)
        res.add("L5", "comparison: the config reached the model",
                len((model.get("comparison") or {}).get("columns", [])) >= 2)
    if "board" in model["features"]:
        res.add("L5", "board: the board is emitted", "function renderBoard(" in html)
        res.add("L5", "board: the grouping is emitted", "function groupBy(" in html)
        res.add("L5", "board: the markup exists", 'id="board"' in html)
        res.add("L5", "board: the config reached the model",
                bool((model.get("board") or {}).get("field")))
    if "calendar" in model["features"]:
        res.add("L5", "calendar: the grid is emitted", "function renderCalendar(" in html)
        res.add("L5", "calendar: the month maths is emitted", "function monthGrid(" in html)
        res.add("L5", "calendar: the markup exists", 'id="cal"' in html)
        res.add("L5", "calendar: the config reached the model",
                bool((model.get("calendar") or {}).get("field")))
    if "detail" in model["features"]:
        res.add("L5", "detail: the read view is emitted", "function openDetail(" in html)
        res.add("L5", "detail: the dialog exists", 'id="detail"' in html)
        res.add("L5", "detail: the row title opens it", "openDetail(r)" in html)
    if "totals" in model["features"]:
        res.add("L5", "totals: the sum is emitted", "function totalsOf(" in html)
        res.add("L5", "totals: the strip shows it", "totalsOf(rows, MODEL.totals)" in html)
        res.add("L5", "totals: the config reached the model",
                bool((model.get("totals") or {}).get("field")))
    if "convert" in model["features"]:
        res.add("L5", "convert: the conversion function is emitted", "function convertValue(" in html)
        res.add("L5", "convert: the screen is emitted", 'id="convert"' in html)
        res.add("L5", "convert: the unit table reached the model",
                len((model.get("converter") or {}).get("units", [])) >= 2)
    if "steps" in model["features"]:
        res.add("L5", "steps: the step renderer is emitted", "function renderStep(" in html)
        res.add("L5", "steps: Back, Next and Save exist",
                all(f'id="{x}"' in html for x in ("stepBack", "stepNext", "stepSave")))
        res.add("L5", "steps: the wizard config reached the model",
                len((model.get("wizard") or {}).get("steps", [])) >= 2)
    if "a11y" in model["features"]:
        res.add("L5", "a11y: a skip link is emitted", 'class="skip"' in html)
        res.add("L5", "a11y: a visible focus ring is emitted", ":focus-visible" in html)
        res.add("L5", "a11y: reduced motion is respected", "prefers-reduced-motion" in html)
        res.add("L5", "a11y: banners are a live region", 'aria-live="polite"' in html)
    if "i18n" in model["features"]:
        res.add("L5", "i18n: a dictionary is emitted", "const LANGS =" in html)
        res.add("L5", "i18n: the language list reached the model",
                isinstance(model.get("i18n", {}).get("languages"), list))
        res.add("L5", "i18n: the html lang attribute is set at runtime", 'setAttribute("lang"' in html)
        for code in (model.get("i18n") or {}).get("languages", []):
            # English is the EN table the runtime always carries; the others are inline
            found = ("const EN = {" in html) if code == "en" else (f"{code}: {{" in html)
            res.add("L5", f"i18n: a {code} dictionary exists", found)
    if "feedback" in model["features"]:
        res.add("L5", "feedback: the size banner is emitted", "SIZE_WARN" in html)
        res.add("L5", "feedback: the backup reminder is emitted", "lastExport" in html)
        res.add("L5", "feedback: exporting records the day", "markExport" in html)
    if "progress" in model["features"]:
        res.add("L5", "progress: a progressOf function is emitted", "function progressOf(" in html)
        res.add("L5", "progress: the bar is emitted", 'id="progress"' in html and 'role="progressbar"' in html)
        res.add("L5", "progress: the config reached the model",
                bool(model.get("progress", {}).get("field")))
    if "toggle" in model["features"]:
        res.add("L5", "toggle: a row checkbox is emitted", 'className = "tick"' in html)
        res.add("L5", "toggle: ticking saves immediately", "r[tickField] = tick.checked" in html)
    if "chart" in model["features"]:
        res.add("L5", "chart: inline svg is emitted", "sparkSvg(" in html and "<svg" in html)
        for lib in ("chart.js", "cdn.jsdelivr", "unpkg.com", "d3.min.js"):
            res.add("L5", f"chart: no library ({lib})", lib not in html.lower())

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


def build_and_check(spec_path, catalog, outdir, tier="personal", licensee="",
                    with_docs=False) -> Result:
    s = specmod.load(spec_path, catalog)
    plan = compose.plan(s, catalog, tier=tier, licensee=licensee, with_docs=with_docs)
    emit.write(plan, outdir)
    res = check_pattern(s, catalog)
    check_app(outdir, catalog, res=res)
    return res


def read_at(sha, path, repo="."):
    """L7: read the file as it is at the commit, not in the working tree."""
    p = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"cannot read {path} at {sha}: {p.stderr.strip()}")
    return p.stdout


# ------------------------------------------------------------------- golden
def golden_path(app_dir) -> Path:
    d = Path(app_dir)
    return d.parent / (d.name + ".golden.json")


def snapshot(app_dir) -> dict:
    import hashlib
    out = {}
    for f in sorted(Path(app_dir).rglob("*")):
        if f.is_file():
            out[str(f.relative_to(app_dir))] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def golden(app_dir, update=False) -> Result:
    """Compare this build with the last one that was accepted."""
    res = Result()
    p = golden_path(app_dir)
    now = snapshot(app_dir)
    if update or not p.exists():
        p.write_text(json.dumps(now, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        res.add("L6", "golden baseline written", True, f"{len(now)} files, {p.name}")
        return res
    try:
        was = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        res.add("L6", "golden baseline is readable", False, str(p))
        return res

    added = sorted(set(now) - set(was))
    removed = sorted(set(was) - set(now))
    changed = sorted(k for k in set(now) & set(was) if now[k] != was[k])
    res.add("L6", "no file added", not added, ", ".join(added))
    res.add("L6", "no file removed", not removed, ", ".join(removed))
    res.add("L6", "no file changed", not changed, ", ".join(changed))
    if changed:
        res.add("L6", "accept with --update-golden", True,
                f"{len(changed)} changed: {', '.join(changed[:4])}")
    return res


def record(entry, path="RUNS.jsonl"):
    """A completion is a command and its output. Nothing else counts."""
    import datetime
    row = dict(entry)
    row["at"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return row
