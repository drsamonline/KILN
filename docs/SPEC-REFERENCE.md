# Spec reference

One file, two halves: a machine block the compiler reads, and prose a person reads.
A second shape is a validation error, never a warning.

---

## The file

````markdown
# Tea Log

```json kiln
{
  "id": "app-tea-log",
  "name": "Tea Log",
  "tier": 1,
  "category": "utility",
  "pitch": "Which tea, how strong, and whether to buy it again.",
  "features": ["crud", "search", "tags", "export", "theme"],
  "entities": [
    {"name": "tea", "label": "Tea", "fields": [
      {"name": "title", "label": "Name", "type": "text", "required": true},
      {"name": "body", "label": "Notes", "type": "longtext"},
      {"name": "tags", "label": "Tags", "type": "tags"},
      {"name": "amount", "label": "Steep seconds", "type": "number"}
    ]}
  ],
  "storage": {"kind": "localstorage", "namespace": "tea-log"},
  "accent": "#c08b5c",
  "done_means": [
    "saving a tea and reloading the page shows the tea in the list",
    "typing a word no tea contains hides every row"
  ],
  "not": ["network calls", "accounts"]
}
```

## Pitch
## The job
## The mechanic
## What it must NOT do
## What it does when things go wrong
## Done means
## The data
````

The file name must be `<id>.md`.

---

## Top-level keys

| Key | Type | Required | Rule |
|---|---|---|---|
| `id` | string | yes | `app-` then lowercase letters, digits, hyphens. Must equal the file name |
| `name` | string | yes | 1–40 characters |
| `tier` | int | yes | 1, 2 or 3. 1 = one list and a few fields |
| `category` | string | yes | one of the catalogue categories |
| `pitch` | string | yes | one sentence, 10–140 characters |
| `features` | string[] | yes | ids from the feature table below; no duplicates |
| `entities` | object[] | yes | at least one |
| `storage` | object | yes | `{"kind": "localstorage", "namespace": "<slug>"}` |
| `accent` | string | no | `#rrggbb`; default `#7c9cff` |
| `done_means` | string[] | yes | at least one, each must pass the lint below |
| `not` | string[] | yes | at least one thing the app refuses to do |

### Categories

`productivity` · `utility` · `health` · `education` · `finance` · `reference` · `creative` · `clinical` · `community`

---

## Entities and fields

| Key | Rule |
|---|---|
| `entities[].name` | lowercase, `snake_case`, unique |
| `entities[].label` | shown in the UI |
| `entities[].fields` | at least one |
| `fields[].name` | lowercase, `snake_case`, unique within the entity |
| `fields[].label` | shown on the form |
| `fields[].type` | one of the seven below |
| `fields[].required` | boolean; the form refuses to save without it |
| `fields[].options` | required for `select`, at least two strings |

The **first field is the row title** in the list. Keep it `text`.

### Field types

| Type | Control | Stored as |
|---|---|---|
| `text` | one-line input | string |
| `longtext` | textarea | string |
| `number` | number input, validated | number or null |
| `date` | date picker, `YYYY-MM-DD` | string |
| `bool` | checkbox | boolean |
| `select` | dropdown from `options` | string |
| `tags` | comma-separated input | array of strings |

---

## Features

| id | What it does | Needs |
|---|---|---|
| `crud` | create, read, update, delete | — |
| `search` | find records by typing | `crud` |
| `export` | download JSON and CSV | `crud` |
| `import` | restore from a JSON file | `crud` |
| `theme` | dark and light, remembered | — |
| `pwa` | inline manifest, installable | — |
| `tags` | tag chips on each record | `crud` |
| `filters` | facet filter per select or tag field | `crud`, `search` |
| `sort` | sort by any column | `crud` |
| `stats` | count and summary strip | `crud` |
| `reminder` | due dates with an overdue flag | `crud` |
| `print` | print stylesheet | `crud` |
| `i18n` | a second language toggle | `theme` |
| `backup` | one-click backup and restore | `export`, `import` |

Dependencies are added for you. A feature outside this table is a validation error.

---

## The done-means lint

Each entry must contain an observable verb **and** must not contain a vague phrase.

| Observable verbs | Vague phrases that fail |
|---|---|
| show, hide, save, reload, export, import, return, refuse, block, count, sort, filter, delete, restore, open, print, render, persist, replace | works as expected, works correctly, does what it says, does its job, as described, user-friendly, properly, and so on |

Stems are matched, so "reloading" passes and "as expected" does not.

---

## Prose sections

| Section | Rule |
|---|---|
| `## Pitch` | present, matches the JSON pitch |
| `## The job` | at least three bullets |
| `## The mechanic` | the one idea that makes it work |
| `## What it must NOT do` | at least one bullet |
| `## What it does when things go wrong` | four labelled bullets: bad input, no network, storage full, corrupt state |
| `## Done means` | one bullet per `done_means` entry |
| `## The data` | what is stored, where, and what leaves the device |

`kiln adopt` generates any section that is missing. `kiln new` writes all of them.

---

## Checking a spec

```bash
python3 -m kiln compose specs/app-x.md     # the file plan
python3 -m kiln build specs/app-x.md -o out
python3 -m kiln verify out/app-x
```

`compose` and `build` validate first. A spec that fails validation writes nothing.
