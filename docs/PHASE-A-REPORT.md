# Phase A report

Master prompt v3, Phase A: A1 → A2 → A3. Stopped here, as §10 requires.

---

## (a) Files confirmed vs missing

| Named in the prompt | State |
|---|---|
| `README.md` | found |
| `USAGE.md` | found |
| `DEV_PLAN.md` | **missing** — no such file exists; `PLAN.md` plays that role |
| `CONTRIBUTING.md` | found |
| `LICENSE` | found |
| `kiln/*.py` | found — 18 modules (`adopt`, `catalog`, `cli`, `compose`, `demo`, `ed25519`, `emit`, `guards`, `intent`, `licence`, `prompt`, `prose`, `spec`, `studio`, `verify`, plus `__init__`, `__main__`) |
| `specs/` | found |
| `studio.html` | found |
| `demo.html` | found |
| `catalogue/` | **was `catalog/`** — renamed in this phase, and `features.json` became `capabilities.json` |
| `catalogue/features/` | **created** in A2 |
| `specs/gallery/` | **created** in A3 |
| `docs/gallery/` | **created** in A3 |
| `docs/PATTERNS.md` | **created** in A3 |
| `GUIDE-*.md` (8 files, §7) | **missing** — Phase B2/B3 |

`catalogue/features/` (a directory) and `catalogue/capabilities.json` (a file) are different
things: the first is the F1–F15 registry, the second is the fourteen app capabilities a spec
may name in `features`.

---

## (b) Features registered

| Family | Entries | Emitted | Planned |
|---|---|---|---|
| F1 entity | 12 | 3 — single, tags, timestamps | 9 |
| F2 field | 29 | 11 — text, textarea, int, decimal, currency_cents, date, boolean, select, radio, checkbox, tags | 18 |
| **Total** | **41** | **14** | **27** |

Every entry carries `id`, `family`, `name`, `spec_keys`, `emitter_hook`, `verify_check`,
`docs_anchor`, `status`. Guard `C14` fails if a runtime field type is unregistered, if an
emitted entry claims a type the runtime lacks, or if a shipped spec uses an unregistered type.

---

## (c) CRUD-list diff summary

| File | Change |
|---|---|
| `catalogue/patterns/crud-list.json` | new — descriptor, required capabilities and fields, spec defaults, verify checks, pros/cons |
| `specs/gallery/crud-list.md` | new — sample spec, a clinic stock list with a `currency_cents` field |
| `docs/gallery/crud-list.png` | new — rendered from the built sample, seeded with five rows |
| `docs/PATTERNS.md` | new — the template, the crud-list block, the seed table for 17 archetypes |
| `kiln/catalog.py` | `patterns()` loader |
| `kiln/spec.py` | optional `pattern` and `currency` keys; `spec_paths()` — one place that knows where specs live |
| `kiln/verify.py` | `check_pattern()` — conformance, sample and screenshot existence |
| `kiln/compose.py` | single-file default, `with_docs`, `currency` in the model |
| `kiln/cli.py` | `new --pattern`, `build --with-docs`, `verify --json`, `catalogue --registry` |
| `templates/app/index.html` | `currency_cents` input, storage and formatting; deterministic ids; no clock, no random |
| `tests/test_registry.py` | new — 16 tests over the registry, the pattern and money |

§1 changes made in the same phase, because A3 could not ship without them:

| § | Was | Now |
|---|---|---|
| §1.1 determinism | a build date in the header, `Date.now()` in `uid()`, `Math.random()` in the corrupt-key path | no date, ids derived from the data, a fixed `:corrupt` key. Three runs, one hash |
| §1.3 single file | seven files | one `index.html`; the rest behind `--with-docs` |
| §1.6 money | floats | `currency_cents`, integer cents, formatted at view time |
| §1.5 evidence | human output only | `verify --json` |

---

## (d) `kiln verify --json` output

```json
{ "app": "out/app-clinic-stock", "ok": true,
  "counts": { "checks": 44, "passed": 44, "failed": 0, "skipped": 0 } }
```

Full report: 44 checks, `ok: true`. Levels L2 (pattern), L3 (layout, wiring), L4 (JS parse),
L5 (provenance, failure paths, smoke), L6 (golden).

---

## (e) Determinism test result

| Run | sha256 of `index.html`, first 16 |
|---|---|
| 1 | `56361b0993f8f0dd` |
| 2 | `56361b0993f8f0dd` |
| 3 | `56361b0993f8f0dd` |

Enforced by `tests/test_kiln.py::TestDeterminism` — byte-identical rebuild, no `{{` left in
the output, no build date, no `Date.now(`, no `Math.random(`, no `crypto.randomUUID`, and a
stable fingerprint.

---

## (f) Proposed next archetype

**`tracker`** (archetype 5 — habit, weight, water, mood, sleep, BP, workouts).

| Why it is next | Detail |
|---|---|
| It is the first archetype that needs a **derived** view | a streak, a 7-day average, a goal percentage — that is family F5 + M5, not yet registered |
| It reuses everything crud-list proved | one entity, one list, the same form machinery |
| It forces the chart decision early | a sparkline is the smallest chart worth having, and it settles whether F7 belongs in the runtime |
| It is the archetype the estate already ships most of | habit and weight trackers are the common shape in `QUEUE/` |

Alternative if you would rather stay flat: `checklist` (archetype 19), which adds only a
boolean field and a progress count — cheaper, and proves less.

---

## What is still open

| Item | Why it is not done |
|---|---|
| `GUIDE-*.md` (8 files) | Phase B2/B3; two of them are generated from the schema, which does not exist yet |
| 29 remaining archetypes | one per pull request, §5 |
| `kiln migrate` | no schema change has shipped that needs it; the layout change is additive (`--with-docs`) |
| i18n dictionary, a11y pass | Phase B4 |
| Dataset-size and backup-reminder banners | Phase B5 |
