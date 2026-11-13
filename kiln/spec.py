"""Spec loading, validation and the falsifiability lint.

One shape. A second shape is a validation error, never a warning.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

BLOCK = re.compile(r"```json\s+kiln\s*\n(.*?)\n```", re.S)
FIELD_TYPES = {"text", "longtext", "number", "date", "bool", "select", "tags",
               "currency_cents", "duration", "lookup"}
REQUIRED_KEYS = ["id", "name", "tier", "category", "pitch", "features",
                 "entities", "storage", "done_means", "not"]
OPTIONAL_KEYS = ["pattern", "accent", "currency", "tracker", "progress",
                 "calculator", "i18n", "converter", "wizard", "detail", "totals",
                 "board", "calendar", "directory", "comparison", "dashboard"]
KNOWN_LANGS = {"en", "hi", "gu"}

# A done-means must name something a person can watch happen.
# Stems, not inflections: "reloading" must match "reload".
VERBS = {"show", "hide", "save", "reload", "export", "import", "return",
         "refuse", "block", "count", "sort", "filter", "delete",
         "restore", "open", "print", "render", "persist", "replace", "draw"}

# A done-means must not be able to certify anything and everything.
VAGUE = ["works as expected", "works correctly", "does what it says",
         "does its job", "as described", "user-friendly", "properly",
         "and so on", "etc.", "good ux", "intuitive"]

FAILURE_KEYS = ["bad_input", "no_network", "storage_full", "corrupt_state"]
PROSE_REQUIRED = ["## Pitch", "## The job", "## The mechanic",
                  "## What it must NOT do",
                  "## What it does when things go wrong",
                  "## Done means", "## The data"]


class SpecError(Exception):
    """Raised with every problem found, not just the first."""

    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("\n".join(f"  - {p}" for p in self.problems))


def split(path) -> tuple[str, str]:
    """Return (machine block text, prose text)."""
    text = Path(path).read_text(encoding="utf-8")
    m = BLOCK.search(text)
    if not m:
        raise SpecError([f"{path}: no ```json kiln block found. See SPEC-SHAPE.md"])
    return m.group(1), text


def parse_only(path):
    """Read the machine block without validating it. For the studio's gallery."""
    text = Path(path).read_text(encoding="utf-8")
    m = BLOCK.search(text)
    if not m:
        raise SpecError([f"{path}: no ```json kiln block found"])
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise SpecError([f"{path}: the block is not valid JSON ({e})"])


def load(path, catalog=None) -> dict:
    raw, text = split(path)
    try:
        spec = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SpecError([f"{path}: machine block is not valid JSON: {e}"])
    problems = validate(spec, catalog, path)
    problems += lint_prose(text)
    if problems:
        raise SpecError(problems)
    spec["_path"] = str(path)
    return spec


# a capability that cannot work without a block of its own
NEEDS_KEY = {
    "tracker": "tracker", "progress": "progress", "calculator": "calculator",
    "converter": "converter", "wizard": "wizard", "detail": "detail",
    "totals": "totals", "board": "board", "calendar": "calendar",
    "directory": "directory", "comparison": "comparison", "i18n": "i18n",
    "relation": "master_detail",
    "balance": "balance", "timeline": "timeline",
    "dashboard": "dashboard", "multi": "entities",
}


