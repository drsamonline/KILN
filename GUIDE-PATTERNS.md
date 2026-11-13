# Guide: choosing an archetype

> **TL;DR**: an archetype is the shape of the app. Pick it before you write the spec;
> the pattern decides which capabilities and fields are required, and `kiln verify` fails
> a spec that does not satisfy the one it names.

---

## The question to ask first

| Your app is mostly… | Archetype |
|---|---|
| a list of records you add to | `crud-list` |
| one number a day, against a goal | `tracker` |
| a list of things that get done | `checklist` |
| one calculation, no list | `calculator` |

If none of those fit, the app probably needs an archetype that does not exist yet; see
[`docs/PATTERNS.md`](docs/PATTERNS.md) for the 17 seeded shapes and their trade-offs, and
[`GUIDE-CONTRIBUTE.md`](GUIDE-CONTRIBUTE.md) for what adding one costs.

## Status, and what "planned" means

| Status | Meaning |
|---|---|
| **emitted** | a descriptor, a sample spec, a screenshot, a verify check and a test exist |
| planned | listed in the seed table; a spec naming it fails verification rather than building something else |

A planned archetype is not a stub. Naming it is an error, on purpose.

## What each archetype costs

| Archetype | Capabilities it requires | Fields it requires | Needs an entity |
|---|---|---|---|
| `crud-list` | crud, search, sort, stats, export, theme | a `text` | yes |
| `tracker` | crud, search, sort, stats, derived, chart, theme | a `number` and a `date` | yes |
| `checklist` | crud, search, sort, progress, toggle, theme | a `bool` | yes |
| `calculator` | formula, theme | none | **no** |

## Using one

```bash
python3 -m kiln new "a packing list for camping" --pattern checklist
```

or in a spec:

```json kiln
{ "pattern": "checklist", "progress": {"field": "done", "label": "packed"} }
```

## Common mistakes

| Message | Fix |
|---|---|
| `pattern x: required features present` fails | add the capabilities the pattern lists |
| `pattern x: required field types present` fails | add the field type the pattern needs |
| `pattern x exists` fails | the id is misspelled, or the archetype is planned |
| `entities must be a non-empty list (this pattern needs one)` | only `calculator` may have none |

## Links

- [`docs/PATTERNS.md`](docs/PATTERNS.md): every archetype, with pros, cons and derived numbers
- [`GUIDE-FEATURES.md`](GUIDE-FEATURES.md): capabilities and the registry
- [`specs/gallery/`](specs/gallery): one working spec per archetype
