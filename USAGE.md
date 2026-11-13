# User guide

Everything you need to go from an idea to an app that runs. Fifteen minutes, no
installation, no account.

---

## 1. Get the tool

```bash
git clone https://github.com/drsamonline/KILN.git
cd KILN
python3 -m kiln doctor
```

`doctor` prints what your machine has. If it says `network needed: no`, you are ready.
No Python? See [`INSTALL.md`](INSTALL.md) — `studio.html` needs only a browser.

---

## 2. Pick a way in

### A. One sentence

```bash
python3 -m kiln new "a tea log with tags and search"
python3 -m kiln build specs/app-tea.md -o out
```

Open `out/app-tea/index.html`. That is the app.

### B. A model's help, by copy-paste

```bash
python3 -m kiln prompt --idea "a tea log" --record "teas" --out p.txt
```

Paste `p.txt` into any chat window. Save the reply as `reply.md`. Then:

```bash
python3 -m kiln adopt reply.md --build
```

`adopt` prints every repair it made. Read them — they tell you what the model got wrong.

### C. A form, on a phone

Send yourself `studio.html`. Open it. Fill three boxes, tick the features, tap **Build app**.
The app downloads. Nothing was uploaded.

---

## 3. Read the spec before you trust the app

A spec is one Markdown file with two halves:

| Half | Who reads it |
|---|---|
| the `json kiln` block | the compiler |
| the prose below it | you, and whoever reviews your work |

The prose is not decoration. `## What it must NOT do` and `## What it does when things go
wrong` are the two sections that stop an app from quietly becoming something else.

Full field-by-field reference: [`docs/SPEC-REFERENCE.md`](docs/SPEC-REFERENCE.md).

---

## 4. Everyday tasks

| I want to | Do this |
|---|---|
| add a field | add it to `entities[0].fields` in the spec, rebuild |
| add a feature | add its id to `features`, rebuild — dependencies come with it |
| change the colour | set `accent` to a `#rrggbb` value |
| rename the app | change `name`, and rename the file to match `id` |
| build every spec | `python3 -m kiln build --all -o out` |
| see what will be written | `python3 -m kiln compose specs/app-x.md` |
| prove an app is offline | `python3 -m kiln verify out/app-x` |
| package it | `python3 -m kiln pipeline "…" --zip` |

---

## 5. What the generated app does

| Action | Where |
|---|---|
| add a record | **New**, top right |
| edit or delete | on the row |
| search | the search box, or `Ctrl-K` |
| sort | the sort dropdown |
| filter | the filter dropdown, if the app has `filters` |
| export | **Export** → JSON and CSV files |
| import | **Import** → choose a JSON file |
| theme | **Theme** |
| print | **Print** |
| switch language | the `EN/हिं` button, if the app has `i18n` |

**Your data lives in that browser, on that device.** Clearing site data deletes it. Export
is the backup.

---

## 6. Editions

| I want to | Command |
|---|---|
| see what my builds will carry | `python3 -m kiln licence` |
| see both editions | `python3 -m kiln licence tiers` |
| activate a purchased key | `python3 -m kiln licence activate KILN1.…` |
| build with the edition my key names | `python3 -m kiln build specs/app-x.md` |
| force a Personal build | `python3 -m kiln build specs/app-x.md --tier personal` |
| check a key without activating it | `python3 -m kiln licence verify KILN1.…` |

Owner-only, once per machine: `python3 -m kiln licence keygen` writes the private key to
`~/.kiln/private.key` and pins the public half in `catalog/licence-key.json`. Then
`kiln licence issue --to "Name" --tier commercial --days 365` prints the key to send.
Two editions only: Personal (free, sponsor block in the app) and Commercial (paid, no
sponsor block). Full table: [`LICENSING.md`](LICENSING.md).

## 7. When something goes wrong

| Message | Meaning | Fix |
|---|---|---|
| `unknown features: x` | the catalogue has no such feature | `kiln catalog` |
| `done_means[0] names no observable outcome` | the sentence cannot be checked | rewrite it as something a person can watch happen |
| `does not match filename` | the file name and the spec `id` disagree | rename one |
| `no ```json kiln block found` | the spec has no machine block | `kiln adopt` can add one, or copy `specs/app-notes.md` |
| `index is stale` | `INDEX.md` is behind `specs/` | `kiln audit --write` |
| `studio.html is stale` | the studio is behind its sources | `kiln studio` |
| an app shows "Nothing here yet" | correct — there are no records | add one |
| an app lost its records | site data was cleared, or a private window closed | import your last export |

---

## 8. Where the limits are

| Limit | Reality |
|---|---|
| 14 features | a feature not in `catalog/features.json` cannot be used. Fork it if you need more |
| one entity per spec | the runtime renders one list. Multi-entity apps are not supported yet |
| `localStorage` only | no SQLite, no files, no sync |
| a few thousand rows | linear search is fine up to that; beyond it, export and start a new file |
| one HTML file | if you need a build pipeline, this is the wrong tool |

These are choices, not oversights. The catalogue is the design space, and a bounded design
space is what makes the output reliable.
