# Monthly Summary

```json kiln
{
  "id": "app-monthly-summary",
  "name": "Monthly Summary",
  "tier": 2,
  "category": "clinical",
  "pattern": "report",
  "pitch": "Every consultation, summarised by kind, with the money added up.",
  "features": ["crud", "report", "search", "print", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "entry",
      "label": "Entry",
      "fields": [
        {"name": "title", "label": "Entry", "type": "text", "required": true},
        {"name": "kind", "label": "Kind", "type": "select",
         "options": ["first", "follow-up", "acute", "advice"]},
        {"name": "fee", "label": "Fee", "type": "currency_cents"},
        {"name": "date", "label": "Day", "type": "date"}
      ]
    }
  ],
  "report": {"group": "kind", "sum": "fee"},
  "currency": "₹",
  "storage": {"kind": "localstorage", "namespace": "monthly-summary"},
  "accent": "#38bdf8",
  "done_means": [
    "three entries in two kinds show two summary rows and a grand total",
    "the kind with the larger sum is shown first",
    "the grand total shows the sum of every fee in the list",
    "the print button produces a page with the summary table on it"
  ],
  "not": ["network calls", "accounts", "sync", "date ranges", "two-dimensional crosstab"]
}
```

## Pitch

Every consultation, summarised by kind, with the money added up.

## The job

- Keep a record of consultations with a kind and a fee
- See the count and the money per kind
- See the grand total
- Print it for the month file
- Take the rows out as a file

## The mechanic

The summary is derived from the rows on every render, so it cannot disagree with them. Groups
are ordered by their sum, then their count, then their name — a stable order, so the same rows
always print the same way.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No date ranges, no period filter
- No crosstab: one grouping level only

## What it does when things go wrong

- **bad input** — an entry without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the entry stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:monthly-summary:corrupt`, the rows reset

## Done means

- Three entries in two kinds show two summary rows and a grand total
- The kind with the larger sum is shown first
- The grand total equals the sum of every fee in the list
- The print button produces a page with the summary table on it

## The data

Stored in `localStorage` under `kiln:monthly-summary`. Fees are integer cents, so a sum is
exact.
