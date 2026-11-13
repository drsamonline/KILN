"""Emit: file plan -> files on disk. Refuses to write an empty file."""
from __future__ import annotations

import re
from pathlib import Path

from .compose import TPL

VAR = re.compile(r"\{\{([A-Z_]+)\}\}")
ONLY_LINE = re.compile(r"^(?:/\*|<!--)\s*@only ([a-z0-9_]+)\s*(?:\*/|-->)$")
END_LINE = re.compile(r"^(?:/\*|<!--)\s*@end only\s*(?:\*/|-->)$")


class EmitError(Exception):
    pass


def strip_unused(text: str, features) -> tuple[str, list[str]]:
    """Remove the blocks for capabilities this app does not have.

    Not a size diet: a calculator should not carry a month grid it cannot show. The
    100 KB ceiling is a backstop; this keeps the output honest about what it is.

    A line scanner, not a regex over the whole file: a regular expression cannot
    pair markers reliably when one block follows another, and a mis-paired block
    silently deletes the wrong code. The stack makes nesting impossible to get
    wrong, and no marker can survive into the output.
    """
    keep = set(features)
    out, stack, dropped = [], [], []
    for line in text.splitlines(keepends=True):
        probe = line.strip()
        m = ONLY_LINE.match(probe)
        if m:
            name = m.group(1)
            stack.append((name, name in keep))
            if name not in keep:
                dropped.append(name)
            continue
        if END_LINE.match(probe):
            if stack:
                stack.pop()
            continue
        if all(flag for _, flag in stack):
            out.append(line)
    return "".join(out), dropped


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
