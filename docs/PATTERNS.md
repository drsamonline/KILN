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

## search-directory

| | |
|---|---|
| Archetype | 17 |
| Status | **emitted** |
| View | a focused search box, cards underneath |
| Requires | `crud`, `search`, `directory`, `theme` |
| Requires fields | a `text` |
| Spec keys | `pattern`, `directory.subtitle`, `directory.body` |
| Sample | [`specs/gallery/search-directory.md`](../specs/gallery/search-directory.md) |
| Screenshot | [`docs/gallery/search-directory.png`](gallery/search-directory.png) |

**Pros**

- the cursor is already in the box, so the first keystroke is the search
- matches are highlighted, so you see why a card came back
- cards fit more per record than a row does
- no toolbar to learn: one box and a list

**Cons**

- search is still a linear scan, so it is not a real index
- nothing is shown until you type, which looks empty to a first-time user
- no sort and no filters: this view deliberately has one control
- cards are taller, so fewer records fit on a screen

**Best for:** a few hundred records you look up by name.

**Avoid if:** you need to browse, sort, or see everything at once.

**The rule:** the search box takes focus, the sort and filter controls are hidden, and a list
longer than three records shows a count instead of the rows until you type.

---

## comparison

| | |
|---|---|
| Archetype | 14 |
| Status | **emitted** |
| View | a fixed-column table |
| Requires | `crud`, `comparison`, `theme` |
| Requires fields | a `text` |
| Spec keys | `pattern`, `comparison.columns`, `comparison.highlight` |
| Sample | [`specs/gallery/comparison.md`](../specs/gallery/comparison.md) |
| Screenshot | [`docs/gallery/comparison.png`](gallery/comparison.png) |

**Pros**

- side by side is the only honest way to compare
- the best value is marked, so the eye does not have to hunt
- columns are chosen in the spec, so the table stays readable
- it scrolls horizontally rather than dropping columns

**Cons**

- one highlight direction per column: max or min, not both
- no weighting, no scoring, no verdict
- more than about six columns needs a wide screen
- a tie marks both rows, which is correct and occasionally surprising

**Best for:** a shortlist of options with a few attributes.

**Avoid if:** the decision needs weights, or the attributes are long text.

**The rule:** `comparison.columns` names at least two fields; `comparison.highlight` maps a
numeric column to `max` or `min`; the best value in each mapped column gets a mark.

---

## dashboard

| | |
|---|---|
| Archetype | 7 |
| Status | **emitted** |
| View | a strip of metric cards, a switcher, and one list at a time |
| Requires | `crud`, `multi`, `dashboard`, `theme` |
| Requires fields | a `text` on each entity |
| Spec keys | `pattern`, `dashboard.cards[]`, and **two or more entities** |
| Sample | [`specs/gallery/dashboard.md`](../specs/gallery/dashboard.md) |
| Screenshot | [`docs/gallery/dashboard.png`](gallery/dashboard.png) |

**Pros**

- two lists in one file, which most small tools actually need
- the cards answer the first question before any list is read
- each list keeps its own fields and its own form
- one storage key, one export, one backup

**Cons**

- no relation between the lists: a visit cannot point at a patient
- the cards are computed over every row, not over a chosen period
- four metrics is the sensible maximum before the strip wraps
- one list is visible at a time; there is no combined view

**Best for:** two related lists and a question about their totals.

**Avoid if:** the lists need to reference each other.

**The rule:** more than one entity requires the `multi` capability, and `multi` requires at
least two entities. A card names an entity, a metric (`count`, `sum`, `avg`, `max`, `min`,
`latest`), and a field for everything except `count`. Storage becomes `{v, data: {entity:
rows}}`; a single-entity app keeps the older `{v, rows}` shape.

---

## master-detail

| | |
|---|---|
| Archetype | 2 |
| Status | **emitted** |
| View | two lists, and a read view that lists a parent's children |
| Requires | `crud`, `multi`, `relation`, `detail`, `theme` |
| Requires fields | a `text`, and a `lookup` pointing at the master |
| Spec keys | `pattern`, `master_detail.master`, `.child`, `.field` |
| Sample | [`specs/gallery/master-detail.md`](../specs/gallery/master-detail.md) |
| Screenshot | [`docs/gallery/master-detail.png`](gallery/master-detail.png) |

**Pros**

- the parent read view becomes the place you work, not a list to scroll
- the pointer is stored as an id, so renaming a parent does not break it
- each list keeps its own fields, its own form and its own search
- one file, one export, both lists

**Cons**

- one level only: a child cannot have children
- no cascade: deleting a parent leaves its children pointing at nothing
- a lookup is a select, so it does not scale past a few hundred parents
- no cross-list search

**Best for:** a parent and its children, read and edited together.

**Avoid if:** the nesting is deeper than one level, or parents number in the thousands.

