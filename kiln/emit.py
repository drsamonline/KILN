"""Emit: file plan -> files on disk. Refuses to write an empty file."""
from __future__ import annotations

import re
from pathlib import Path

from .compose import TPL

VAR = re.compile(r"\{\{([A-Z_]+)\}\}")


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
        if not text.strip():
            raise EmitError(f"refusing to write an empty file: {item['path']}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        written.append((item["path"], len(text.encode("utf-8"))))
    return written
