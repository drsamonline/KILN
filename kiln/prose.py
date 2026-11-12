"""Prose generation, shared by `new` and `adopt`.

One generator, so a hand-written spec and a machine-repaired spec read the same.
"""
from __future__ import annotations

FAILURE = {
    "bad input": "the form refuses to save and names the field that is wrong",
    "no network": "everything keeps working; a note says the network is not needed",
    "storage full": "the change stays in memory, a banner says it will not survive a reload, export is offered",
    "corrupt state": "the bad state is copied aside under a :corrupt: key, the app resets, and a banner says where it went",
}


def sections(spec, catalog, reasons=None) -> dict:
    """{heading without '## ': body}. Deterministic."""
    ent = spec["entities"][0]
    job = [f"- record a {ent['name']}", f"- find it again"]
    for f in spec["features"]:
        if f in ("crud",):
            continue
        job.append(f"- {catalog['features'][f]['label'].lower()}")
    out = {
        "Pitch": spec["pitch"],
        "The job": "\n".join(job),
        "The mechanic": (
            f"One {ent['name']}, one list, one file. The entity is declared once and the "
            "list, the form, the search and the export all read that declaration, so "
            "nothing can drift out of agreement."),
        "What it must NOT do": "\n".join(f"- {n}" for n in spec["not"]),
        "What it does when things go wrong":
            "\n".join(f"- **{k}** — {v}" for k, v in FAILURE.items()),
        "Done means": "\n".join(f"- {d}" for d in spec["done_means"]),
        "The data": (
            f"Stored in `localStorage` under `kiln:{spec['storage']['namespace']}`. "
            "Nothing leaves the device unless the user exports it."),
    }
    if reasons:
        out["How this spec was derived"] = "\n".join(f"- {r}" for r in reasons)
    return out


def render(spec, catalog, reasons=None) -> str:
    return "\n\n".join(f"## {h}\n\n{b}" for h, b in sections(spec, catalog, reasons).items())


def fill(text, spec, catalog, reasons=None) -> tuple[str, list[str]]:
    """Add only the sections that are missing. Never overwrites what is there."""
    from . import spec as specmod
    have = specmod.sections(text)
    want = sections(spec, catalog, reasons)
    added = []
    for heading, body in want.items():
        if heading in have and have[heading].strip():
            continue
        added.append(heading)
        text = text.rstrip() + f"\n\n## {heading}\n\n{body}\n"
    return text, added