**The rule:** a `lookup` field stores an id and shows a title. `master_detail.field` must be
that lookup, and it must point at `master_detail.master`. Opening a master lists its
children; a child pointing at nothing is shown as an orphan, not hidden.

---

## inventory

| | |
|---|---|
| Archetype | 20 |
| Status | **emitted** |
| View | items, with a derived balance and a reorder flag |
| Requires | `crud`, `multi`, `relation`, `detail`, `balance`, `theme` |
| Requires fields | a `text`, a `lookup`, a `number` |
| Spec keys | `pattern`, `master_detail`, `balance.field`, `.lookup`, `.reorder` |
| Sample | [`specs/gallery/inventory.md`](../specs/gallery/inventory.md) |
| Screenshot | [`docs/gallery/inventory.png`](gallery/inventory.png) |

**Pros**

- the balance is derived, so it can never disagree with the movements
- a movement is signed, so receipts and issues are the same kind of record
- the reorder flag turns the list into a worklist
- the parent read view shows the history that produced the number

**Cons**

- the balance is recomputed on every render: fine at hundreds of movements, not at hundreds of thousands
- no valuation: quantities only, no price per movement
- no lot numbers, no expiry dates, no locations
- deleting a movement changes history with no audit trail

**Best for:** a small store room where the count must match the movements.

**Avoid if:** you need valuation, lots, or an audit trail.

**The rule:** the balance is the signed sum of the children that point at the parent. It is
never stored. An item at or below its reorder level is counted in the strip and shown in the
warning colour.

---

## timeline

| | |
|---|---|
| Archetype | 16 |
| Status | **emitted** |
| View | the list, grouped by month |
| Requires | `crud`, `timeline`, `theme` |
| Requires fields | a `date` |
| Spec keys | `pattern`, `timeline.field` |
| Sample | [`specs/gallery/timeline.md`](../specs/gallery/timeline.md) |
| Screenshot | [`docs/gallery/timeline.png`](gallery/timeline.png) |

**Pros**

- months are how people remember, so the list reads like a history
- a heading per month costs almost nothing and saves a lot of scanning
- it is the same records as the plain list, seen differently
- an empty month simply does not appear

**Cons**

- no year headings, so a long history is a long scroll
- no counts per month beyond the heading itself
- records without a date fall into a final group called Undated
- no zoom from month to day

**Best for:** a record of things that happened, read backwards.

**Avoid if:** the records are tasks rather than events.

**The rule:** the group key is the first seven characters of the date, months sort newest
first, and a record with no usable date goes into a final group called Undated rather than
being dropped.

---

## The seed table

Filled in as each archetype lands. "Planned" means the descriptor does not exist yet, so a
spec naming it fails verification rather than silently building something else.

| Archetype | Pros | Cons | Status |
|---|---|---|---|
| crud-list | fast, familiar | linear search >5k rows | **emitted** |
| master-detail | shows relations | more spec surface | **emitted** |
| kanban | status at a glance | mobile-unfriendly >5 cols | **emitted** |
| calendar | time context | overlap, cramped month view | **emitted** |
| tracker | streaks, motivation | needs discipline | **emitted** |
| checklist | packing, grocery | one level only | **emitted** |
| journal | low friction | no encryption | **emitted** |
| dashboard | insight at a glance | charts add weight | **emitted** |
| wizard | guided, fewer errors | long specs, slow for pros | **emitted** |
| Quiz / Flashcard | a learning loop | content authoring burden | planned |
| calculator | tiny, instant | no persistence by default | **emitted** |
| converter | tiny, offline | rounding discipline | **emitted** |
| Voting / Poll | quick collection | single device only | planned |
| comparison | decision clarity | rigid for small sets | **emitted** |
| Gallery / Cards | visual, scannable | verbose for data-heavy | planned |
| Grid / Matrix | many dimensions | cramped on mobile | planned |
| search-directory | scales by search | still linear underneath | **emitted** |
| log | time and mileage | duration field | **emitted** |
| inventory | stock accuracy | needs master-detail | **emitted** |
| timeline | chronology | long scroll | **emitted** |
| Print / Report | shareable artefact | layout brittle across browsers | planned |

---

## Size

**Target: under 100 KB. The ceiling is 100 KB, and it is a backstop, not a target.**

Most apps build at 38–43 KB. A capability a spec does not declare is stripped at emit time —
its code, its CSS and its markup — so a calculator does not carry the board, and a journal
does not carry the month grid. That is why the numbers stay where they are without anyone
rationing features.

The board and the calendar are the largest because the view is the point: a five-column board
and a forty-two cell grid emit more markup than a list.

If an app does pass 100 KB, that is a signal worth reading: either the spec asked for a great
many capabilities at once, or something is no longer being stripped.

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
