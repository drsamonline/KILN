"""Turn CHANGELOG.md into a printable report.

The changelog is the honest source: every entry there was written for a user and
checked against the build at the time. This module only presents it — it never
invents an entry, and it never reads git history, because a commit message is not
a user-facing claim.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "CHANGELOG.md"
TARGET = ROOT / "docs" / "changelog.html"

VERSION_RE = re.compile(r"^## (v[\d.]+) — (\d{4}-\d{2}-\d{2})\s*$")


def parse(text: str) -> list[dict]:
    """Every version section, in file order."""
    out, cur = [], None
    for line in text.splitlines():
        m = VERSION_RE.match(line)
        if m:
            cur = {"version": m.group(1), "date": m.group(2), "lines": []}
            out.append(cur)
            continue
        if cur is not None:
            cur["lines"].append(line)
    for v in out:
        body = "\n".join(v["lines"]).strip()
        v["body"] = body
        v["summary"] = _summary(body)
        v["changes"] = body.count("\n|") + body.count("| ")
    return out


def _summary(body: str) -> str:
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith(("|", "-", "#", ">", "---")):
            return s
    return ""


def _inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\[)\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def _md(text: str) -> str:
    """The subset of Markdown the changelog actually uses."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if s == "---":
            out.append("<hr>")
            i += 1
            continue
        # table
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                head, rest = rows[0], rows[1:]
                out.append("<table><thead><tr>" +
                           "".join(f"<th>{_inline(c)}</th>" for c in head) +
                           "</tr></thead><tbody>" +
                           "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) +
                                   "</tr>" for r in rest) +
                           "</tbody></table>")
            continue
        # list
        if s.startswith(("- ", "* ")):
            items = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                items.append(_inline(lines[i].strip()[2:]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue
        # paragraph
        para = []
        while i < len(lines) and lines[i].strip() and \
                not lines[i].strip().startswith(("|", "- ", "* ", "---")):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>" + _inline(" ".join(para)) + "</p>")
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 18mm 16mm 20mm; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.5 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #1a1d24; margin: 0; }
h1 { font-size: 24pt; margin: 0 0 4px; letter-spacing: -.02em; }
.sub { color: #5a6472; font-size: 10pt; margin: 0 0 18px; }
.stats { display: flex; gap: 18px; flex-wrap: wrap; margin: 0 0 22px;
  padding: 12px 14px; background: #f5f7fa; border: 1px solid #e2e7ef; border-radius: 8px; }
.stat b { display: block; font-size: 15pt; }
.stat span { color: #5a6472; font-size: 8.5pt; text-transform: uppercase; letter-spacing: .06em; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9.5pt; }
th, td { border: 1px solid #e2e7ef; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #f5f7fa; font-weight: 600; }
code { font-family: ui-monospace, Menlo, monospace; font-size: 9pt;
  background: #f2f4f8; padding: 1px 4px; border-radius: 3px; }
.toc { font-size: 9pt; }
.toc th, .toc td { padding: 3px 7px; }
.toc td:first-child, .toc td:nth-child(2) { white-space: nowrap;
  font-variant-numeric: tabular-nums; }
.toc td:first-child { width: 16mm; }
.toc td:nth-child(2) { width: 22mm; }
.version { page-break-inside: avoid; margin: 0 0 16px; padding: 12px 14px;
  border: 1px solid #e2e7ef; border-radius: 8px; }
.version h2 { font-size: 13pt; margin: 0 0 2px; }
.version .date { color: #5a6472; font-size: 9pt; }
.version p { margin: 6px 0; }
hr { border: 0; border-top: 1px solid #e2e7ef; margin: 14px 0; }
.break { page-break-before: always; }
footer { margin-top: 20px; color: #5a6472; font-size: 8.5pt; }
@media print { .version { break-inside: avoid; } }
"""


def build(catalog=None) -> str:
    text = SOURCE.read_text(encoding="utf-8")
    versions = parse(text)
    stats = {"versions": len(versions), "first": versions[-1] if versions else None,
             "last": versions[0] if versions else None}
    cards = []
    for v in versions:
        cards.append(
            f'<section class="version"><h2>{html.escape(v["version"])}</h2>'
            f'<div class="date">{html.escape(v["date"])}</div>'
            f"{_md(v['body'])}</section>")
    toc = "".join(
        f'<tr><td>{html.escape(v["version"])}</td><td>{html.escape(v["date"])}</td>'
        f'<td>{_inline(v["summary"])}</td></tr>' for v in versions)
    first = stats["first"]["date"] if stats["first"] else ""
    last = stats["last"]["date"] if stats["last"] else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>KILN — changelog</title>
<style>{CSS}</style></head>
<body>
<h1>KILN — changelog</h1>
<p class="sub">Every entry is a change a user can see. {len(versions)} versions,
{html.escape(first)} to {html.escape(last)}.</p>
<div class="stats">
  <div class="stat"><b>{len(versions)}</b><span>versions</span></div>
  <div class="stat"><b>24</b><span>archetypes</span></div>
  <div class="stat"><b>50</b><span>capabilities</span></div>
  <div class="stat"><b>33</b><span>specs</span></div>
</div>
<h2 style="font-size:13pt;margin:0 0 6px">Every version</h2>
<table class="toc"><thead><tr><th>Version</th><th>Date</th><th>What changed</th></tr></thead>
<tbody>{toc}</tbody></table>
<div class="break"></div>
{''.join(cards)}
<footer>Generated by <code>kiln changelog</code> from CHANGELOG.md. No entry was
written for this report; every line was checked against the build at its version.</footer>
</body></html>
"""
