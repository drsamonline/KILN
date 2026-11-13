# Guide: limits

> **TL;DR**: this page is the honest list of what KILN will not do. Every line is something
> you would otherwise discover by building an app and finding the gap.

---

## What the compiler will not do

| Limit | Why | Where to look instead |
|---|---|---|
| No server, no API, no sync | the output is one file opened from disk | [`GUIDE-PATTERNS.md`](GUIDE-PATTERNS.md) |
| No accounts, no login | there is nobody to authenticate against | — |
| No encryption at rest | a single HTML file cannot hold a key safely | use full-disk encryption |
| No rich text or images | plain text keeps the file small and the diff readable | — |
| No multi-entity apps | one list per app, except where a pattern adds a view | `dashboard` and `master-detail` are not built |
| No conditionals in forms | every field in a step is always shown | [`GUIDE-PATTERNS.md`](GUIDE-PATTERNS.md) |
| No drag and drop | two buttons per card work with a keyboard too | the `kanban` pattern |
| No charts beyond a sparkline | a chart library would break the no-dependency rule | the `tracker` pattern |
| No timers, no notifications | a closed file cannot ring | — |
| No import from other formats | only its own JSON export | — |

## What the *generated app* will not do

| Limit | Detail |
|---|---|
| Work across devices | the data lives in one browser's `localStorage` |
| Survive clearing site data | export first; the backup banner says so after 7 days |
| Handle more than a few thousand rows gracefully | search is a linear scan; the banner appears past 2000 |
| Protect itself from editing | the file is text; the fingerprint is evidence, not a lock |
| Recover a deleted record | there is no undo; export is the backup |

## What the *tooling* will not do

| Limit | Detail |
|---|---|
| Install anything | Python 3.9+ and the standard library |
| Reach the network | no command opens a socket, except the model call you make by hand |
| Guess a spec you did not write | `kiln adopt` repairs, it does not invent |
| Emit a capability that is not in the catalogue | it fails instead, on purpose |
| Emit two archetypes at once | a spec names one pattern |

## The honest summary

KILN is good at: **one list, one screen, one device, one file**. Everything outside that
sentence is either a pattern that has not been written, or something a browser cannot do.

## Links

- [`GUIDE-PATTERNS.md`](GUIDE-PATTERNS.md): what each archetype can and cannot do
- [`docs/PATTERNS.md`](docs/PATTERNS.md): the cons column, in full
- [`GUIDE-LICENSING.md`](GUIDE-LICENSING.md): the two editions
- [`docs/FAQ.md`](docs/FAQ.md): the questions this page usually answers