def validate(spec, catalog=None, path="<spec>") -> list[str]:
    p: list[str] = []
    if not isinstance(spec, dict):
        return [f"{path}: machine block must be an object"]

    for k in REQUIRED_KEYS:
        if k not in spec:
            p.append(f"missing required key: {k}")
    if p:
        return p

    if not re.fullmatch(r"app-[a-z0-9][a-z0-9-]*", str(spec["id"])):
        p.append("id must look like app-<slug>")
    stem = Path(path).stem
    if path != "<spec>" and stem.startswith("app-") and stem != spec["id"]:
        p.append(f"id '{spec['id']}' does not match filename '{stem}'")
    if not 1 <= len(str(spec["name"])) <= 40:
        p.append("name must be 1-40 characters")
    if spec["tier"] not in (1, 2, 3):
        p.append("tier must be 1, 2 or 3")
    if not 10 <= len(str(spec["pitch"])) <= 140:
        p.append("pitch must be 10-140 characters")

    if catalog is not None:
        known = catalog["features"]
        unknown = [f for f in spec["features"] if f not in known]
        if unknown:
            p.append(f"features not in catalog: {', '.join(unknown)}")
    if len(set(spec["features"])) != len(spec["features"]):
        p.append("features contains duplicates")

    ents = spec["entities"]
    if not isinstance(ents, list):
        p.append("entities must be a list")
        ents = []
    elif not ents:
        # an archetype may declare that it needs no entity at all
        pid = spec.get("pattern")
        needs = True
        if pid:
            try:
                from . import catalog as _cat
                needs = _cat.patterns().get(pid, {}).get("requires_entities", True)
            except Exception:
                needs = True
        if needs:
            p.append("entities must be a non-empty list (this pattern needs one)")
    seen_ent = set()
    for e in ents:
        for k in ("name", "label", "fields"):
            if k not in e:
                p.append(f"entity missing key: {k}")
        if e.get("name") in seen_ent:
            p.append(f"duplicate entity name: {e.get('name')}")
        seen_ent.add(e.get("name"))
        fields = e.get("fields") or []
        if not fields:
            p.append(f"entity '{e.get('name')}' has no fields")
        seen_f = set()
        for f in fields:
            if f.get("type") not in FIELD_TYPES:
                p.append(f"field '{f.get('name')}' has unknown type '{f.get('type')}'")
            if f.get("name") in seen_f:
                p.append(f"duplicate field '{f.get('name')}' in '{e.get('name')}'")
            seen_f.add(f.get("name"))
            if f.get("type") == "select" and len(f.get("options") or []) < 2:
                p.append(f"select field '{f.get('name')}' needs at least two options")

    st = spec["storage"]
    if st.get("kind") != "localstorage":
        p.append("storage.kind must be 'localstorage'")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(st.get("namespace", ""))):
        p.append("storage.namespace must be lowercase letters, digits and hyphens")

    if "tracker" in spec:
        tr = spec["tracker"]
        if not isinstance(tr, dict):
            p.append("tracker must be an object")
        else:
            types = {f["name"]: f["type"] for e in ents for f in (e.get("fields") or [])}
            fld = tr.get("field")
            if fld not in types:
                p.append(f"tracker.field '{fld}' is not a field on any entity")
            elif types[fld] not in ("number", "currency_cents"):
                p.append(f"tracker.field '{fld}' must be number or currency_cents")
            goal = tr.get("goal")
            if not isinstance(goal, (int, float)) or isinstance(goal, bool) or goal <= 0:
                p.append("tracker.goal must be a number greater than zero")
            win = tr.get("window", 7)
            if not isinstance(win, int) or isinstance(win, bool) or not 1 <= win <= 90:
                p.append("tracker.window must be a whole number from 1 to 90")

    field_names = {f["name"] for e in ents for f in (e.get("fields") or [])}

    for cap, key in NEEDS_KEY.items():
        if cap in (spec.get("features") or []) and key not in spec:
            p.append(f"the '{cap}' capability needs a '{key}' block: it cannot work without one")
    if "multi" in (spec.get("features") or []) and len(ents) < 2:
        p.append("the 'multi' capability needs at least two entities")
    if len(ents) > 1 and "multi" not in (spec.get("features") or []):
        p.append(f"{len(ents)} entities need the 'multi' capability in features")

    if "balance" in spec:
        bl = spec["balance"]
        if not isinstance(bl, dict):
            p.append("balance must be an object")
        else:
            names = {e["name"] for e in ents}
            for k in ("master", "child"):
                if bl.get(k) not in names:
                    p.append(f"balance.{k} names an entity that does not exist: {bl.get(k)}")
            types = {f["name"]: f for e in ents for f in (e.get("fields") or [])}
            fld = bl.get("field")
            if fld not in types:
                p.append(f"balance.field '{fld}' is not a field on any entity")
            elif types[fld]["type"] not in ("number", "currency_cents", "duration"):
                p.append("balance.field must be numeric")
            look = bl.get("lookup")
            if look not in types:
                p.append(f"balance.lookup '{look}' is not a field on any entity")
            elif types[look]["type"] != "lookup":
                p.append("balance.lookup must be the lookup field on the child")
            ro = bl.get("reorder")
            if ro is not None and ro not in types:
                p.append(f"balance.reorder '{ro}' is not a field on any entity")

    if "timeline" in spec:
        tl = spec["timeline"]
        if not isinstance(tl, dict):
            p.append("timeline must be an object")
        else:
            fld = tl.get("field")
            types = {f["name"]: f for e in ents for f in (e.get("fields") or [])}
            if fld not in types:
                p.append(f"timeline.field '{fld}' is not a field on any entity")
            elif types[fld]["type"] != "date":
                p.append("timeline.field must be a date field")

    if "master_detail" in spec:
        md = spec["master_detail"]
        if not isinstance(md, dict):
            p.append("master_detail must be an object")
        else:
            names = {e["name"] for e in ents}
            for k in ("master", "child"):
                if md.get(k) not in names:
                    p.append(f"master_detail.{k} names an entity that does not exist: {md.get(k)}")
            fld = md.get("field")
            types = {f["name"]: f for e in ents for f in (e.get("fields") or [])}
            if fld not in types:
                p.append(f"master_detail.field '{fld}' is not a field on any entity")
            elif types[fld]["type"] != "lookup":
                p.append("master_detail.field must be a lookup field")
            elif types[fld].get("entity") != md.get("master"):
                p.append("master_detail.field must point at the master entity")

    # a lookup must point at another declared entity
    for e in ents:
        for f in (e.get("fields") or []):
            if f.get("type") == "lookup":
                target = f.get("entity")
                if target not in {x["name"] for x in ents}:
                    p.append(f"lookup field '{f['name']}' points at an entity that does not exist: {target}")
                elif target == e["name"]:
                    p.append(f"lookup field '{f['name']}' points at its own entity")

    if "dashboard" in spec:
        db = spec["dashboard"]
        if not isinstance(db, dict):
            p.append("dashboard must be an object")
        else:
            cards = db.get("cards")
            if not isinstance(cards, list) or not cards:
                p.append("dashboard.cards must be a non-empty list")
                cards = []
            names = {e["name"] for e in ents}
            for i, card in enumerate(cards):
                if not isinstance(card, dict):
                    p.append(f"dashboard card {i + 1} must be an object")
                    continue
                if card.get("entity") not in names:
                    p.append(f"dashboard card {i + 1} names an entity that does not exist: {card.get('entity')}")
                m = card.get("metric", "count")
                if m not in ("count", "sum", "avg", "max", "min", "latest"):
                    p.append(f"dashboard card {i + 1} metric '{m}' is not count, sum, avg, max, min or latest")
                if m != "count" and not card.get("field"):
                    p.append(f"dashboard card {i + 1} needs a field for the '{m}' metric")
                elif m != "count":
                    types = {f["name"]: f["type"] for e in ents for f in (e.get("fields") or [])}
                    if card["field"] not in types:
                        p.append(f"dashboard card {i + 1} names a field that does not exist: {card['field']}")
                    elif types[card["field"]] not in ("number", "duration", "currency_cents"):
                        p.append(f"dashboard card {i + 1} field '{card['field']}' is not numeric")

    if "directory" in spec:
        dr = spec["directory"]
        if not isinstance(dr, dict):
            p.append("directory must be an object")
        else:
            for k in ("subtitle", "body"):
                if k in dr and dr[k] not in field_names:
                    p.append(f"directory.{k} '{dr[k]}' is not a field on any entity")
        if "directory" not in spec.get("features", []):
            p.append("a directory block needs the 'directory' capability in features")
        if "search" not in spec.get("features", []):
            p.append("a directory needs the 'search' capability: it is a search-first view")

    if "comparison" in spec:
        cp = spec["comparison"]
        if not isinstance(cp, dict):
            p.append("comparison must be an object")
        else:
            cols = cp.get("columns")
            if not isinstance(cols, list) or len(cols) < 2:
                p.append("comparison.columns must name at least two fields")
                cols = []
            for c in cols:
                if c not in field_names:
                    p.append(f"comparison.columns names a field that does not exist: {c}")
            hl = cp.get("highlight")
            if hl is not None:
                if not isinstance(hl, dict):
                    p.append("comparison.highlight must be an object of field: max|min")
                else:
                    for k, v in hl.items():
                        if v not in ("max", "min"):
                            p.append(f"comparison.highlight.{k} must be max or min")
        if "comparison" not in spec.get("features", []):
            p.append("a comparison block needs the 'comparison' capability in features")

    if "board" in spec:
        bd = spec["board"]
        if not isinstance(bd, dict):
            p.append("board must be an object")
        else:
            fld = bd.get("field")
            if fld not in field_names:
                p.append(f"board.field '{fld}' is not a field on any entity")
            else:
                types = {f["name"]: f["type"] for e in ents for f in (e.get("fields") or [])}
                if types[fld] != "select":
                    p.append("board.field must be a select field, because its options are the columns")
                else:
                    opts = [f for e in ents for f in (e.get("fields") or []) if f["name"] == fld][0].get("options") or []
                    if len(opts) < 2:
                        p.append("board.field needs at least two options, one per column")
        if "board" not in spec.get("features", []):
            p.append("a board block needs the 'board' capability in features")

    if "calendar" in spec:
        cd = spec["calendar"]
        if not isinstance(cd, dict):
            p.append("calendar must be an object")
        else:
            fld = cd.get("field")
            if fld not in field_names:
                p.append(f"calendar.field '{fld}' is not a field on any entity")
            else:
                types = {f["name"]: f["type"] for e in ents for f in (e.get("fields") or [])}
                if types[fld] != "date":
                    p.append("calendar.field must be a date field")
        if "calendar" not in spec.get("features", []):
            p.append("a calendar block needs the 'calendar' capability in features")

    if "detail" in spec:
        dt = spec["detail"]
        if not isinstance(dt, dict):
            p.append("detail must be an object")
        else:
            fld = dt.get("field")
            if fld is not None and fld not in field_names:
                p.append(f"detail.field '{fld}' is not a field on any entity")
            elif fld is not None:
                types = {f["name"]: f["type"] for e in ents for f in (e.get("fields") or [])}
                if types[fld] not in ("longtext", "text"):
                    p.append("detail.field must be longtext or text")
        if "detail" not in spec.get("features", []):
            p.append("a detail block needs the 'detail' capability in features")

    if "totals" in spec:
        tt = spec["totals"]
        if not isinstance(tt, dict):
            p.append("totals must be an object")
        else:
            fld = tt.get("field")
            if fld not in field_names:
                p.append(f"totals.field '{fld}' is not a field on any entity")
            else:
                types = {f["name"]: f["type"] for e in ents for f in (e.get("fields") or [])}
                if types[fld] not in ("number", "duration", "currency_cents"):
                    p.append("totals.field must be number, duration or currency_cents")
            if tt.get("format") not in (None, "duration", "number"):
                p.append("totals.format must be duration or number")
        if "totals" not in spec.get("features", []):
            p.append("a totals block needs the 'totals' capability in features")

    if "converter" in spec:
        cv = spec["converter"]
        if not isinstance(cv, dict):
            p.append("converter must be an object")
        else:
            units = cv.get("units")
            if not isinstance(units, list) or len(units) < 2:
                p.append("converter.units must list at least two units")
                units = []
            ids = set()
            for u in units:
                if not isinstance(u, dict) or not u.get("id"):
                    p.append("every converter unit needs an id")
                    continue
                if not re.fullmatch(r"[a-z0-9_]+", str(u["id"])):
                    p.append(f"converter unit id '{u['id']}' must be lowercase")
                if u["id"] in ids:
                    p.append(f"duplicate converter unit '{u['id']}'")
                ids.add(u["id"])
                f = u.get("factor")
                if not isinstance(f, (int, float)) or isinstance(f, bool) or f <= 0:
                    p.append(f"converter unit '{u['id']}' needs a positive factor")
            for k in ("default_from", "default_to"):
                if cv.get(k) not in ids:
                    p.append(f"converter.{k} must name one of the units")
            if "convert" not in spec.get("features", []):
                p.append("a converter spec must include the 'convert' capability")

    if "wizard" in spec:
        w = spec["wizard"]
        if not isinstance(w, dict):
            p.append("wizard must be an object")
        else:
            steps = w.get("steps")
            if not isinstance(steps, list) or len(steps) < 2:
                p.append("wizard.steps must list at least two steps")
                steps = []
            seen = set()
            for i, st in enumerate(steps):
                if not isinstance(st, dict) or not isinstance(st.get("fields"), list):
                    p.append(f"wizard step {i + 1} needs a fields list")
                    continue
                if not st["fields"]:
                    p.append(f"wizard step {i + 1} has no fields")
                for name in st["fields"]:
                    if name not in field_names:
                        p.append(f"wizard step {i + 1} names a field that does not exist: {name}")
                    if name in seen:
                        p.append(f"wizard field '{name}' appears in more than one step")
                    seen.add(name)
            if "steps" not in spec.get("features", []):
                p.append("a wizard spec must include the 'steps' capability")

    if "i18n" in spec:
        i = spec["i18n"]
        if not isinstance(i, dict):
            p.append("i18n must be an object")
        else:
            langs = i.get("languages")
            if not isinstance(langs, list) or len(langs) < 2:
                p.append("i18n.languages must list at least two languages")
            else:
                bad = [x for x in langs if x not in KNOWN_LANGS]
                if bad:
                    p.append(f"i18n.languages has no dictionary for: {', '.join(map(str, bad))} "
                             f"(known: {', '.join(sorted(KNOWN_LANGS))})")
                if "en" not in langs:
                    p.append("i18n.languages must include en as the fallback")
        if "i18n" not in spec.get("features", []):
            p.append("an i18n block needs the 'i18n' capability in features")

    if "calculator" in spec:
        if "formula" not in spec.get("features", []):
            p.append("a calculator spec must include the 'formula' capability")
        c = spec["calculator"]
        if not isinstance(c, dict):
            p.append("calculator must be an object")
        else:
            ins = c.get("inputs")
            if not isinstance(ins, list) or not ins:
                p.append("calculator.inputs must be a non-empty list")
                ins = []
            names = set()
            for i in ins:
                if not isinstance(i, dict) or not i.get("name"):
                    p.append("every calculator input needs a name")
                    continue
                if not re.fullmatch(r"[a-z][a-z0-9_]*", str(i["name"])):
                    p.append(f"calculator input '{i['name']}' must be lowercase snake_case")
                if i["name"] in names:
                    p.append(f"duplicate calculator input '{i['name']}'")
                names.add(i["name"])
            f = c.get("formula")
            if not isinstance(f, str) or not f.strip():
                p.append("calculator.formula must be a non-empty string")
            else:
                allowed = set(names) | {"min", "max", "abs", "round", "floor", "ceil", "sqrt", "pow"}
                used = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", f))
                stray = sorted(used - allowed)
                if stray:
                    p.append(f"calculator.formula uses undeclared names: {', '.join(stray)}")
            out = c.get("output")
            if not isinstance(out, dict) or not out.get("label"):
                p.append("calculator.output needs a label")
            elif "decimals" in out and not (isinstance(out["decimals"], int) and 0 <= out["decimals"] <= 6):
                p.append("calculator.output.decimals must be 0-6")

    if "progress" in spec:
        pg = spec["progress"]
        if not isinstance(pg, dict):
            p.append("progress must be an object")
        else:
            types = {f["name"]: f["type"] for e in ents for f in (e.get("fields") or [])}
            fld = pg.get("field")
            if fld not in types:
                p.append(f"progress.field '{fld}' is not a field on any entity")
            elif types[fld] not in ("bool",):
                p.append(f"progress.field '{fld}' must be a bool field")
            if "label" in pg and not (isinstance(pg["label"], str) and 1 <= len(pg["label"]) <= 20):
                p.append("progress.label must be 1-20 characters")

    if "pattern" in spec and not re.fullmatch(r"[a-z][a-z0-9-]*", str(spec["pattern"])):
        p.append("pattern must be a slug, e.g. crud-list")
    if "currency" in spec and not (isinstance(spec["currency"], str) and 1 <= len(spec["currency"]) <= 3):
        p.append("currency must be a short symbol, e.g. \u20b9")
    if "accent" in spec and not re.fullmatch(r"#[0-9a-fA-F]{6}", str(spec["accent"])):
        p.append("accent must be #rrggbb")

    if not spec["not"]:
        p.append("'not' must list at least one thing the app refuses to do")

    p += lint_done_means(spec["done_means"], path)
    return p


