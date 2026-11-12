# AUDIT — every defect found in Forge, and the guard in KILN

Audit date: 2026-11-13. Method: read `forge` at HEAD (`README.md`, `SPEC-SHAPE.md`, `LESSONS.md`, `LEARNINGS.md`, `DIAGNOSE.md`, `BACKLOG.md`, `ROADMAP.md`, `PROMPTS/*`, `templates/*`, `scripts/*`, `.github/workflows/*`), plus `app-builder`, `registry`, `ml-kit`, `search-kit`, `skills`, `NEO`, and a sample of `QUEUE/app-*.md`.

Every row below is a defect with a named source. Every guard is code in this repo, not advice.

---

## A. Defects that produce bad apps

| # | Defect | Evidence | Root cause | Guard in KILN | Enforced by |
|---|---|---|---|---|---|
| A1 | Apps are skeletal; real coding is deferred to an LLM | `templates/app/index.html` is one thin shell; every app spec needs a build agent to be useful | Template emits a container, not behaviour | Generic runtime shipped in the template: CRUD, storage, search, export, import, theme, failure path. Spec selects features; nobody writes the app by hand | `tests/test_kiln.py::test_generated_app_is_complete` |
| A2 | 153 apps, 7 buildable | `LESSONS.md` | Generation never gated on a build | `kiln build` emits, `kiln verify` builds and asserts before a spec can be marked done | `kiln.yml` job `verify-all` |
| A3 | A thing that is not wired looks wired (10 recorded) | `LEARNINGS.md` lesson 1 | No reference check between declared and used | `verify` fails on: declared feature with no emitter, emitted file not referenced, unused storage key, form field with no column | `kiln/verify.py::check_wiring` |
| A4 | Read-back lies (7 recorded) | `LEARNINGS.md` lesson 2 | Verifying `main` after writing elsewhere | `verify --at <sha>` reads the artifact at the commit, not the working tree; prints the sha it read | `kiln/verify.py::read_at` |
| A5 | Measuring the wrong thing (9 recorded) | `LEARNINGS.md` lesson 3 | Counting bytes instead of behaviour | Smoke assertions test outcomes (row saved, row found, export parses), never size | `tests/smoke.py` in every emitted app |
| A6 | Duplicate kit copies across repos | `BACKLOG.md` F-100 | Kits vendored by copy, not referenced | Kit references resolve through `catalog/kits.json`; an unknown kit is a hard error | `kiln/catalog.py::resolve_kits` |
| A7 | Hand-rolled reimplementation of kit capability | `LESSONS.md` harvest queue — `web-kit` hand-rolled in 38 repos | No capability lookup before coding | Every feature maps to exactly one kit in `catalog/features.json`; `kiln catalog --feature <id>` is the lookup | `kiln/guards.py::check_kit_coverage` |

---

## B. Defects in the spec corpus

| # | Defect | Evidence | Root cause | Guard in KILN | Enforced by |
|---|---|---|---|---|---|
| B1 | 18 specs whose done-means certifies nothing | `SPEC-SHAPE.md`, `spec-mismatch.json` | Prose accepted without a check | `done_means` entries must contain an assertion verb and must not match the vague-phrase list | `kiln/spec.py::lint_done_means` |
| B2 | 37 specs on an older merged shape, 1 malformed | `SPEC-SHAPE.md` (`app-poets-studio.md`) | Two shapes allowed at once | One shape. Schema-validated. A second shape is a validation error | `schema/spec.schema.json` |
| B3 | No spec states the failure path | `SPEC-SHAPE.md` F-71 | Section optional in practice | `failure` object with four required keys: `bad_input`, `no_network`, `storage_full`, `corrupt_state` | `kiln/spec.py::validate` |
| B4 | Master list and `QUEUE/` drift apart | `BACKLOG.md` reconciliation task | Two hand-maintained sources of truth | `specs/` is the only source; `INDEX.md` is generated and diffed in CI | `kiln/guards.py::check_index` |
| B5 | Spec front-matter is prose, so nothing can consume it | `SPEC-SHAPE.md` header list | Written for humans only | Machine block: one fenced `json kiln` object per spec, plus the human prose below it | `kiln/spec.py::load` |

---

## C. Defects in the machine around the apps

| # | Defect | Evidence | Root cause | Guard in KILN | Enforced by |
|---|---|---|---|---|---|
| C1 | 65 workflow errors, 63 failing workflows | `DIAGNOSE.md` | Workflows written and pushed without a local run | Every workflow is linted for structure and dry-run locally before push; CI runs its own linter | `kiln/guards.py::check_workflows` |
| C2 | Three cycles reported the system blocked on a 404 that was a credential | `forge/README.md` | 404 not distinguished from permission denial | `kiln preflight` probes with an explicit authenticated call and reports which of the two it is | `kiln/guards.py::preflight` |
| C3 | 10 false completions recorded | `LESSONS.md` | "Done" claimed without a command and its output | A completion is a recorded command plus its output in `RUNS.jsonl`; nothing else counts | `kiln/verify.py::record` |
| C4 | All schedules stopped, nothing observed itself | `LESSONS.md` | Silence read as health | Heartbeat writes a dated row; a missing row is reported as `STALE`, never as OK | `kiln/guards.py::heartbeat` |
| C5 | Licence claims diverge from licence files | `DIAGNOSE.md` — 14 policies, 4 MIT | Badges and docs written by hand | One `catalog/licence.json`; README badge and LICENSE generated from it | `kiln/guards.py::check_licence` |
| C6 | Shell bugs from unquoted variables and wrong-file picks | `PROMPTS/shellcheck.md` exists but is a prompt, not a gate | Lint treated as guidance | `shellcheck` runs as a CI gate on every script in this repo | `kiln.yml` job `lint` |

