# PLAN — from skeleton generator to app compiler

Status date: 2026-11-13. Owner: Dr Sohil Momin. Builder: Kiln build session.

---

## The one-line goal

> A spec plus a command produces an app that runs, with no model in the loop, verified by evidence rather than assertion.

---

## Non-goals

| Not doing | Why |
|---|---|
| Replacing Forge's portfolio management | Forge's dashboard, audit and registry are estate-level; KILN is a compiler |
| Generating arbitrary applications | The catalog is bounded on purpose. Bounded means testable |
| A chat interface | A chat box is a worse form. Intent parsing is a command line and a palette |
| Cloud sync, accounts, servers | The output must run from a USB stick |
| Model-dependent output | A generated app must be identical with or without an API key |

---

## Phases

| Phase | Deliverable | Acceptance (falsifiable) |
|---|---|---|
| P0 | Repo, spec schema, catalog, audit | `python3 -m kiln audit` exits 0; `tests/` green |
| P1 | Deterministic runtime template | A generated app opens offline, saves a row, reloads it, exports it |
| P2 | Compiler: parse → compose → emit | `kiln build specs/app-notes.md` writes 9 files, none empty |
| P3 | Verifier | `kiln verify out/app-notes` exits 0; tampering with the output makes it exit 1 |
| P4 | Intent parser | `kiln intake "a notes app with tags and search"` returns `features=[crud,search,tags,export]`, confidence ≥ 0.6 |
| P5 | Three real specs from the estate | All three build and verify in CI |
| P6 | Packaging hand-off | `build-apps.yml` calls `app-builder`; artifact produced on a tag |
| P7 | Prompt bridge | `kiln prompt` prints a filled prompt; `kiln adopt` turns a sloppy reply into a spec that builds |
| P8 | Repair engine | A reply with chatter, smart quotes, wrong types, an invented feature and a vague done-means still builds — asserted in `tests/fixtures/reply-sloppy.md` |
| P9 | Zero-dependency package | No kit points at another repo; `kiln doctor` shows nothing to install |
| P10 | Any device | `studio.html` builds an app in a phone browser, offline, byte-identical to `kiln studio` |

---

## Verification ladder

| Level | Check | Fails the build |
|---|---|---|
| L1 | Spec parses, schema-valid, done-means falsifiable | yes |
| L2 | Every declared feature has an emitter | yes |
| L3 | Plan has no empty file, no unreferenced file | yes |
| L4 | Emitted JS parses (`node --check`) | yes |
| L5 | Smoke assertions: create, persist, reload, search, export | yes |
| L6 | Golden diff against the last emitted output | warning on change, `--strict` fails |
| L7 | Read at commit sha, not working tree | yes |

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Catalog grows past what emitters cover | Medium | A feature without an emitter is a validation error, not a TODO |
| Generated apps all look identical | High | Theme tokens and per-app accent from the spec; layout variants per feature set |
| Specs stay prose-only and drift | Medium | JSON block is required; CI rejects a spec without one |
| Someone edits generated code and loses it | Medium | One-shot model: emitted code is disposable, spec is the source. Stated in every generated README |
| Reintroducing agent-in-the-loop by habit | High | The LLM path can only touch `specs/`, never `out/` |

---

## Definition of done for this repo

| Criterion | Evidence |
|---|---|
| Compiles an app from a spec | `kiln build` output tree in CI artifact |
| App works offline | No `http://`, `https://`, `cdn` or `fetch(` in emitted `index.html` — asserted by `verify` |
| No model needed | every command except copying the prompt by hand runs with no key and no network |
| Nothing else installed | `kiln doctor` lists no required package; `catalog/kits.json` names no repository |
| Works on a phone | `studio.html` opens from local storage and downloads a working app |
| Every Forge defect has a guard | `AUDIT-FORGE.md` row ↔ code symbol, checked by `kiln audit` |
| Tests exist and pass | `tests/` green on 3.9–3.12 |
| A human can use it in five minutes | README quick start, copy-pasteable |
