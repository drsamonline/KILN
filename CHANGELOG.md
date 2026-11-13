# Changelog

Every entry is a change a user can see. Dates are ISO. Versions are `MAJOR.MINOR`.

---

## v0.13 — 2026-11-13

Phase B4 and B5 in one batch: a real i18n dictionary, an accessibility pass, and the two banners.

| Area | Change |
|---|---|
| B4 i18n | the `i18n` capability now has actual dictionaries for **en, hi and gu**, a spec key `i18n.languages`, a toggle that cycles the declared languages, and `lang` set on `<html>`. Before this, the catalogue claimed a dictionary that did not exist |
| B4 a11y | skip link first in the body, a visible `:focus-visible` ring, `aria-live` on the banner region, `prefers-reduced-motion` respected, `aria-label` on every control that has no text |
| B5 feedback | a size warning past 2000 rows, and a backup reminder after 7 days without an export; exporting records the day |
| Registry | `a11y-skip-link` and `i18n-dictionary` (F14), `feedback-banner` (F12) — 52 entries |
| Emit | the strip markers now accept **digits** in a capability id (`i18n`, `a11y`), and both comment styles; three blocks had been leaking into every build |
| Counts | 188 tests, 180 guards |

## v0.12 — 2026-11-13

Phase B2 and B3: the guides. Two of the six are generated, so they cannot drift.

| Area | Change |
|---|---|
| B2 | `GUIDE-SPEC-REF.md` and `GUIDE-FEATURES.md` are written from `catalogue/` and `kiln/spec.py` by `kiln guide`. Every capability, field type, archetype and registry family appears because it exists, not because someone remembered |
| B3 | `GUIDE-QUICKSTART.md`, `GUIDE-COOKBOOK.md`, `GUIDE-PATTERNS.md`, `GUIDE-CONTRIBUTE.md` |
| Command | `kiln guide` regenerates, `kiln guide --check` fails on a stale file |
| Guard | `C17`: six guides exist, both generated ones match their sources, each opens with a TL;DR and ends with links |
| Cookbook | four buildable recipes, twenty-six named and marked as not written — the same honesty the registry applies to features |
| Counts | 173 tests, 178 guards |

## v0.11 — 2026-11-13

Phase B, third archetype: `calculator`. The first app with no entity.

| Area | Change |
|---|---|
| Archetype | `calculator` — inputs, a formula, one answer. No list, no storage, nothing to lose |
| Parser | a recursive-descent evaluator in the page: `+ - * / % ^`, parentheses, unary minus, `min max abs round floor ceil sqrt pow`. No `eval`, no `Function`, no library |
| Capabilities | `formula` — 19 in total |
| Entities | a spec may have none, but only if its pattern declares `requires_entities: false` |
| Emit | **unused capability code is stripped**: a notes app no longer carries the calculator, the tracker or the progress bar. Marked `@only <capability>` in the template |
| Size | every spec now builds under the 40 KB ceiling; notes fell from 40.1 KB to 33.4 KB, the calculator is 38.2 KB |
| Registry | `form-calculator` (F6) and `metric-result` (F7) — 49 entries |
| Tests | 14 parser cases under node, plus a size-budget test that builds every spec |
| Counts | 163 tests, 157 guards |

## v0.10 — 2026-11-13

Phase B, second archetype: `checklist`.

| Area | Change |
|---|---|
| Archetype | `checklist` — a list of things that get done, with a progress bar: done, left, percent |
| Capabilities | `progress` (a count and a percentage from one bool) and `toggle` (a row checkbox that saves without the form) |
| Registry | `metric-progress` (F7) and `table-toggle` (F5) — 47 entries |
| Spec key | `progress: {field, label}`, validated: the field must exist and be a bool |
| Sample | Clinic Opening — seven tasks, three done, 36 KB |
| Tests | 8 progress cases run under node; the bar's ARIA attributes are checked in the emitted HTML |
| Guards | `B6` caught `PROMPT.md` again (twice now — the guard is doing its job), `C16` caught the test count |
| Counts | 141 tests, 147 guards |

