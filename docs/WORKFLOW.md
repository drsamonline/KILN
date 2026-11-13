# WORKFLOW

## The three paths

| Path | Steps | When |
|---|---|---|
| Phrase | `kiln new "…"` → `kiln build` | you know what you want in a sentence |
| Prompt | `kiln prompt` → paste into a model → `kiln adopt reply.md --build` | you want a fuller spec than one sentence gives |
| Form | open `studio.html` → fill → Build | you are on a phone, or you want to see the fields |

All three produce the same document and the same app.

---

## One command, whole pipeline

```bash
python3 -m kiln pipeline "a reading log with tags and a rating" --zip
```

| Step | Output |
|---|---|
| 1 | spec written to `out/app-reading.md` |
| 2 | app emitted to `out/app-reading/` |
| 3 | verification passed, or it stops |
| 4 | `out/app-reading.zip` |

---

## Step by step

| Step | Command | What it proves |
|---|---|---|
| 1. Describe | `kiln intake "a clinic log with search and print"` | the phrase maps to catalogue features, and you can see why |
| 2. Write the spec | `kiln new "…" --out specs/` | a spec exists that passes the schema |
| 3. Edit the prose | open `specs/app-x.md` | the human contract says what the machine block cannot |
| 4. Compose | `kiln compose specs/app-x.md` | the file plan, before anything is written |
| 5. Build | `kiln build specs/app-x.md -o out/` | the app, plus a verify pass |
| 6. Verify | `kiln verify out/app-x` | the evidence, printed |
| 6b. Compare | `kiln verify out/app-x --golden` | nothing changed since the build you accepted |
| 7. Package | tag the app repo | EXE and APK through your `app-builder` |

---

## The prompt path, in detail

| Step | Command | Notes |
|---|---|---|
| 1 | `kiln prompt --idea "…" --record "teas" --out p.txt` | writes the filled prompt |
| 2 | paste `p.txt` into any model | phone, local, hosted, terminal |
| 3 | save the reply as `reply.md` | chatter included, it does not matter |
| 4 | `kiln adopt reply.md --out specs/` | prints every repair it made |
| 5 | `kiln adopt reply.md --build` | repairs, writes, builds, verifies |

`adopt` is idempotent: running it on its own output reports no repairs.

---

## What "done" means here

| Claim | Evidence required |
|---|---|
| The app works | `kiln verify out/<app>` exits 0 |
| The app is offline | no `http://`, `https://`, `fetch(` in `index.html`, asserted |
| The spec is honest | every `done_means` names an observable outcome |
| Nothing is unwired | every declared feature and field appears in the artifact |
| No skeleton shipped | no `TODO`, `FIXME`, `lorem ipsum` in the artifact |
| The prompt is honest | `PROMPT.md` lists exactly the features that exist |
| The studio is current | `studio.html` matches `kiln studio` byte for byte |

A completion with no command and no output is not a completion.

---

## Adding a feature

| Order | Step |
|---|---|
| 1 | Add the entry to `catalogue/capabilities.json` — aliases, requires, kit, assertion |
| 2 | Add the row to the table in `PROMPT.md` |
| 3 | Gate the behaviour in `templates/app/index.html` on `F.has("<id>")` |
| 4 | Add the assertion to `templates/app/smoke.py` if it is new behaviour |
| 5 | Add a test in `tests/` that a spec using the feature builds and verifies |
| 6 | `kiln studio && kiln audit --write` to regenerate the studio and the index |
| 7 | Push. CI runs every spec, every guard |

`kiln audit` fails if step 2 or step 6 is forgotten. That is the point.

---

## CI jobs

| Job | Runs | Fails when |
|---|---|---|
| `test` | unit tests on 3.9–3.13 | any test fails |
| `verify-all` | every spec built and checked, then the studio built | any check fails |
| `audit` | the guards, then `git diff --exit-code INDEX.md` | a guard fails or the index is stale |
| `lint` | shellcheck, `compileall` | a script or module is broken |

---

## When something is wrong

| Symptom | First command |
|---|---|
| "unknown feature" | `kiln catalog` |
| "no observable outcome" | rewrite the `done_means` entry as something a person can watch |
| "no spec object found" | the reply had no JSON object — re-run `kiln prompt` |
| "does not match filename" | rename the file to the spec `id` |
| "index is stale" | `kiln audit --write` |
| "studio.html is stale" | `kiln studio` |
| a guard fails on a repo you cannot see | `kiln preflight` — it separates 404 from permission |
