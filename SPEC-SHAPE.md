# SPEC-SHAPE — what a KILN spec must say

One shape. One machine block. One human contract. A second shape is a validation error.

---

## Layout

````markdown
# Notes

```json kiln
{
  "id": "app-notes",
  "name": "Notes",
  "tier": 1,
  "category": "productivity",
  "pitch": "Write a note, find it again, keep it on the device.",
  "features": ["crud", "search", "tags", "export", "theme"],
  "entities": [
    {
      "name": "note",
      "label": "Note",
      "fields": [
        {"name": "title", "label": "Title", "type": "text", "required": true},
        {"name": "body", "label": "Body", "type": "longtext"},
        {"name": "tags", "label": "Tags", "type": "tags"}
      ]
    }
  ],
  "storage": {"kind": "localstorage", "namespace": "notes"},
  "accent": "#7c9cff",
  "done_means": [
    "creating a note and reloading the page shows the note in the list",
    "typing in search hides every note whose title and body do not contain the query"
  ],
  "not": ["sync", "accounts", "network calls"]
}
```

## Pitch

One sentence, in the user's words.

## The job

What the user can accomplish, as a list.

## The mechanic

The one idea that makes it work. Not a feature list.

## What it must NOT do

The negative contract.

## What it does when things go wrong

- **bad input** — …
- **no network** — …
- **storage full** — …
- **corrupt state** — …

## Done means

Restate each `done_means` entry as the check a person would run.
````

---

## Machine block rules

| Field | Type | Required | Rule |
|---|---|---|---|
| `id` | string | yes | `app-<slug>`, matches the filename |
| `name` | string | yes | 1–40 chars |
| `tier` | int 1–3 | yes | 1 = small utility, 3 = large |
| `category` | string | yes | from `catalogue/categories.json` |
| `pitch` | string | yes | one sentence, ≤ 140 chars |
| `features` | string[] | yes | every entry must exist in `catalogue/capabilities.json`; no duplicates |
| `entities` | object[] | yes | at least one; names unique |
| `entities[].fields` | object[] | yes | at least one; `name` unique per entity |
| `fields[].type` | enum | yes | `text`, `longtext`, `number`, `date`, `bool`, `select`, `tags` |
| `fields[].required` | bool | no | default false |
| `fields[].options` | string[] | for `select` | at least two |
| `storage.kind` | enum | yes | `localstorage` (only supported value today) |
| `storage.namespace` | string | yes | `[a-z0-9-]+`, unique per app |
| `accent` | string | no | `#rrggbb` |
| `done_means` | string[] | yes | ≥ 1, each must pass the falsifiability lint |
| `not` | string[] | yes | ≥ 1 |

---

## Falsifiability lint

A `done_means` entry passes only if both hold:

| Rule | Detail |
|---|---|
| Contains an observable verb | one of: shows, hides, saves, reloads, exports, imports, returns, refuses, blocks, counts, sorts, filters, deletes, restores, opens, prints |
| Contains no vague phrase | rejects: "works as expected", "works correctly", "does what it says", "does its job", "as described", "user-friendly", "properly", "and so on" |

---

## Prose rules

| Section | Required | Checked |
|---|---|---|
| `## Pitch` | yes | present, ≤ 200 chars |
| `## The job` | yes | ≥ 3 bullets |
| `## The mechanic` | yes | present |
| `## What it must NOT do` | yes | ≥ 1 bullet |
| `## What it does when things go wrong` | yes | all four labelled bullets present |
| `## Done means` | yes | one bullet per `done_means` entry |
| `## The data` | yes | names what is stored and what leaves the device |

---

## Why the machine block is JSON and not YAML

| Reason | Detail |
|---|---|
| No dependency | `json` is stdlib; YAML needs a parser on every machine |
| No ambiguity | no tabs, no implicit typing, no duplicate-key surprises |
| Reviewable | a fenced block diffs cleanly in a pull request |
| Coexists with prose | the human contract stays readable underneath |
