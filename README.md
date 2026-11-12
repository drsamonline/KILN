# KILN

> **Spec in. Finished app out. No model required. Nothing else installed.**

KILN is a deterministic app compiler for offline, single-file applications. It is one folder with no dependencies: Python 3.9+ and the standard library. No other repository, no submodule, no package, no key, no network.

Forge makes the shape. Kiln fires it into an app that runs.

---

## The three ways in

| Way | You have | You run | You get |
|---|---|---|---|
| Phrase | one sentence | `kiln new "a tea log with tags"` | a spec |
| Prompt | any chat model, or none | `kiln prompt` → paste → `kiln adopt reply.md` | a spec |
| Form | a phone or a browser | open `studio.html`, tap Build | an app, straight away |

All three end at the same place: a spec that compiles to a working app.

---

## Quick start

```bash
git clone <this repo> kiln && cd kiln

# one command, whole pipeline
python3 -m kiln pipeline "a reading log with tags and a rating" --zip

# or step by step
python3 -m kiln new "a notes app with tags, search and export"
python3 -m kiln build specs/app-notes.md -o out
python3 -m kiln verify out/app-notes
```

No `pip install`. No `npm install`. No `.env`. No API key. No network.

---

## The prompt bridge

`PROMPT.md` holds one prompt with five placeholders. Copy it, fill it, paste it into any chat window — a phone, a local model, a terminal. Paste the reply back:

```bash
python3 -m kiln prompt --idea "a tea log" --record "teas" --out my-prompt.txt
python3 -m kiln adopt reply.md --build
```

`kiln adopt` is the part that matters. It finds the spec object anywhere in the reply, repairs it, and refuses to write a spec that cannot build:

| The model does this | KILN does this |
|---|---|
| Adds chatter around the spec | finds the block, ignores the words, says so |
| Uses ```json or no fence at all | finds the object anyway |
| Writes `"type": "string"`, `"integer"`, `"textarea"`, `"datetime"` | maps to `text`, `number`, `longtext`, `date` |
| Invents a feature | drops it, names it, explains |
| Forgets `search` that `filters` needs | adds it |
| Writes `"works as expected"` as done-means | replaces it with a real assertion from the catalogue |
| Returns entities as an object, fields as an object | converts both to lists |
| Leaves out half the sections | generates them |
| Uses smart quotes, trailing commas, Python literals | repairs the JSON |
| Returns nothing usable | refuses, and says what to re-send |

A sloppy model cannot produce a broken app. Verified: `tests/fixtures/reply-sloppy.md` becomes a passing app in `tests/test_bridge.py`.

---

## Commands

| Command | What it does | Network |
|---|---|---|
| `kiln pipeline "<idea>" --zip` | idea → spec → app → verify → zip | no |
| `kiln new "<phrase>"` | phrase → spec file | no |
| `kiln prompt` | print the prompt for any model | no |
| `kiln adopt <file> [--build]` | model reply → spec → app | no |
| `kiln compose <spec>` | show the file plan, write nothing | no |
| `kiln build <spec> [-o dir]` | emit the app, then verify it | no |
| `kiln build --all` | every spec in `specs/` | no |
| `kiln verify <dir>` / `--all` | read the artifact, print evidence | no |
| `kiln studio` | rebuild `studio.html` | no |
| `kiln catalog` | features, kits, assertions | no |
| `kiln audit` | 43 guards over this repo | no |
| `kiln doctor` | what this machine can do | no |

---

## What a generated app contains

| Part | Detail |
|---|---|
| `index.html` | The whole app, ~21 KB. Embedded model, runtime, styles. No CDN, no fonts, no network |
| Storage | Namespaced `localStorage`, versioned, corrupt-state recovery, quota handling |
| CRUD | List, create, edit, delete, generated from the entity schema |
| Search | Field scan, `Ctrl-K` to focus |
| Export / import | JSON and CSV download, JSON restore |
| Theme | Dark and light, remembered |
| Failure path | Bad input, no network, storage full, corrupt state — handled and surfaced |
| `README.md`, `app.json`, `CHANGELOG.md`, `LICENSE` | The app documents itself |
| `.github/workflows/build-apps.yml` | Packaging, if you want it |
| `tests/smoke.py` | Behaviour assertions for this app |

---

## Self-contained, on purpose

| Dependency | Status |
|---|---|
| Other drsamonline repos | none. The five "kits" are regions of `templates/app/index.html`, in this repo |
| Python packages | none, stdlib only |
| Node | optional, only to syntax-check emitted JavaScript |
| Git | optional, only for `verify --at <sha>` and `preflight` |
| GitHub | optional: CI, releases, Pages |
| Internet | not needed, for any command except copying the prompt by hand |

Detail and the check: [`docs/SELF-CONTAINED.md`](docs/SELF-CONTAINED.md).

---

## Portability

| Where | How |
|---|---|
| Linux, macOS, Windows | `python3 -m kiln …` |
| Android, iOS, any phone | open `studio.html` in the browser, tap Build |
| Any browser, any OS | open a generated `index.html` |
| Windows EXE / Android APK | your `app-builder`, if you wire it |

Detail: [`docs/PORTABILITY.md`](docs/PORTABILITY.md).

---

## Feature catalog

`crud`, `search`, `export`, `import`, `theme`, `pwa`, `tags`, `filters`, `sort`, `stats`, `reminder`, `print`, `i18n`, `backup`.

Each declares emitters, required features, a kit, and an assertion. A feature not in `catalog/features.json` cannot appear in a spec. `catalog/` — [`catalog/features.json`](catalog/features.json).

---

## Repo map

| Path | Contents |
|---|---|
| `PROMPT.md` | The prompt bridge, with the catalogue in it |
| `studio.html` | The browser version, built from the same sources |
| `PLAN.md` | Phases and falsifiable acceptance criteria |
| `AUDIT-FORGE.md` | Every Forge defect, and the guard against it |
| `SPEC-SHAPE.md` | What a spec must say |
| `schema/spec.schema.json` | Machine schema for the spec block |
| `catalog/` | Features, kits, categories, licence |
| `kiln/` | The compiler: spec, catalog, intent, prompt, adopt, prose, compose, emit, verify, studio, guards, cli |
| `templates/app/` | The runtime and the files it emits |
| `templates/studio/` | The studio source |
| `specs/` | Specs, one file per app |
| `tests/` | 43 tests, including a deliberately sloppy model reply |
| `docs/` | Architecture, portability, workflow, self-containment |
| `INDEX.md` | Generated list of every spec |

---

## Licence

PolyForm Noncommercial 1.0.0 — matches the estate default. See `LICENSE`.