## v0.9 — 2026-11-13

Phase B, first archetype: `tracker`.

| Area | Change |
|---|---|
| Archetype | `tracker` — one number a day, against a goal: streak, days logged, average, goal percent, a week of bars |
| Capabilities | `derived` (metrics computed at view time) and `chart` (inline SVG sparkline, no library) |
| Registry | F7 family opens: `metric-streak`, `metric-average`, `metric-goal`, `metric-sparkline` — 45 entries in total |
| Spec key | `tracker: {field, goal, window, unit}`, validated: the field must exist and be numeric, the goal positive, the window 1–90 |
| Determinism | the derivation takes the date as an argument, so it can be run on its own — and is, under node, in `tests/test_tracker.py` |
| Guards | `B6` caught `PROMPT.md` missing the two new capabilities; the prompt now lists them, and explains `tracker` |
| Size | the tracker sample builds to 33 KB, inside the 40 KB ceiling |
| Counts | 127 tests, 134 guards |

## v0.8 — 2026-11-13

Phase A of the master prompt: determinism, one file, integer money, and the first archetype.

| Area | Change |
|---|---|
| §1.1 determinism | no build date, no `Date.now`, no `Math.random`, no uuid in emitted code; ids come from the data. Two builds are byte-identical, and a test says so |
| §1.3 single file | `kiln build` emits **one** `index.html`; the docs and smoke test move behind `--with-docs` |
| §1.6 money | new field type `currency_cents`: stored as integer cents, formatted only at view time |
| §1.5 evidence | `kiln verify --json` prints a machine-readable report |
| A2 registry | `catalogue/features/` — 41 entries across F1 (entity) and F2 (field), each with spec keys, emitter hook, verify check, docs anchor and status |
| A3 archetype | `crud-list`: descriptor, sample spec, screenshot, verify conformance, pros/cons block |
| Layout | `catalog/` renamed `catalogue/`; `features.json` renamed `capabilities.json` |
| Guards | `C14` registry, `C15` pattern integrity |
| Counts | 112 tests, 123 guards |

## v0.7 — 2026-11-13

Golden builds, a key ledger, and a studio that can open a spec.

| Area | Change |
|---|---|
| Golden | `verify --golden` compares a build with the one you last accepted; `--update-golden` accepts |
| Ledger | `kiln licence list` — every key issued from this machine, with expiry, from `~/.kiln/issued.jsonl` |
| Studio | "Open a spec file" reads a `.md` from `specs/` or a saved reply straight into the form |
| Studio | says which edition it builds: Personal, with the author block |
| Licensing | prices are on request, with the factors that set them, and what money never changes |
| Counts | 90 tests, 106 guards |

## v0.6 — 2026-11-13

Two editions, and no releases.

| Area | Change |
|---|---|
| Editions | `personal` (free, PolyForm, sponsor and author block in the app) and `commercial` (paid, full features, no sponsor block) |
| Removed | the corporate edition, and the free/demo naming that went with it |
| Demo | still the Personal edition, capped and without export — labelled as a demo, not an edition |
| Command | `kiln licence tiers` prints two editions and one demo row; `kiln licence` says "edition" |
| Releases | none published until the owner says so — [`RELEASE.md`](RELEASE.md) |
| Guard | `C12` fails if a third edition reappears anywhere in the repository |
| Counts | 80 tests, 106 guards |

## v0.5 — 2026-11-13

Tiers, watermark, and a gallery that shows every spec while running only some of them.

| Area | Change |
|---|---|
| Tiers | `free`, `commercial`, `corporate`, and a capped `demo` — [`LICENSING.md`](LICENSING.md) |
| Free builds | licence line, "Built with KILN", the sponsor block, in an About panel |
| Commercial builds | sponsor block gone; one line in About: "Built with KILN", hyperlinked |
| Corporate builds | no About button at all; the build comment stays in the file |
| Keys | Ed25519, verified offline, no packages; pinned public key; expiry enforced at build |
| Watermark | build record, fingerprint in the head, and an integrity check the app runs on boot |
| Commands | `kiln licence status\|tiers\|keygen\|issue\|verify\|activate`, `build --tier` |
| Demo | `demo.html` is a gallery of every spec; clinical and health specs are refused, with the reason |
| Demo builds | capped to crud, search, sort, theme, with a banner that says so |
| Guards | `C12` licensing and watermark, `C13` the gallery covers every spec and refuses some |
| Counts | 81 tests, 107 guards |

