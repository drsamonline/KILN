# SELF-CONTAINED

The promise: this folder, and nothing else, produces an app. No other repository,
no package manager, no key, no network.

---

## What "bundled" means here

| Thing | Where it lives | How it gets in |
|---|---|---|
| The runtime (CRUD, storage, search, export, theme) | `templates/app/index.html` | it is the template |
| The five kits | regions of that same file, named in `catalogue/kits.json` | nothing to fetch |
| The feature catalogue | `catalogue/capabilities.json` | read at runtime by the CLI |
| The spec schema | `schema/spec.schema.json` + `kiln/spec.py` | one shape, checked in code |
| The prompt | `PROMPT.md` | one text file you can copy by hand |
| The browser version | `studio.html`, generated from the two above | `kiln studio` |

`catalogue/kits.json` names no repository. That was a defect in v0.1 and it is
gone: a kit is a capability of the template, not a repo to clone.

---

## The check

```bash
python3 -m kiln doctor
python3 -m kiln audit
```

`doctor` prints what the machine has. `audit` includes two guards that matter here:

| Guard | What it fails on |
|---|---|
| `C7 studio.html matches its sources` | the committed studio drifting from the template or catalogue |
| `C7 studio.html has no http://` | any external reference sneaking into the studio |

And one that keeps the prompt honest:

| Guard | What it fails on |
|---|---|
| `B6 PROMPT.md lists every feature` | the prompt offering a feature the compiler does not have |
| `B6 PROMPT.md states the requires of each feature` | a dependency the model cannot know about |

---

## Copying it somewhere with no internet

| Target | Steps |
|---|---|
| USB stick | copy the folder; `python3 -m kiln build specs/app-notes.md` |
| A machine with no Python | copy `studio.html` only — it is the whole builder |
| A phone | send yourself `studio.html`; open it; tap Build |
| An air-gapped server | copy the folder, run the tests, then build |

---

## What is deliberately not vendored

| Not included | Why |
|---|---|
| A Python web server | the output needs no server |
| A framework (React, Vue) | 21 KB of vanilla beats 200 KB of runtime on a USB stick |
| A database | `localStorage` is the database |
| A bundler | there is nothing to bundle |
| Fonts | the system font is the font |
| An icon set | the app has no icons, and that is a feature |

---

## The one thing that is optional by design

The model. `kiln prompt` prints text; `kiln adopt` reads text. Neither opens a
socket. If you never use a model, `kiln new`, `studio.html` and `specs/` cover
every case the catalogue supports.
