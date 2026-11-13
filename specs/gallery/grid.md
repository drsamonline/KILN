# Visits by Kind and Month

```json kiln
{
  "id": "app-visits-grid",
  "name": "Visits by Kind and Month",
  "tier": 2,
  "category": "clinical",
  "pattern": "grid",
  "pitch": "Two dimensions at once: what kind of visit, in which month.",
  "features": ["crud", "crosstab", "search", "print", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "visit",
      "label": "Visit",
      "fields": [
        {"name": "title", "label": "Patient", "type": "text", "required": true},
        {"name": "kind", "label": "Kind", "type": "select",
         "options": ["first", "follow-up", "acute"]},
        {"name": "month", "label": "Month", "type": "select",
         "options": ["2026-09", "2026-10", "2026-11"]},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "crosstab": {"row": "kind", "column": "month"},
  "storage": {"kind": "localstorage", "namespace": "visits-grid"},
  "accent": "#38bdf8",
  "done_means": [
    "four records over two kinds and two months show four cells and two totals",
    "an empty cell shows a dot, not a blank",
    "the bottom row shows a total per month and the right column a total per kind",
    "the grand total in the corner shows the number of records"
  ],
  "not": ["network calls", "accounts", "sync", "a third dimension", "sums in the cells"]
}
```

## Pitch

Two dimensions at once: what kind of visit, in which month.

## The job

- Record visits with a kind and a month
- See the grid of kind against month
- Spot the empty cells, which are usually the finding
- Read the totals on both edges
- Print it for the month file

## The mechanic

Rows are one field's values, columns are another's, and each cell is a count. Both edges are
totalled and the corner holds the grand total, so the margins cost nothing.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No third dimension, no drill-down
- Cells hold counts, not sums

## What it does when things go wrong

- **bad input** — a visit without a patient refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the visit stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:visits-grid:corrupt`, the grid resets

## Done means

- Four records over two kinds and two months fill four cells and two totals
- An empty cell shows a dot rather than a blank
- The bottom row totals each month and the right column totals each kind
- The grand total in the corner equals the number of records

## The data

Stored in `localStorage` under `kiln:visits-grid`. Both dimensions are short text values, which
is what keeps the grid readable.
