"""Emit: file plan -> files on disk. Refuses to write an empty file."""
from __future__ import annotations

import re
from pathlib import Path

from .compose import TPL

VAR = re.compile(r"\{\{([A-Z_]+)\}\}")
ONLY = re.compile(
    r"(?:/\*|<!--)\s*@only ([a-z0-9_]+)\s*(?:\*/|-->).*?(?:/\*|<!--)\s*@end only\s*(?:\*/|-->)\n?",
    re.S)
MARKER = re.compile(r"(?:/\*|<!--)\s*@(?:only [a-z0-9_]+|end only)\s*(?:\*/|-->)\n?")


def strip_unused(text: str, features) -> tuple[str, list[str]]:
    """Remove the code blocks for capabilities this app does not have.

    A calculator should not carry the tracker's arithmetic. The markers are in
    the template, so the block and its removal live next to each other.
    """
    keep = set(features)
    dropped = []

    def sub(m):
        name = m.group(1)
        if name in keep:
            return MARKER.sub("", m.group(0))
        dropped.append(name)
        return ""
    return ONLY.sub(sub, text), dropped


class EmitError(Exception):
    pass


def render(template: str, ctx: dict) -> str:
    def sub(m):
        key = m.group(1)
        if key not in ctx:
            raise EmitError(f"template references unknown variable {{{{{key}}}}}")
        return str(ctx[key])
    out = VAR.sub(sub, template)
    left = VAR.search(out)
    if left:
        raise EmitError(f"unsubstituted variable {left.group(0)}")
    return out


def write(plan, outdir) -> list[tuple[str, int]]:
    outdir = Path(outdir)
    written = []
    for item in plan:
        dest = outdir / item["path"]
        if "inline" in item:
            text = item["inline"]
        else:
            src = TPL / item["template"]
            if not src.exists():
                raise EmitError(f"missing template: {src}")
            text = render(src.read_text(encoding="utf-8"), item["ctx"])
        if item.get("strip") is not None:
            text, dropped = strip_unused(text, item["strip"])
            item["dropped"] = dropped
        if not text.strip():
            raise EmitError(f"refusing to write an empty file: {item['path']}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        written.append((item["path"], len(text.encode("utf-8"))))
    return written