def lint_done_means(entries, path="<spec>") -> list[str]:
    """The F-71 guard: a done-means that certifies nothing fails the build."""
    p = []
    if not entries:
        return ["done_means must have at least one entry"]
    for i, e in enumerate(entries):
        low = str(e).lower()
        if len(low) < 12:
            p.append(f"done_means[{i}] is too short to check")
            continue
        if not any(v in low for v in VERBS):
            p.append(f"done_means[{i}] names no observable outcome (needs one of: "
                     f"{', '.join(sorted(VERBS))})")
        for v in VAGUE:
            if v in low:
                p.append(f"done_means[{i}] uses a phrase that certifies nothing: '{v}'")
    return p


def lint_prose(text) -> list[str]:
    return [f"prose section missing: {h}" for h in PROSE_REQUIRED if h not in text]


def sections(text) -> dict:
    """Split the prose into {heading: body}."""
    out, cur, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur, buf = line[3:].strip(), []
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return out


def spec_paths(root=None) -> list[Path]:
    """Every spec in the repository, gallery included. One list, used everywhere."""
    from pathlib import Path as _P
    base = _P(root) if root else _P(__file__).resolve().parent.parent
    out = sorted(base.glob("specs/*.md")) + sorted(base.glob("specs/gallery/*.md"))
    return [f for f in out if f.name.lower() != "readme.md"]


def load_all(spec_dir, catalog=None) -> list[dict]:
    """Every spec in a directory. A broken spec is an error, not a skip."""
    specs, problems = [], []
    for f in sorted(Path(spec_dir).glob("*.md")):
        try:
            specs.append(load(f, catalog))
        except SpecError as e:
            problems += [f"{f.name}: {x}" for x in e.problems]
    if problems:
        raise SpecError(problems)
    return specs
