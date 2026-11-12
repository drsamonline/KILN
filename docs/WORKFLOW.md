# WORKFLOW

## Day to day

| Step | Command | What it proves |
|---|---|---|
| 1. Describe | `python3 -m kiln intake "a clinic log with search and print"` | the phrase maps to catalog features, and you can see why |
| 2. Write the spec | `python3 -m kiln new "..." --out specs/` | a spec exists that passes the schema |
| 3. Edit the prose | open `specs/app-x.md` | the human contract says what the machine block cannot |
| 4. Compose | `python3 -m kiln compose specs/app-x.md` | the file plan, before anything is written |
| 5. Build | `python3 -m kiln build specs/app-x.md -o out/` | the app, plus a verify pass |
| 6. Verify | `python3 -m kiln verify out/app-x` | the evidence, printed |
| 7. Package | tag the app repo | EXE and APK through `app-builder` |

---

## What "done" means here

| Claim | Evidence required |
|---|---|
| The app works | `kiln verify out/<app>` exits 0, output pasted into `RUNS.jsonl` |
| The app is offline | no `http://`, `https://`, `fetch(` in `index.html`, asserted |
| The spec is honest | every `done_means` names an observable outcome |
| Nothing is unwired | every declared feature and field appears in the artifact |
| No skeleton shipped | no `TODO`, `FIXME`, `lorem ipsum` in the artifact |

A completion that has no command and no output is not a completion.

---

## Adding a feature

| Order | Step |
|---|---|
| 1 | Add the entry to `catalog/features.json` — aliases, requires, kit, assertion |
| 2 | Gate the behaviour in `templates/app/index.html` on `F.has("<id>")` |
| 3 | Add the assertion to `templates/app/smoke.py` if it is new behaviour |
| 4 | Add a test in `tests/` that a spec using the feature builds and verifies |
| 5 | `python3 -m kiln audit --write` to refresh `INDEX.md` |
| 6 | Push. CI runs every spec, every guard |

A feature without an assertion is rejected by `catalog.load()`.

---

## CI jobs

| Job | Runs | Fails when |
|---|---|---|
| `test` | unit tests on 3.9–3.12 | any test fails |
| `verify-all` | every spec built and checked | any check fails |
| `audit` | the Forge-defect guards, then `git diff --exit-code INDEX.md` | a guard fails, or the index is stale |
| `lint` | shellcheck, `compileall` | a script or module is broken |

---

## The optional LLM path

| Rule | Detail |
|---|---|
| Off by default | no key, no config, nothing to disable |
| Scope | `specs/` only. `out/` is generated, never drafted |
| Provider | anything OpenAI-compatible, plus a local endpoint |
| Failure | if the call fails, the spec is unchanged and `intake` is still available |

Config lives at `~/.kiln/config.json`, outside the repo, so a key can never be committed.

---

## When something is wrong

| Symptom | First command |
|---|---|
| "unknown feature" | `kiln catalog` |
| "no observable outcome" | rewrite the `done_means` entry as something a person can watch |
| "does not match filename" | rename the file to the spec `id` |
| "index is stale" | `kiln audit --write` |
| a guard fails on a repo you cannot see | `kiln preflight` — it separates 404 from permission |
