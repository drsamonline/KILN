"""Pull a top-level function out of the runtime template, for the node tests.

Deliberately not marker-based: the template's strip markers move when a block is
reordered, and a test that depends on them breaks for the wrong reason. A
top-level function ends at the first `}` in column zero.
"""
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "app" / "index.html"


def source(name: str) -> str:
    tpl = TEMPLATE.read_text(encoding="utf-8")
    start = tpl.index("function " + name + "(")
    end = tpl.index("\n}\n", start) + 3
    return tpl[start:end]
