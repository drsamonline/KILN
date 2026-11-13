# Guide — cookbook

> **TL;DR** — one recipe per archetype. Four are buildable today and live in
> [`specs/gallery/`](specs/gallery); the rest are named so you know what is coming, not
> promised as if it worked. Every recipe is a spec, not code.

---

## The four you can build now

### 1. A list of records — `crud-list`

```bash
python3 -m kiln build specs/gallery/crud-list.md -o out
```

| | |
|---|---|
| Shape | one entity, one list, one form |
| Spec | [`specs/gallery/crud-list.md`](specs/gallery/crud-list.md) |
| Screenshot | [`docs/gallery/crud-list.png`](docs/gallery/crud-list.png) |
| Shows off | `currency_cents`, sort, search, export |

### 2. One number a day — `tracker`

| | |
|---|---|
| Shape | a value per day, with a streak, an average, a goal and a week of bars |
| Spec | [`specs/gallery/tracker.md`](specs/gallery/tracker.md) |
| Screenshot | [`docs/gallery/tracker.png`](docs/gallery/tracker.png) |
| Shows off | `tracker` key, `derived`, `chart` |

```json kiln
"tracker": {"field": "litres", "goal": 2.5, "window": 7, "unit": "L"}
```

### 3. Things that get done — `checklist`

| | |
|---|---|
| Shape | a bool per row and a progress bar |
| Spec | [`specs/gallery/checklist.md`](specs/gallery/checklist.md) |
| Screenshot | [`docs/gallery/checklist.png`](docs/gallery/checklist.png) |
| Shows off | `progress`, `toggle` |

### 4. One calculation — `calculator`

| | |
|---|---|
| Shape | inputs, a formula, an answer. No entity, no storage |
| Spec | [`specs/gallery/calculator.md`](specs/gallery/calculator.md) |
| Screenshot | [`docs/gallery/calculator.png`](docs/gallery/calculator.png) |
| Shows off | `formula`, the parser, no `eval` |

---

## The recipes that are not written yet

Listed in [`docs/PATTERNS.md`](docs/PATTERNS.md) with their trade-offs. Naming one in a spec
fails verification, deliberately.

| Archetype | The app it would make | Blocked on |
|---|---|---|
| master-detail | a project and its tasks | relations |
| kanban | a pipeline, dragged between columns | a second view |
| calendar | appointments by month | date maths and a grid |
| journal | a dated entry with no numbers | a detail view |
| dashboard | several metrics at once | multi-entity |
| wizard | a multi-step form | conditional fields |
| quiz | a deck with a score | an answer model |
| converter | units in, units out | one more input than `calculator` |
| voting | collect answers on one device | a tally view |
| comparison | a feature matrix | column model |
| gallery | cards with images | image metadata |
| grid | habits × days | a matrix view |
| search-directory | a searchable library | full-text index |
| timeline | a trip itinerary | ordering and grouping |
| inventory | stock with movements | a second entity |
| budget | envelopes and spend | multi-entity |
| invoice | line items and a total | money arithmetic across rows |
| splitter | split a receipt | rounding rules |
| log | time and mileage | duration field |
| register | attendance and grades | a matrix view |
| scheduler | bookings without overlap | date maths |
| playlist | a queue with order | manual ordering |
| formula-app | derived fields everywhere | `computed` field type |
| decision-log | decisions and outcomes | a detail view |
| report | a printable record | a print layout |

---

## Writing a recipe for an archetype you added

| # | Step |
|---|---|
| 1 | copy the shape of an existing recipe above |
| 2 | point it at your `specs/gallery/<id>.md` and `docs/gallery/<id>.png` |
| 3 | add the row to the "not written yet" table's replacement — delete the row |
| 4 | `python3 -m kiln audit` — guard `C15` checks the sample and the screenshot exist |

## Links

- [`docs/PATTERNS.md`](docs/PATTERNS.md) — pros, cons, and the numbers each pattern derives
- [`GUIDE-SPEC-REF.md`](GUIDE-SPEC-REF.md) — the keys these recipes use
- [`specs/gallery/`](specs/gallery) — the specs themselves
