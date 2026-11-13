# Changelog

Every entry is a change a user can see. Dates are ISO. Versions are `MAJOR.MINOR`.

---

## v0.23 — 2026-11-13

Two archetypes, two field types, and the guard that stops a bug class.

| Area | Change |
|---|---|
| Field type | `image` — a url string (`https://` or `data:`); nothing uploaded, nothing fetched at build time |
| Archetype | `quiz` — one question at a time, options as buttons, the score derived from the picks |
| Archetype | `gallery` — a responsive grid, lazy images, a placeholder where a picture is missing |
| Capabilities | `quiz` and `gallery` — 38 in total |
| Registry | `view-quiz` (F4) and `field-image` (F2) — 72 entries |
| **Guard C18** | **a name declared inside an `@only` block must not be used by a capability that does not require it.** This is the bug that broke the runtime four times in this project; it is now checked on every audit, with `typeof`, property access and `F.has(owner)` treated as the safe probes they are |
| Fixed by C18 | three real escapes: the lookup option builder (relation), the wizard handover inside `openEditor` (steps), and the children list inside `openDetail` (relation) |
| Counts | 358 tests, 330 guards, 21 specs verifying |

## v0.22 — 2026-11-13

Two archetypes in one batch: `inventory` and `timeline`.

| Area | Change |
|---|---|
| Archetype | `inventory` — items and signed movements, a **derived** balance per item, and a reorder count in the strip |
| Archetype | `timeline` — the same list grouped by month, newest first, undated records kept in their own group |
| Capabilities | `balance` and `timeline` — 36 in total |
| Registry | `metric-balance` (F7) and `view-timeline` (F4) — 69 entries |
| Correctness | the balance is never stored: it is the signed sum of the children, so it cannot disagree with the history |
| Correctness | an undated record is shown under "Undated", not dropped |
| Counts | 341 tests, 309 guards, 19 specs verifying |

## v0.21 — 2026-11-13

The first relation, and the `master-detail` archetype.

| Area | Change |
|---|---|
| Field type | `lookup` — a select of another entity's rows; the **id** is stored, the **title** is shown |
| Archetype | `master-detail` — a parent's read view lists its children, and only its children |
| Capability | `relation` — 34 in total |
| Registry | `field-lookup` (F2) and `view-children` (F4) — 66 entries |
| Validation | a lookup must point at a declared entity that is not itself; `master_detail.field` must be that lookup, pointing at the master |
| Honesty | an orphan child is shown as an orphan, not hidden; deleting a parent leaves its children pointing at nothing, and the pattern's cons say so |
| Counts | 322 tests, 289 guards, 17 specs verifying |

## v0.20 — 2026-11-13

Multi-entity, and the `dashboard` archetype that needed it.

| Area | Change |
|---|---|
| Multi-entity | a spec may declare two or more entities; a switcher changes which list is being edited, and storage becomes `{v, data: {entity: rows}}` |
| Backwards | a single-entity app keeps the older `{v, rows}` shape, so every existing spec builds as before |
| Archetype | `dashboard` — a strip of metric cards over one or more entities, above the list |
| Metric | `count`, `sum`, `avg`, `max`, `min`, `latest`, computed over the whole list on every render |
| Capabilities | `multi` and `dashboard` — 33 in total |
| Registry | `view-multi` (F1) and `metric-card` (F7) — 63 entries |
| CSS | the metric strip moved out of the `derived` block into the base stylesheet: it is shared by two capabilities, so it is not optional |
| Guard | `C16` caught the counts, again |
| Counts | 308 tests, 279 guards, 16 specs verifying |

## v0.19 — 2026-11-13

Two archetypes in one batch: `search-directory` and `comparison`.

| Area | Change |
|---|---|
| Archetype | `search-directory` — the box takes focus, sort and filter are hidden, matches are highlighted, and a long list shows a count instead of the rows until you type |
| Archetype | `comparison` — one row per record, the columns named in the spec, and the best value in each numeric column marked (`max` or `min`) |
| Capabilities | `directory` and `comparison` — 31 in total |
| Registry | `view-directory` and `view-comparison` (F4) — 61 entries |
| Correctness | the comparison assertion no longer claims exclusivity: a tie marks both rows, which is what "cheapest" means |
| Counts | 291 tests, 268 guards, 14 specs verifying |

## v0.18 — 2026-11-13

The studio catches up with the compiler.

