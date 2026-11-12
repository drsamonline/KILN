# KILN

> **Spec in. Finished app out. No model required.**

KILN is a deterministic app compiler for offline, single-file applications. You write a spec, KILN emits a complete working app: CRUD, storage, search, export, import, theme, docs, CI. No skeleton to finish by hand, no LLM in the loop.

Forge makes the shape. Kiln fires it into an app that runs.

---

## Why this exists

| Forge today | KILN |
|---|---|
| Emits a shell; real coding still needs an LLM | Emits a working app; the runtime does the work once, for every app |
| 153 apps, 7 buildable | Every generated app is built and smoke-tested before the spec counts as done |
| Spec is prose, checked by hand | Spec is a JSON block in Markdown, checked by schema in CI |
| Template = one app shape | Catalog of 14 features, each with a real emitter and a test |
| "Done" is a sentence | "Done" must be a falsifiable assertion, or the build fails |
| Agent writes code, agent reports success | `kiln verify` reads the artifact and prints evidence |

Full defect list and the guard against each: [`AUDIT-FORGE.md`](AUDIT-FORGE.md).

---

## Quick start

```bash
# 1. describe the app in plain words (no model, no network)
python3 -m kiln intake "a notes app with tags, search and export"

# 2. compile it
python3 -m kiln build specs/app-notes.md -o out/

# 3. prove it works
python3 -m kiln verify out/app-notes
```

Result: one `index.html` that runs offline, on any browser, on any OS, from a USB stick.

---

## Commands

| Command | What it does | Needs network |
|---|---|---|
| `kiln intake "<phrase>"` | Deterministic phrase → spec patch (alias match + tf-idf + slot fill) | no |
| `kiln new <id> "<phrase>"` | intake + write a spec file | no |
| `kiln compose <spec>` | Print the file plan (no writes) | no |
| `kiln build <spec> -o <dir>` | Emit the app | no |
| `kiln verify <dir>` | Schema, wiring, JS parse, smoke assertions | no |
| `kiln verify --all` | Every spec in `specs/` | no |
| `kiln catalog` | Feature catalog and kit map | no |
| `kiln audit` | Run the Forge-mistake guards over this repo | no |
| `kiln llm on` | Optional: enable BYOK drafting of specs only | yes |

---

## What a generated app contains

| Part | Detail |
|---|---|
| `index.html` | The whole app. Embedded model, runtime, styles. No CDN, no fonts, no network. |
| Storage | Namespaced `localStorage`, versioned, with corrupt-state recovery and quota handling |
| CRUD | List, create, edit, delete, generated from the entity schema |
| Search | Token index over declared fields, `Ctrl-K` to focus |
| Export / import | JSON and CSV download, JSON restore |
| Theme | Dark and light, remembered |
| Failure path | Bad input, no network, storage full, corrupt state — all four handled and surfaced |
| `README.md` | What the app does, how to run it, what it stores |
| `kiln.spec.md` | The spec it was built from |
| `.github/workflows/build-apps.yml` | Build to EXE + APK via `app-builder` |
| `tests/smoke.py` | Behaviour assertions for this specific app |

---

## Feature catalog

`crud`, `search`, `export`, `import`, `theme`, `pwa`, `tags`, `filters`, `sort`, `stats`, `reminder`, `print`, `i18n`, `backup`.

Each feature declares: emitters, required features, conflicts, and a smoke assertion. See `catalog/features.json`.

---

## Portability

| Thing | Runs on |
|---|---|
| KILN itself | Windows, macOS, Linux — Python 3.9+ stdlib only |
| Generated app | Any browser, any OS, offline, no install |
| GitHub | Optional: CI, releases, Pages |
| EXE / APK | Via `app-builder` (Windows, Android) |

Detail: [`docs/PORTABILITY.md`](docs/PORTABILITY.md).

---

## Repo map

| Path | Contents |
|---|---|
| `PLAN.md` | The plan, phases, and acceptance criteria |
| `AUDIT-FORGE.md` | Every Forge defect found, and the guard |
| `SPEC-SHAPE.md` | What a spec must say |
| `schema/spec.schema.json` | Machine schema for the spec block |
| `catalog/` | Feature and kit catalog |
| `kiln/` | The compiler |
| `templates/` | Emitters |
| `specs/` | Specs, one file per app |
| `tests/` | Tests for the compiler |
| `docs/` | Architecture, portability, workflow |
| `INDEX.md` | Generated list of every spec |

---

## Licence

PolyForm Noncommercial 1.0.0 — matches the estate default. See `LICENSE`.
