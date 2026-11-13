# Contributing

Thank you for looking. KILN is small on purpose, and contributions that keep it small are
the most welcome ones.

---

## The four-step rule

Every change must pass these before it is merged:

| Step | Command | Must be |
|---|---|---|
| 1 | `python3 -m unittest discover -s tests` | all green |
| 2 | `python3 -m kiln verify --all` | 0 failing |
| 3 | `python3 -m kiln audit` | 0 failed |
| 4 | `python3 -m kiln studio && python3 -m kiln demo` | no diff, or the diff is intended |

CI runs all four. A pull request that skips one will fail, and that is the point.

---

## Adding a feature

The catalogue is the design space. Adding to it means touching five places, in this order:

| # | File | Change |
|---|---|---|
| 1 | `catalogue/capabilities.json` | the entry: id, label, aliases, requires, kit, assertion |
| 2 | `PROMPT.md` | the row in the catalogue table — a guard fails without it |
| 3 | `templates/app/index.html` | gate the behaviour on `F.has("<id>")` |
| 4 | `templates/app/smoke.py` | the assertion, if it is new behaviour |
| 5 | `tests/` | a test that a spec using the feature builds and verifies |
| 6 | — | `python3 -m kiln studio && python3 -m kiln demo && python3 -m kiln audit --write` |

A feature with no assertion is rejected by `catalog.load()`. A feature with no emitter is
rejected by `verify`.

## Adding a field type

`FIELD_TYPES` in `kiln/spec.py`, `fieldInput` and `readForm` in the runtime template, and a
test. Nothing else.

## Fixing a bug

Include the failing case as a test first. If the bug was in a guard that let something
through, add the guard's counter-example to `tests/`.

## Style

| Area | Rule |
|---|---|
| Python | standard library only; no new dependency will be merged |
| Comments | explain why, not what; no comment that repeats the line |
| Prose | plain English, short sentences, no marketing voice |
| Commit messages | what changed and why, in one line, then detail if needed |
| File size | a generated app stays under 60 KB; the studio under 80 KB |

## Inbound licence

By opening a pull request you agree that:

1. you wrote the contribution, or you have the right to submit it;
2. you licence it to this project under the same terms as the project
   (PolyForm Noncommercial 1.0.0), plus a perpetual, worldwide, royalty-free right for the
   maintainer to relicense it, including for commercial licensing;
3. you are not expecting payment, equity or attribution beyond the commit record.

No CLA form to sign. This paragraph is the grant.

## What will be declined

| Proposal | Why |
|---|---|
| Adding a dependency | the whole value is zero dependencies |
| A React/Vue/Tailwind rewrite | 21 KB beats 200 KB on a USB stick |
| A server component | the output must run offline |
| An LLM API call in the compiler | the prompt bridge exists so that this is never needed |
| A feature that only one app would use | put it in your fork |
| Telemetry, analytics, "anonymous usage stats" | no |

## Reporting a security issue

Not here. See [`SECURITY.md`](SECURITY.md).