### One rule narrowed

The verifier used to reject any `http://` or `https://` in an app. Attribution needs links, so
the rule now rejects **loaded** resources — `src=`, `@import`, `fetch(`, `<script src` — and
allows an anchor in About. The app still loads nothing.

## v0.4 — 2026-11-13

The support block, and the last of the repository furniture.

| Area | Change |
|---|---|
| Support | UPI, GitHub Sponsors, Ko-fi, PayPal, books and email, in the README and on the landing page |
| QR | `docs/assets/upi-qr.svg`, the estate's UPI QR |
| Funding | `.github/FUNDING.yml` — the estate standard |
| Pages | `.nojekyll`, so the tree is served verbatim |
| Citation | `CITATION.cff` |
| Docs | `docs/README.md`, an index with a reading order |
| Guards | `C11` the support block is present in three places and the copies agree |
| Counts | 85 guards |

## v0.3 — 2026-11-13

The house is finished: a landing page, a live demo, real screenshots, the legal set,
the user guides, and the repository furniture the rest of the estate has.

| Area | Change |
|---|---|
| Landing | `index.html` — hero, badges, screenshots, pipeline, quick start, support block |
| Demo | `demo.html`, generated by `kiln demo`: a real app inlined in the page, not a mock |
| Screenshots | `assets/screenshot-app.png`, `assets/screenshot-studio.png`, rendered from this repository's own files |
| README | rebuilt: badges, screenshot, three ways in, prompt-bridge table, support, legal footer |
| Legal | `PRIVACY.md`, `TERMS.md`, `DISCLAIMER.md`, `COMMERCIAL.md`, `SECURITY.md`, `NOTICE` |
| Guides | `USAGE.md`, `INSTALL.md`, `docs/SPEC-REFERENCE.md`, `docs/FAQ.md`, `SUPPORT.md` |
| Community | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue forms, pull request template |
| Metadata | `MANIFEST.json`, `PAGES.json`, `icon.svg`, `manifest.webmanifest`, repository topics |
| Guards | `C8` landing and demo drift, `C9` the legal set, `C10` every relative link resolves |
| Counts | 55 tests, 76 guards |

## v0.2 — 2026-11-13

Self-contained, and the prompt bridge.

| Area | Change |
|---|---|
| Self-contained | `catalog/kits.json` names no repository; kits are regions of the template |
| Prompt | `PROMPT.md` — one copy-paste prompt with the catalogue inside it |
| Adopt | `kiln adopt` repairs a model's reply until it builds: types, features, done-means, sections, JSON |
| Studio | `studio.html` — the compiler in a browser, for a phone, offline, 50 KB |
| Pipeline | `kiln pipeline "<idea>" --zip` — spec, app, verify, package in one command |
| Commands | `kiln doctor`, `kiln build --all`, `--quiet` |
| Guards | `B6` prompt drift, `C7` studio drift |
| Self-audit | `AUDIT-FORGE.md` section G: six defects in KILN v0.1, closed |

## v0.1 — 2026-11-12

First working compiler.

| Area | Change |
|---|---|
| Spec | one shape: a `json kiln` block plus a prose contract, with a falsifiability lint |
| Catalogue | 14 features, 5 kits, requires-closure, conflict detection |
| Compiler | `intake` → `spec` → `compose` → `emit` → `verify` |
| Runtime | CRUD, storage, search, export, import, theme, all four failure paths |
| Verifier | wiring, external references, stub markers, JS parse, behaviour assertions |
| Guards | 37 guards, one per Forge defect |
| Specs | three real apps: notes, clinic log, field survey |
| CI | tests on 3.9–3.13, verify-all, audit, lint |