| Area | Change |
|---|---|
| Pattern picker | choose one of the ten archetypes; it brings its capabilities, adds the field type it needs, and fills its spec key (`tracker`, `progress`, `board`, `calendar`, `detail`, `totals`, `calculator`, `converter`, `wizard`, `journal`, `log`) |
| Gallery | the ten sample specs are embedded, so the browser can load one without a filesystem |
| Explain panel | live: pattern, capability count, entity and field count, **the real rendered size**, and what is left out |
| Parity | the studio now runs the same line-scanner strip as the CLI, so a browser build no longer ships `@only` markers or capabilities the spec cannot use |
| Parity test | the JS strip and the Python strip are compared on the same input — same text, same dropped list |
| Model | every optional key (`pattern`, `tracker`, `progress`, `board`, `calendar`, `i18n` …) reaches the model, the same as the CLI |
| Edition | the studio builds the Personal edition and now says so in the build record |
| Size | studio.html 118 KB, carrying 10 gallery specs and 10 archetypes |
| Counts | 274 tests, 248 guards |

## v0.17 — 2026-11-13

The size policy relaxed, and the Phase C tooling.

| Area | Change |
|---|---|
| Size | **one lenient ceiling: 100 KB.** The 40/44 KB rule is gone. Typical builds are 38–43 KB, and the ceiling is a backstop rather than a target. Per-capability stripping stays, because a calculator still should not carry a month grid |
| Command | `kiln explain <spec>` — pattern, capabilities, fields, real measured size, checks. `--json` for machines. Never raises on a bad spec; it explains the failure |
| Command | `kiln completions bash\|zsh\|fish` — generated from the argument parser that just ran, so it cannot describe a stale CLI |
| Guides | `GUIDE-LIMITS.md` and `GUIDE-LICENSING.md` — §7's eight guides are now all present |
| Guard | `C17` covers all eight |
| Counts | 265 tests, 248 guards |

## v0.16 — 2026-11-13

Two archetypes in one batch: `kanban` and `calendar`. The first alternative views.

| Area | Change |
|---|---|
| Archetype | `kanban` — a board of columns from one select field, a card per record, two move buttons |
| Archetype | `calendar` — a six by seven month grid, Monday first, computed in UTC, a cell per day |
| Capabilities | `board` and `calendar` — 29 in total |
| Registry | `view-board` and `view-calendar` (F4) — 59 entries |
| Render | the board and the calendar replace the list; both read the same filtered rows, so search still works |
| Refactor | the strip is now `renderStrip()`, so three views share one summary |
| Emit | `groupBy`, the month maths and `openEditorFor` are gated to their capability; the view CSS is gated too |
| Size | kanban 41.8 KB and calendar 42.1 KB, both above the 40 KB target and under the 44 KB ceiling — a board of five columns and a 42-cell grid are the most markup any archetype emits |
| Counts | 252 tests, 240 guards |

## v0.15 — 2026-11-13

Two archetypes in one batch: `journal` and `log`.

| Area | Change |
|---|---|
| Archetype | `journal` — a dated entry you read: a read-only dialog with the long text as paragraphs |
| Archetype | `log` — a dated entry with a `duration`, and a running total in the strip |
| Field type | `duration` — whole minutes in, `1h 30m` out, exported as minutes |
| Capabilities | `detail` and `totals` — 27 in total |
| Registry | `view-detail` (F4), `field-duration` (F2), `metric-total` (F7) — 57 entries |
| Strip | one place builds it now, so a total and a count cannot overwrite each other |
| Correctness | a null value is skipped by the total, not counted as zero |
| Size ceiling | **40 KB target, 44 KB enforced ceiling.** The tracker archetype needs `derived` + `chart` + `stats` + `search` + `sort` + `theme`, which cannot fit in 40 KB without dropping a capability it declares. That is the written justification §5 asks for; everything else builds under 40 KB |
| Counts | 231 tests, 220 guards |

## v0.14 — 2026-11-13

Two archetypes in one batch: `converter` and `wizard`.

| Area | Change |
|---|---|
| Archetype | `converter` — one amount, two unit selects, a factor table. `amount × factor_from ÷ factor_to` |
| Archetype | `wizard` — the editor split into steps, each validated before it advances, with Back/Next/Save and a draft |
| Capabilities | `convert` and `steps` — 25 in total |
| Registry | `form-convert` and `form-steps` (F6) — 54 entries |
| Emit | the strip is now a **line scanner with a stack**, not a regular expression. Two markers had been mis-pairing and silently deleting the wrong block; nesting can no longer go wrong, and no marker can ship |
| Emit | CSS is gated per capability too, and the form machinery is gated behind `crud` — a calculator no longer carries the editor |
| Dedupe | one field reader, shared by the plain form and by a step |
| Tests | the node tests extract a function by its boundary instead of by a strip marker, so reordering a block no longer breaks them |
| Size | every spec builds under 40 KB: converter 34.9 KB, wizard 38.4 KB |
| Counts | 211 tests, 200 guards |

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
