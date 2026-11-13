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

## checklist

| | |
|---|---|
| Archetype | 19 |
| Status | **emitted** |
| View | table, with a progress bar above it |
| Requires | `crud`, `search`, `sort`, `progress`, `toggle`, `theme` |
| Requires fields | a `bool` |
| Spec keys | `pattern`, `progress.field`, `progress.label` |
| Sample | [`specs/gallery/checklist.md`](../specs/gallery/checklist.md) |
| Screenshot | [`docs/gallery/checklist.png`](gallery/checklist.png) |

**Pros**

- the bar answers "am I nearly there" without counting
- one tap per row, no form, so it is usable while packing
- it survives a reload, which a paper list does not
- grouping by category is one select field away

**Cons**

- one level: no sub-items, so a nested checklist needs a second app
- no assignee, so a shared list is out of scope
- no reminders, so it only helps once you open it
- reordering by hand is not available; sort is by field

**Best for:** a finite set of things that each end up done.

**Avoid if:** items have sub-items, quantities to reconcile, or owners.

**What is derived**

| Number | Rule |
|---|---|
| done / total | rows whose bool field is true, over rows that carry the field |
| left | total − done |
| percent | done ÷ total, rounded to the nearest whole number |
| the bar | the percent, as a width, with `role="progressbar"` and `aria-valuenow` |

---

## calculator

| | |
|---|---|
| Archetype | 10 |
| Status | **emitted** |
| View | form — **no entity at all** |
| Requires | `formula`, `theme` |
| Requires fields | none |
| Spec keys | `pattern`, `calculator.inputs[]`, `calculator.formula`, `calculator.output` |
| Sample | [`specs/gallery/calculator.md`](../specs/gallery/calculator.md) |
| Screenshot | [`docs/gallery/calculator.png`](gallery/calculator.png) |

**Pros**

- nothing to store, so nothing to lose and nothing to back up
- instant: one screen, one answer, no save button
- the formula is data in the spec, so a new calculator is a new spec, not new code
- works from a USB stick with no network, which is when you need it

**Cons**

- no history, so a result cannot be revisited tomorrow
- one formula per app: a second calculation needs a second app
- the parser is deliberately small: no dates, no percentages of a base, no lookups
- it cannot explain itself beyond the label and the unit

**Best for:** one calculation done repeatedly, where a spreadsheet is overkill.

**Avoid if:** the answer depends on records kept over time, or several formulas are needed.

**The grammar, and what it will not do**

| Supported | Not supported |
|---|---|
| `+ - * / % ^`, parentheses, unary minus | dates, strings, comparisons |
| named inputs from `calculator.inputs` | lookups into records |
| `min max abs round floor ceil sqrt pow` | user-defined functions |
| integers and decimals | money (use `currency_cents` in a list app) |

The parser is a recursive-descent evaluator in the page. `eval` and `new Function` are
forbidden, and `verify` fails a build that contains either.

---

## converter

| | |
|---|---|
| Archetype | 11 |
| Status | **emitted** |
| View | form — one amount, two unit selects |
| Requires | `convert`, `theme` |
| Requires keys | `converter.units[]`, `converter.default_from`, `converter.default_to` |
| Sample | [`specs/gallery/converter.md`](../specs/gallery/converter.md) |
| Screenshot | [`docs/gallery/converter.png`](gallery/converter.png) |

**Pros**

- the factor table is data, so a new dimension is a new spec
- no storage and no history: nothing to lose, nothing to clear
- two selects and one number, so it is usable one-handed
- exact factors in the spec, not rounded constants in code

**Cons**

- one dimension per app; temperature needs an offset, which this does not do
- no history, so a conversion cannot be revisited
- the factors are as good as whoever typed them
- it will not tell you which unit is sensible

**Best for:** one family of units, converted often.

**Avoid if:** the conversion needs an offset (temperature), or several dimensions at once.

**The rule:** `amount × factor_from ÷ factor_to`, against one base unit. A mile is
1609.344 metres because the spec says so, not because the code remembers it.

---

## wizard

| | |
|---|---|
| Archetype | 8 |
| Status | **emitted** |
| View | form, in steps |
| Requires | `crud`, `steps`, `theme` |
| Requires keys | `wizard.steps[]` |
| Sample | [`specs/gallery/wizard.md`](../specs/gallery/wizard.md) |
| Screenshot | [`docs/gallery/wizard.png`](gallery/wizard.png) |

**Pros**

- a long form becomes three short ones, so it gets finished
- each step validates on its own, so the error is always near the field
- the step names double as a progress indicator
- the draft survives stepping back and forth

**Cons**

- more clicks than one form, which annoys an expert user
- conditional steps are not supported: every step is always shown
- no save-and-resume across sessions
- the step list is in the spec, so reordering means editing the spec

**Best for:** a record with more fields than fit on one screen.

**Avoid if:** the form is short, or the fields depend on each other.

**The rule:** a field belongs to exactly one step, and `verify` refuses a spec where a step
names a field that does not exist or repeats one.

---

## journal

| | |
|---|---|
| Archetype | 6 |
| Status | **emitted** |
| View | list + a read-only detail dialog |
| Requires | `crud`, `search`, `detail`, `theme` |
| Requires fields | a `longtext` and a `date` |
| Spec keys | `pattern`, `detail.field` |
| Sample | [`specs/gallery/journal.md`](../specs/gallery/journal.md) |
| Screenshot | [`docs/gallery/journal.png`](gallery/journal.png) |

**Pros**

- the entry is read at a comfortable width, not squeezed into a row
- one field carries the writing; everything else is a label
- search still finds a word from three months ago
- no formatting to fiddle with, so the writing gets done

**Cons**

