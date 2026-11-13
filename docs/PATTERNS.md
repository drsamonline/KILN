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

## tracker

| | |
|---|---|
| Archetype | 5 |
| Status | **emitted** |
| View | table, with a derived strip above it |
| Requires | `crud`, `search`, `sort`, `stats`, `derived`, `chart`, `theme` |
| Requires fields | a `number` and a `date` |
| Spec keys | `pattern`, `tracker.field`, `tracker.goal`, `tracker.window`, `tracker.unit` |
| Sample | [`specs/gallery/tracker.md`](../specs/gallery/tracker.md) |
| Screenshot | [`docs/gallery/tracker.png`](gallery/tracker.png) |

**Pros**

- the streak is the cheapest motivation a small app can offer
- one number a day is the lowest-friction input there is
- the average and the goal do the thinking, so the user does not
- the sparkline answers "how has this week gone" in one glance

**Cons**

- a missed day breaks the streak, and some people stop logging after that
- one metric per app: a second tracker needs a second app
- the window is a fixed N days, so a month view is not available yet
- no reminders, so the habit still depends on the user remembering

**Best for:** one number a day, against a goal the user sets once.

**Avoid if:** the value only makes sense as part of a longer record, or several metrics
need tracking together.

**What is derived, and how**

| Number | Rule |
|---|---|
| streak | consecutive days with a record, counting back from today; a streak ending yesterday still counts |
| days logged | distinct dates that have a record |
| average | sum ÷ days logged, not ÷ days in the window |
| goal | the window's total ÷ (goal × window), as a percentage |
| sparkline | one bar per day in the window, oldest first, inline SVG, no library |

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
| tracker | streaks, motivation | needs discipline | **emitted** |
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
