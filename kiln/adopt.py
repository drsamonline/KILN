"""Adopt: take a document a model wrote and make it a spec KILN can build.

The model is allowed to be sloppy. This is where sloppy becomes valid, and
where every change is reported rather than hidden.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import catalog as cat
from . import intent, prose, spec as specmod

TYPE_MAP = {
    "string": "text", "str": "text", "text": "text", "varchar": "text",
    "char": "text", "email": "text", "url": "text", "tel": "text",
    "textarea": "longtext", "text area": "longtext", "longtext": "longtext",
    "long text": "longtext", "paragraph": "longtext", "richtext": "longtext",
    "rich text": "longtext", "markdown": "longtext", "notes": "longtext",
    "int": "number", "integer": "number", "float": "number", "decimal": "number",
    "double": "number", "currency": "number", "money": "number", "number": "number",
    "date": "date", "datetime": "date", "timestamp": "date", "time": "date",
    "bool": "bool", "boolean": "bool", "checkbox": "bool", "toggle": "bool",
    "switch": "bool", "flag": "bool",
    "select": "select", "enum": "select", "dropdown": "select", "choice": "select",
    "radio": "select", "options": "select", "status": "select",
    "tags": "tags", "array": "tags", "list": "tags", "multi": "tags",
    "multiselect": "tags", "labels": "tags",
}
SELECT_DEFAULT = ["general", "work", "personal"]
FENCE = re.compile(r"```[ \t]*([a-zA-Z0-9]*)[ \t]*([a-zA-Z0-9]*)[ \t]*\n(.*?)\n```", re.S)


class AdoptError(Exception):
    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("\n".join(f"  - {p}" for p in self.problems))


# ------------------------------------------------------------------ extraction
def _fix_json(raw: str) -> tuple[str, list[str]]:
    fixes, out = [], raw
    for a, b in [("\u201c", '"'), ("\u201d", '"'), ("\u2018", "'"), ("\u2019", "'"),
                 ("\u00a0", " "), ("\ufeff", "")]:
        if a in out:
            out = out.replace(a, b)
            fixes.append("replaced a smart quote or stray character")
    stripped = re.sub(r"//[^\n]*", "", out)
    stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.S)
    if stripped != out:
        out = stripped
        fixes.append("removed JSON comments")
    if re.search(r"[:,]\s*[}\]]", out):
        out = re.sub(r",(\s*[}\]])", r"\1", out)
        fixes.append("removed trailing commas")
    if re.search(r"\b(True|False|None)\b", out):
        out = re.sub(r"\bTrue\b", "true", out)
        out = re.sub(r"\bFalse\b", "false", out)
        out = re.sub(r"\bNone\b", "null", out)
        fixes.append("converted Python literals to JSON")
    return out, fixes


def _balanced(text, start):
    depth, i, instr, esc = 0, start, False, False
    while i < len(text):
        c = text[i]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def extract(text) -> tuple[dict, tuple[int, int], list[str]]:
    """Find the spec object anywhere in the document. Returns (spec, span, repairs)."""
    repairs = []
    candidates = []
    for m in FENCE.finditer(text):
        tag = (m.group(1) or "").lower()
        tag2 = (m.group(2) or "").lower()
        candidates.append(("kiln" if tag == "kiln" or tag2 == "kiln" else tag, m))
    candidates.sort(key=lambda c: 0 if c[0] == "kiln" else (1 if c[0] == "json" else 2))

    for tag, m in candidates:
        raw, fixes = _fix_json(m.group(3))
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and ("features" in obj or "entities" in obj):
            if tag and tag != "kiln":
                repairs.append(f"read a plain `{tag}` block as the spec")
            elif not tag:
                repairs.append("read an untagged code block as the spec")
            repairs += fixes
            before = re.sub(r"^\s*#\s+.*$", "", text[:m.start()], count=1, flags=re.M).strip()
            if before:
                repairs.append(f"ignored {len(before.split())} words before the block")
            return obj, (m.start(), m.end()), repairs

    # no fence: scan for a balanced object that looks like a spec
    for m in re.finditer(r"\{", text):
        end = _balanced(text, m.start())
        if end < 0:
            continue
        raw, fixes = _fix_json(text[m.start():end])
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and ("features" in obj or "entities" in obj):
            repairs.append("found the spec with no code fence at all")
            repairs += fixes
            return obj, (m.start(), end), repairs

    raise AdoptError([
        "no spec object found. The document must contain a JSON object with "
        "'features' or 'entities' — fenced or not.",
        "re-run the prompt from PROMPT.md and paste the whole reply.",
    ])


# ----------------------------------------------------------------- normalising
def _slug(s, fallback="item"):
    s = re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")
    return s or fallback


def _ident(s, fallback="item"):
    s = re.sub(r"[^a-z0-9]+", "_", str(s or "").lower()).strip("_")
    if not s or s[0].isdigit():
        s = fallback + ("_" + s if s else "")
    return s


def _alias_index(catalog):
    idx = {}
    for fid, d in catalog["features"].items():
        for a in d["aliases"] + [fid, d["label"]]:
            idx[a.lower()] = fid
    return idx


def _match_feature(word, catalog, idx):
    w = str(word).lower().strip()
    if w in catalog["features"]:
        return w
    if w in idx:
        return idx[w]
    w2 = re.sub(r"[^a-z0-9 ]", " ", w)
    w2 = re.sub(r"\s+", " ", w2).strip()
    if w2 in idx:
        return idx[w2]
    best, score = None, 0
    for alias, fid in idx.items():
        if len(alias) < 3:
            continue
        if alias in w2 or w2 in alias:
            if len(alias) > score:
                best, score = fid, len(alias)
    if best:
        return best
    r = intent.parse(w2, catalog)
    if r["confidence"] >= 0.5 and len(r["features"]) == 1:
        return r["features"][0]
    return None


def normalise(spec, catalog, path="<adopted>") -> tuple[dict, list[str]]:
    rep = []
    s = dict(spec)

    name = str(s.get("name") or "").strip()
    raw_id = str(s.get("id") or "").strip()
    stem = Path(path).stem if path != "<adopted>" else ""
    if not raw_id:
        # the filename is usually "reply.md", so the app name wins over it
        if stem.startswith("app-"):
            raw_id = stem
        else:
            raw_id = "app-" + _slug(name or "untitled")
        rep.append(f"generated id '{raw_id}' from the app name")
    sid = _slug(raw_id)
    if not sid.startswith("app-"):
        sid = "app-" + sid
        rep.append(f"prefixed the id: '{sid}'")
    if sid != raw_id:
        rep.append(f"normalised the id to '{sid}'")
    s["id"] = sid

    if not name:
        name = sid.replace("app-", "").replace("-", " ").title()
        rep.append(f"generated name '{name}'")
    if len(name) > 40:
        name = name[:40].rstrip()
        rep.append("truncated the name to 40 characters")
    s["name"] = name

    tier = s.get("tier", 1)
    try:
        tier = int(tier)
    except (TypeError, ValueError):
        tier = 1
        rep.append("tier was not a number, set to 1")
    if tier not in (1, 2, 3):
        tier = 1
        rep.append("tier was outside 1-3, set to 1")
    s["tier"] = tier

    category = str(s.get("category") or "").lower().strip()
    cat_syn = {"food": "utility", "food & drink": "utility", "drink": "utility",
               "medical": "clinical", "clinic": "clinical", "healthcare": "clinical",
               "wellness": "health", "fitness": "health", "study": "education",
               "learning": "education", "money": "finance", "budget": "finance",
               "notes": "productivity", "tasks": "productivity", "todo": "productivity",
               "data": "utility", "tools": "utility", "social": "community",
               "book": "reference", "library": "reference", "art": "creative"}
    if category not in catalog["categories"] and category in cat_syn:
        rep.append(f"category '{category}' mapped to '{cat_syn[category]}'")
        category = cat_syn[category]
    if category not in catalog["categories"]:
        rep.append(f"category '{category or 'missing'}' is not in the catalogue, set to utility")
        category = "utility"
    s["category"] = category

    pitch = " ".join(str(s.get("pitch") or "").split())
    if len(pitch) < 10:
        pitch = f"{name} — an offline app that keeps its data on the device."
        rep.append("pitch was missing or too short, generated one")
    if len(pitch) > 140:
        pitch = pitch[:137].rstrip() + "..."
        rep.append("truncated the pitch to 140 characters")
    s["pitch"] = pitch

    # features
    raw_feats = s.get("features") or []
    if isinstance(raw_feats, str):
        raw_feats = [x for x in re.split(r"[,/]| and ", raw_feats) if x.strip()]
        rep.append("features was a string, split it into a list")
    idx = _alias_index(catalog)
    picked = []
    for f in raw_feats:
        hit = _match_feature(f, catalog, idx)
        if hit and hit not in picked:
            if hit != str(f).strip().lower():
                rep.append(f"feature '{f}' -> '{hit}'")
            picked.append(hit)
        elif not hit:
            rep.append(f"dropped feature '{f}': it does not exist in the catalogue")
    if not picked:
        picked = ["crud", "export", "theme"]
        rep.append("no usable features, defaulted to crud, export, theme")
    s["features"] = picked

    # entities
    ents = s.get("entities")
    if isinstance(ents, dict):
        ents = [ents]
        rep.append("entities was an object, wrapped it in a list")
    if not ents:
        ents = [{"name": _ident(name), "label": name, "fields": []}]
        rep.append("no entities, created one from the app name")
    fixed_ents = []
    for e in ents:
        if not isinstance(e, dict):
            continue
        ename = _ident(e.get("name") or e.get("label") or "item")
        elabel = str(e.get("label") or ename.replace("_", " ").title())[:40]
        fields = e.get("fields")
        if isinstance(fields, dict):
            merged = []
            for k, v in fields.items():
                if isinstance(v, dict):
                    merged.append(dict({"name": k}, **v))
                else:
                    merged.append({"name": k, "type": v})
            fields = merged
            rep.append(f"entity '{ename}' had fields as an object, converted to a list")
        fields = fields or []
        ffix = []
        for f in fields:
            if isinstance(f, str):
                f = {"name": f, "type": "text"}
                rep.append(f"field '{f['name']}' was a bare string, treated as text")
            if not isinstance(f, dict):
                continue
            fname = _ident(f.get("name") or f.get("label") or "field")
            flabel = str(f.get("label") or fname.replace("_", " ").title())[:40]
            ftype = str(f.get("type") or "text").lower().strip()
            if ftype not in specmod.FIELD_TYPES:
                mapped = TYPE_MAP.get(ftype)
                if mapped:
                    rep.append(f"field '{fname}' type '{ftype}' -> '{mapped}'")
                    ftype = mapped
                else:
                    rep.append(f"field '{fname}' had unknown type '{ftype}', set to text")
                    ftype = "text"
            out = {"name": fname, "label": flabel, "type": ftype}
            if f.get("required") is True:
                out["required"] = True
            if ftype == "select":
                opts = f.get("options") or f.get("choices") or f.get("values")
                if isinstance(opts, str):
                    opts = [o.strip() for o in opts.split(",") if o.strip()]
                if not isinstance(opts, list) or len(opts) < 2:
                    opts = SELECT_DEFAULT
                    rep.append(f"select field '{fname}' had no usable options, used defaults")
                out["options"] = [str(o) for o in opts]
            ffix.append(out)
        if not ffix:
            ffix = [{"name": "title", "label": "Title", "type": "text", "required": True}]
            rep.append(f"entity '{ename}' had no fields, added a title")
        elif ffix[0]["type"] in ("bool", "number", "date"):
            ffix.insert(0, {"name": "title", "label": "Title", "type": "text", "required": True})
            rep.append(f"entity '{ename}' started with a non-text field, added a title")
        req = [f for f in ffix if f.get("required")]
        if len(req) > 2:
            for f in req[2:]:
                f.pop("required", None)
            rep.append(f"entity '{ename}' had more than two required fields, kept two")
        fixed_ents.append({"name": ename, "label": elabel, "fields": ffix})
    s["entities"] = fixed_ents

    # storage
    st = s.get("storage")
    ns = _slug(sid.replace("app-", ""))
    if not isinstance(st, dict) or st.get("kind") != "localstorage" or not st.get("namespace"):
        rep.append(f"storage set to localstorage with namespace '{ns}'")
        st = {"kind": "localstorage", "namespace": ns}
    s["storage"] = {"kind": "localstorage", "namespace": _slug(st.get("namespace"))}

    accent = str(s.get("accent") or "").strip()
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
        accent = "#7c9cff"
        rep.append("accent was missing or not #rrggbb, set to #7c9cff")
    s["accent"] = accent.lower()

    # done_means: replace anything that certifies nothing with a real assertion
    dm = s.get("done_means") or s.get("doneMeans") or []
    if isinstance(dm, str):
        dm = [dm]
        rep.append("done_means was a string, wrapped it in a list")
    pool = [catalog["features"][f]["assertion"] for f in picked
            if f in catalog["features"]] or ["the app opens and shows its empty state"]
    good = []
    for d in dm:
        if specmod.lint_done_means([d]) == []:
            good.append(str(d))
        else:
            rep.append(f"replaced an unverifiable done-means: '{str(d)[:48]}'")
    i = 0
    while len(good) < 2 and i < len(pool):
        if pool[i] not in good:
            good.append(pool[i])
            rep.append("added a done-means from the feature catalogue")
        i += 1
    s["done_means"] = good[:6]

    nots = s.get("not") or s.get("mustNot") or []
    if isinstance(nots, str):
        nots = [nots]
    nots = [str(x) for x in nots if str(x).strip()]
    if not nots:
        nots = ["network calls", "accounts", "sync"]
        rep.append("'not' was empty, defaulted to no network, no accounts, no sync")
    s["not"] = nots

    # the requires-closure must hold before we write anything
    try:
        s["features"] = cat.expand(s["features"], catalog)
    except cat.CatalogError as e:
        raise AdoptError(e.problems)
    return s, rep


# ----------------------------------------------------------------------- adopt
def adopt(path, catalog, outdir=None, write=True) -> tuple[dict, list[str], Path]:
    src = Path(path)
    text = src.read_text(encoding="utf-8")
    obj, (a, b), rep = extract(text)
    s, rep2 = normalise(obj, catalog, str(src))
    rep += rep2

    rest = (text[:a] + "\n" + text[b:]).strip()
    rest = re.sub(r"^#\s+.*$", "", rest, count=1, flags=re.M).strip()
    body = prose.render(s, catalog)
    if rest:
        body, added = prose.fill("# x\n\n" + rest, s, catalog)
        body = re.sub(r"^# x\n\n", "", body)
        if added:
            rep.append("added missing sections: " + ", ".join(added))
    header = f"# {s['name']}\n\n```json kiln\n{json.dumps(s, indent=2)}\n```\n\n"
    document = header + body.strip() + "\n"

    problems = specmod.validate(s, catalog, f"{s['id']}.md") + specmod.lint_prose(document)
    if problems:
        raise AdoptError(problems)

    dest = Path(outdir or src.parent) / f"{s['id']}.md"
    if write:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(document, encoding="utf-8")
    return s, rep, dest
