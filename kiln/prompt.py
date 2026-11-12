"""The prompt bridge: one document you can paste into any model, any window.

KILN never calls a model. It hands you the prompt and takes the reply.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "PROMPT.md"

PLACEHOLDERS = ["APP_IDEA", "WHO_USES_IT", "WHAT_THEY_RECORD", "PLATFORM", "MUST_NOT"]
BLOCK = re.compile(r"```text\n(.*?)\n```", re.S)


def body(doc_path=None) -> str:
    """The prompt itself, lifted out of PROMPT.md so there is one copy."""
    p = Path(doc_path or DOC)
    text = p.read_text(encoding="utf-8")
    m = BLOCK.search(text)
    if not m:
        raise ValueError(f"{p} has no ```text block")
    return m.group(1)


def fill(doc_path=None, **values) -> str:
    out = body(doc_path)
    for key in PLACEHOLDERS:
        if key in values and values[key]:
            out = out.replace(f"[[{key}]]", str(values[key]).strip())
    return out


def unfilled(text) -> list[str]:
    return sorted(set(re.findall(r"\[\[([A-Z_]+)\]\]", text)))


def catalogue_table(catalog) -> str:
    rows = ["| id | what it does | needs |", "|---|---|---|"]
    for fid, d in catalog["features"].items():
        needs = ", ".join(d.get("requires") or []) or "-"
        rows.append(f"| {fid} | {d['label'].lower()} | {needs} |")
    return "\n".join(rows)
