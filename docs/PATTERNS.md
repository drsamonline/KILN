# Patterns

An archetype is a shape of app: the view, the data, and the handful of behaviours that
make that shape work. A spec names one with `"pattern": "<id>"`, and `kiln verify` then
checks that the spec satisfies what the pattern promises.

One archetype per pull request. Never two.

---

## The template

```markdown
## <name>

Pros:      (3–5 bullets)
Cons:      (3–5 bullets)
Best for:  <one line>
Avoid if:  <one line>
Spec keys: <list>
Sample:    specs/gallery/<name>.md
```

Every pattern file carries the same fields in `catalogue/patterns/<id>.json`:
`requires_capabilities`, `requires_fields`, `spec_defaults`, `verify_checks`, `pros`, `cons`,
`best_for`, `avoid_if`, `sample`, `screenshot`, `status`.

---

## crud-list

| | |
|---|---|
| Archetype | 1 |
| Status | **emitted** |
| View | table |
| Requires | `crud`, `search`, `sort`, `stats`, `export`, `theme` |
| Sample | [`specs/gallery/crud-list.md`](../specs/gallery/crud-list.md) |
| Screenshot | [`docs/gallery/crud-list.png`](gallery/crud-list.png) |

**Pros**

- the fastest shape to build and to use
- one form, one list, nothing to learn
- search and sort come free from the runtime
- prints and exports without extra work

**Cons**

- linear search: fine to a few thousand rows, slow beyond
- no relations, so a second entity needs a second app
- one view, so comparison across records is manual

**Best for:** a single flat list of records that one person maintains.

**Avoid if:** records point at other records, or the app needs two lists at once.

**Spec keys:** `pattern`, `features`, `entities[].fields[]`, `currency`, `accent`

---

## The seed table

Filled in as each archetype lands. "Planned" means the descriptor does not exist yet, so a
spec naming it fails verification rather than silently building something else.

| Archetype | Pros | Cons | Status |
|---|---|---|---|
| crud-list | fast, familiar | linear search >5k rows | **emitted** |
| Master-detail | shows relations | more spec surface | planned |
| Kanban | status at a glance | mobile-unfriendly >5 cols | planned |
| Calendar | time context | overlap, cramped month view | planned |
| Tracker | streaks, motivation | needs discipline | planned |
| Journal | low friction | no encryption | planned |
| Dashboard | insight at a glance | charts add weight | planned |
| Wizard | guided, fewer errors | long specs, slow for pros | planned |
| Quiz / Flashcard | a learning loop | content authoring burden | planned |
| Calculator | tiny, instant | no persistence by default | planned |
| Converter | tiny, offline | rounding discipline | planned |
| Voting / Poll | quick collection | single device only | planned |
| Comparison table | decision clarity | rigid for small sets | planned |
| Gallery / Cards | visual, scannable | verbose for data-heavy | planned |
| Grid / Matrix | many dimensions | cramped on mobile | planned |
| Search directory | scales by search | still linear underneath | planned |
| Print / Report | shareable artefact | layout brittle across browsers | planned |

---

## Adding an archetype

| # | Step | Checked by |
|---|---|---|
| 1 | write `catalogue/patterns/<id>.json` | guard `C15` |
| 2 | write `specs/gallery/<id>.md` | `verify` on the spec |
| 3 | render `docs/gallery/<id>.png` | `verify` on the pattern |
| 4 | add the block above, and the seed-table row | `C15` |
| 5 | register any new field types in `catalogue/features/` | `C14` |
| 6 | add a test that the sample builds and verifies | `tests/` |

A pattern with no sample, no screenshot or no pros/cons block fails the build.
