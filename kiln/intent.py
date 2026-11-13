"""Deterministic intent parsing. No model, no network, no key.

Three signals, combined and reported separately so a wrong guess is debuggable:
  1. alias match   - an exact phrase from catalogue/capabilities.json appears in the text
  2. tf-idf cosine - token overlap against the feature's own description
  3. slot fill     - nouns and adjectives that become entities and fields
"""
from __future__ import annotations

import math
import re

STOP = {"a", "an", "the", "app", "that", "with", "and", "for", "of", "to", "my",
        "it", "is", "in", "on", "me", "i", "want", "need", "make", "build",
        "should", "can", "keep", "simple", "small", "little", "some"}

# words that are never an entity
NOT_ENTITY = {"app", "tool", "thing", "it", "one", "way", "list", "data"}

FIELD_CUES = [
    (("due date", "deadline", "due"), "date", "due", "Due date"),
    (("tag", "tags", "label", "labels"), "tags", "tags", "Tags"),
    (("note", "notes", "body", "description", "detail", "details"), "longtext", "body", "Body"),
    (("rating", "score", "amount", "price", "quantity", "count", "weight"), "number", "amount", "Amount"),
    (("status",), "select", "status", "Status"),
    (("category", "categories", "type"), "select", "category", "Category"),
    (("priority",), "select", "priority", "Priority"),
    (("done", "completed", "complete"), "bool", "done", "Done"),
    (("date",), "date", "date", "Date"),
]

SELECT_DEFAULTS = {
    "status": ["open", "in progress", "done"],
    "category": ["general", "work", "personal"],
    "priority": ["low", "medium", "high"],
}

DEFAULTS = ["crud", "export", "theme"]


def _tokens(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP]


def _singular(word):
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith(("sses", "shes", "ches", "xes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def _tfidf(query_tokens, docs):
    """Plain tf-idf cosine. Deterministic; ties broken by feature id."""
    df = {}
    for toks in docs.values():
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    n = len(docs) or 1
    idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
    q = {}
    for t in query_tokens:
        q[t] = q.get(t, 0) + 1
    qn = math.sqrt(sum((c * idf.get(t, 1.0)) ** 2 for t, c in q.items())) or 1.0
    out = {}
    for fid, toks in docs.items():
        dv = {}
        for t in toks:
            dv[t] = dv.get(t, 0) + 1
        dn = math.sqrt(sum((c * idf.get(t, 1.0)) ** 2 for t, c in dv.items())) or 1.0
        dot = sum(q.get(t, 0) * c * idf.get(t, 1.0) ** 2 for t, c in dv.items())
        out[fid] = dot / (qn * dn)
    return out


def parse(text, catalog) -> dict:
    """Return a spec patch plus the reasoning behind it."""
    feats = catalog["features"]
    low = " " + re.sub(r"[^a-z0-9\s-]", " ", text.lower()) + " "
    low = re.sub(r"\s+", " ", low)

    reasons, scores = [], {}
    for fid, d in feats.items():
        hit = None
        for alias in d["aliases"]:
            if f" {alias} " in low or f" {alias}s " in low:
                if hit is None or len(alias) > len(hit):
                    hit = alias
        if hit:
            scores[fid] = 2.0 + 0.4 * len(hit.split())
            reasons.append(f"{fid}: alias '{hit}'")
        else:
            scores[fid] = 0.0

    docs = {fid: _tokens(d["label"] + " " + " ".join(d["aliases"]) + " " + d["assertion"])
            for fid, d in feats.items()}
    cos = _tfidf(_tokens(text), docs)
    for fid, c in cos.items():
        if scores[fid] == 0.0 and c >= 0.18:
            scores[fid] = 1.2 * c
            reasons.append(f"{fid}: tf-idf {c:.2f}")

    picked = [f for f in feats if scores[f] >= 0.30]
    for f in DEFAULTS:
        if f not in picked and f in feats:
            picked.append(f)
            reasons.append(f"{f}: default")

    entity = _entity(low, text)
    fields, freasons = _fields(low)
    reasons += freasons

    total = sum(scores.values()) or 1.0
    confidence = round(min(1.0, sum(scores[f] for f in picked) / total), 2)

    return {
        "features": picked,
        "entity": entity,
        "fields": fields,
        "confidence": confidence,
        "reasons": reasons,
        "unmatched": [t for t in _tokens(text)
                      if not any(t in d["aliases"] or t in d["label"].lower()
                                 for d in feats.values())],
    }


def _entity(low, text):
    m = re.search(r"\b(?:a|an|my|the)\s+([a-z]{3,20})\s+(?:app|tool|tracker|log|list)\b", low)
    if not m:
        m = re.search(r"\b(?:track|tracking|log|logging|manage|managing|record|recording|"
                      r"keep track of|list of)\s+(?:my\s+)?([a-z]{3,20})\b", low)
    if not m:
        m = re.search(r"\b([a-z]{3,20})\s+(?:app|tracker)\b", low)
    word = _singular(m.group(1)) if m else "item"
    if word in NOT_ENTITY:
        word = "item"
    return {"name": word, "label": word.capitalize()}


def _fields(low):
    out, reasons = [], []
    seen = set()
    for cues, ftype, name, label in FIELD_CUES:
        if any(c in low for c in cues) and name not in seen:
            seen.add(name)
            f = {"name": name, "label": label, "type": ftype}
            if ftype == "select":
                f["options"] = SELECT_DEFAULTS.get(name, ["one", "two"])
            if ftype == "tags":
                f["options"] = []
                f.pop("options")
            out.append(f)
            reasons.append(f"field {name}: cue '{next(c for c in cues if c in low)}'")
    names = {f["name"] for f in out}
    if "title" not in names:
        out.insert(0, {"name": "title", "label": "Title", "type": "text", "required": True})
        reasons.append("field title: default")
    if not any(f["type"] == "date" for f in out):
        out.append({"name": "created", "label": "Created", "type": "date"})
        reasons.append("field created: default")
    return out, reasons


def to_spec(text, catalog, spec_id=None) -> dict:
    """A complete, validatable spec from one sentence."""
    r = parse(text, catalog)
    ent = r["entity"]
    slug = spec_id or ("app-" + re.sub(r"[^a-z0-9]+", "-", ent["name"]).strip("-"))
    name = ent["label"] + "s"
    return {
        "id": slug,
        "name": name[:40],
        "tier": 1,
        "category": "productivity",
        "pitch": text.strip().rstrip(".")[:140],
        "features": r["features"],
        "entities": [{"name": ent["name"], "label": ent["label"], "fields": r["fields"]}],
        "storage": {"kind": "localstorage", "namespace": slug.replace("app-", "")},
        "accent": "#7c9cff",
        "done_means": [
            f"creating a {ent['name']} and reloading the page shows it in the list",
            f"typing a query that no {ent['name']} contains hides every row",
        ],
        "not": ["network calls", "accounts", "sync"],
        "_intent": {"confidence": r["confidence"], "reasons": r["reasons"]},
    }