---

## D. What Forge gets right and KILN keeps

| Practice | Source | Why it survives |
|---|---|---|
| Kits are one-way: an app consumes a kit, a kit never gets retrofitted into an app | `LESSONS.md` | Keeps the standard library honest and the apps disposable |
| The negative contract (`## What it must NOT do`) | `SPEC-SHAPE.md` | The strongest habit in the estate; stops scope drift at the spec |
| Failure path as a required section | `SPEC-SHAPE.md` | Most apps in the wild die here; Forge names it, KILN enforces it |
| One licence policy for the estate | `OPEN-SOURCE-POLICY.md` | Predictable for consumers |
| Spec per app, one file | `QUEUE/` | Cheap to review, cheap to diff |
| Reusable workflow over copy-paste | `app-builder` | One fix reaches every app |

---

## E. Deliberate divergences

| Decision | Forge | KILN | Reason |
|---|---|---|---|
| Scope | Whole estate: 154 apps, dashboard, audit, registry | One thing: spec → app | A compiler that also manages a portfolio does neither well |
| Agent role | Builder agent writes each app | Agent optional, used only to draft a spec | Removes the failure class in A1–A5 entirely |
| Output | Repo per app | One file per app, repo optional | Offline-first is the estate's thesis; a file is the smallest offline unit |
| State | Many JSON ledgers at root | One `STATE.json`, generated | Less to drift |

---

## F. Open questions for the owner

| # | Question | Default taken |
|---|---|---|
| F1 | Public or private repo? | Public — reusable workflows must be reachable from public app repos |
| F2 | Licence: PolyForm Noncommercial or MIT? | PolyForm, matching the estate default |
| F3 | Does KILN replace `new-app.py` or feed it? | Feeds it: KILN emits, `app-builder` packages |
| F4 | Keep `NEO`/NOVA as an output target? | Not now. TypeScript/HTML is the boring correct substrate |

---

## G. Defects in KILN v0.1, found and fixed in v0.2

The first version of this repo repeated two of the mistakes it criticises. Both are now closed.

| # | Defect in v0.1 | Why it was wrong | Fix in v0.2 | Enforced by |
|---|---|---|---|---|
| G1 | `catalog/kits.json` named five other repositories | A "self-contained" compiler that needs five clones is not self-contained. It also reintroduced A6 (duplicate copies) and A7 (kits drifting) | Kits are regions of `templates/app/index.html`, declared `"bundled": true`, with no repo field | `catalog.load()` requires the kit to exist; `docs/SELF-CONTAINED.md` |
| G2 | The prompt existed only as prose in a doc | Nothing checked that it offered features the compiler has, so a model could be asked for something that cannot build | `PROMPT.md` carries the catalogue table, and a guard compares it to `catalog/features.json` row by row | `guards.check_prompt_catalog` |
| G3 | A model's reply had to be hand-massaged into a spec | The whole point of a bridge is that the other side can be sloppy | `kiln adopt` extracts, repairs and refuses; 24 repairs on the fixture, 0 on its own output | `tests/test_bridge.py` |
| G4 | No way to build without Python | "Any OS" was true; "any device" was not | `studio.html`, generated from the same template and catalogue, runs in a phone browser | `guards.check_studio`, `tests/test_bridge.py` |
| G5 | The studio could silently drift from the CLI | Two copies of one truth is the F-100 pattern again | The studio is generated and byte-compared in `kiln audit` and in CI | `guards.check_studio` |
| G6 | `PROMPT.md` claimed five placeholders but the CLI filled none | A documented interface that does not work | `kiln prompt --idea …` fills them; `unfilled()` reports what is left | `tests/test_bridge.py::test_fill_substitutes_named_placeholders` |

### The rule this section establishes

A tool that audits other systems has to audit itself first, and the self-audit has to be in the same table as the rest.

---

## H. Repository furniture, and what protects it

Forge's repos carry a fixed set of files — landing page, changelog, contributing, privacy,
security, notice, manifest. KILN now carries the same set, and unlike a checklist, each one
is checked.

| File | Purpose | Guard |
|---|---|---|
| `index.html` | landing page, self-contained, no remote asset | `C8` |
| `demo.html` | a real generated app, inlined, not a mock | `C8` (byte-compared to `kiln demo`) |
| `studio.html` | the browser compiler | `C7` (byte-compared to `kiln studio`) |
| `assets/*.png` | screenshots rendered from this repository | `C8` (present and non-trivial) |
| `LICENSE`, `NOTICE` | licence and third-party position | `C5`, `C9` |
| `PRIVACY.md`, `TERMS.md`, `DISCLAIMER.md` | what the software does with data, and what it does not promise | `C9` |
| `SECURITY.md`, `SUPPORT.md`, `COMMERCIAL.md` | how to report, how to get help, how to buy | `C9` |
| `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` | the inbound licence grant and the behaviour rules | `C9` |
| `USAGE.md`, `INSTALL.md`, `docs/SPEC-REFERENCE.md`, `docs/FAQ.md` | the guides a person actually reads | `C9` |
| `MANIFEST.json`, `PAGES.json`, `manifest.webmanifest`, `icon.svg` | machine-readable project facts | `tests/test_site.py` |
| every relative link in README and the landing page | — | `C10` (resolves or fails the build) |

The point of the last row: a documentation set that rots into 404s is worse than no
documentation, because it wastes the reader's time twice.