- no rich text, no images: plain paragraphs only
- no encryption, and the file is a plain HTML file
- one entry per day is a habit, not an enforcement: duplicates are allowed
- no export to a diary format; JSON and CSV only

**Best for:** writing a paragraph or two, most days.

**Avoid if:** entries need images, or the writing must be encrypted at rest.

**The rule:** the list is for finding, the dialog is for reading. `detail.field` names the
long text that gets the width; every other field is shown as a labelled line.

---

## log

| | |
|---|---|
| Archetype | 24 |
| Status | **emitted** |
| View | table, with a running total in the strip |
| Requires | `crud`, `search`, `sort`, `totals`, `theme` |
| Requires fields | a `duration` and a `date` |
| Spec keys | `pattern`, `totals.field`, `totals.format`, `totals.label` |
| Sample | [`specs/gallery/log.md`](../specs/gallery/log.md) |
| Screenshot | [`docs/gallery/log.png`](gallery/log.png) |

**Pros**

- the running total answers "how much this month" without a spreadsheet
- a duration is entered in minutes and read as 1h 25m
- sorting by date or by length is one dropdown
- exports as minutes, so it opens in a spreadsheet unchanged

**Cons**

- one unit per app: minutes or kilometres, not both
- no start and stop timer; you type the minutes
- the total is over every row, not over a chosen period
- no charts: that is the tracker archetype

**Best for:** logging sessions and seeing the sum.

**Avoid if:** you need a timer, a per-period total, or two different measures.

**The rule:** `duration` is stored as whole minutes and formatted only when drawn; the total
is the sum of one field, recomputed on every render and never stored.

---

## kanban

| | |
|---|---|
| Archetype | 3 |
| Status | **emitted** |
| View | a board of columns |
| Requires | `crud`, `board`, `theme` |
| Requires fields | a `select` with at least two options |
| Spec keys | `pattern`, `board.field` |
| Sample | [`specs/gallery/kanban.md`](../specs/gallery/kanban.md) |
| Screenshot | [`docs/gallery/kanban.png`](gallery/kanban.png) |

**Pros**

- the state of everything is visible at once, without reading rows
- moving a card is one button, not an edit form
- the column counts are the summary, so no separate stats are needed
- it degrades to a scrolling row of columns on a phone

**Cons**

- no drag and drop: two buttons per card instead
- columns come from a select field, so adding a stage means editing the spec
- no work-in-progress limits, no swimlanes
- past four or five columns it wants a wide screen

**Best for:** work that moves through a handful of named stages.

**Avoid if:** the order within a column matters, or stages need rules.

**The rule:** the columns are the options of one select field, in the order the spec lists
them. A value outside that list lands in a column called Unplaced, and `verify` refuses a
board on anything but a select with two or more options.

---

## calendar

| | |
|---|---|
| Archetype | 4 |
| Status | **emitted** |
| View | a month grid |
| Requires | `crud`, `calendar`, `theme` |
| Requires fields | a `date` |
| Spec keys | `pattern`, `calendar.field` |
| Sample | [`specs/gallery/calendar.md`](../specs/gallery/calendar.md) |
| Screenshot | [`docs/gallery/calendar.png`](gallery/calendar.png) |

**Pros**

- time is the axis people already think in
- an empty day is a fact you can see, not one you have to compute
- clicking a day opens the form with the date filled in
- the grid is computed in UTC, so it cannot drift across a timezone

**Cons**

- no times of day: one date field, one cell
- no recurring entries, no multi-day spans
- two entries a day is the most a cell shows before it says "+N more"
- a phone gets a cramped month; the list is the better view there

**Best for:** one thing per day, seen across a month.

**Avoid if:** entries have times, durations, or spans across days.

**The rule:** six rows of seven, Monday first, 42 cells always, computed in UTC from
`YYYY-MM`. A day is a string, so grouping is a comparison and never a timezone.

---

## The seed table

Filled in as each archetype lands. "Planned" means the descriptor does not exist yet, so a
spec naming it fails verification rather than silently building something else.

| Archetype | Pros | Cons | Status |
|---|---|---|---|
| crud-list | fast, familiar | linear search >5k rows | **emitted** |
| Master-detail | shows relations | more spec surface | planned |
| kanban | status at a glance | mobile-unfriendly >5 cols | **emitted** |
| calendar | time context | overlap, cramped month view | **emitted** |
| tracker | streaks, motivation | needs discipline | **emitted** |
| checklist | packing, grocery | one level only | **emitted** |
| journal | low friction | no encryption | **emitted** |
| Dashboard | insight at a glance | charts add weight | planned |
| wizard | guided, fewer errors | long specs, slow for pros | **emitted** |
| Quiz / Flashcard | a learning loop | content authoring burden | planned |
| calculator | tiny, instant | no persistence by default | **emitted** |
| converter | tiny, offline | rounding discipline | **emitted** |
| Voting / Poll | quick collection | single device only | planned |
| Comparison table | decision clarity | rigid for small sets | planned |
| Gallery / Cards | visual, scannable | verbose for data-heavy | planned |
| Grid / Matrix | many dimensions | cramped on mobile | planned |
| Search directory | scales by search | still linear underneath | planned |
| log | time and mileage | duration field | **emitted** |
| Print / Report | shareable artefact | layout brittle across browsers | planned |

---

## Size, and the ceiling

The target is 40 KB per generated app. The enforced ceiling is 44 KB.

A capability that a spec does not declare is stripped at emit time, including its CSS and
its markup, so most apps sit between 34 and 40 KB. The tracker archetype is the exception:
`derived` + `chart` + `stats` + `search` + `sort` + `theme` together do not fit in 40 KB, and
dropping one would break the pattern's own contract. That is the written justification §5
asks for.

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
