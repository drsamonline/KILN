# Remedy Cost Sheet

```json kiln
{
  "id": "app-remedy-cost",
  "name": "Remedy Cost Sheet",
  "tier": 2,
  "category": "clinical",
  "pattern": "formula-app",
  "pitch": "Bottles, strength and rate, and the cost of each line worked out for you.",
  "features": ["crud", "formula", "compute", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "line",
      "label": "Line",
      "fields": [
        {"name": "title", "label": "Remedy", "type": "text", "required": true},
        {"name": "bottles", "label": "Bottles", "type": "number"},
        {"name": "rate", "label": "Rate", "type": "number"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "compute": {"inputs": ["bottles", "rate"], "formula": "bottles * rate",
              "output": {"label": "Cost"}},
  "storage": {"kind": "localstorage", "namespace": "remedy-cost"},
  "accent": "#38bdf8",
  "done_means": [
    "two rows of 3 x 4 and 5 x 6 show 12 and 30, and 42 as the total",
    "the formula is shown next to its result on every row",
    "changing a rate shows a new cost on the next render",
    "a row with an empty input shows a cost of zero, not an error"
  ],
  "not": ["network calls", "accounts", "sync", "row-to-row references", "conditionals"]
}
```

## Pitch

Bottles, strength and rate, and the cost of each line worked out for you.

## The job

- Record what was ordered and at what rate
- See the cost per line without a calculator
- See the total
- Change a rate and see the cost change
- Take the sheet out as a file

## The mechanic

The formula is written once in the spec and evaluated over each row's own fields, using the
same recursive-descent parser as the calculator: no `eval`, no second dialect.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No row-to-row references, no lookups, no conditionals
- No units checking

## What it does when things go wrong

- **bad input** — a line without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the line stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:remedy-cost:corrupt`, the sheet resets

## Done means

- Two rows of 3 × 4 and 5 × 6 show 12 and 30, and 42 as the total
- The formula is shown next to its result on every row
- Changing a rate shows a new cost on the next render
- A row with an empty input is computed as zero, not as an error

## The data

Stored in `localStorage` under `kiln:remedy-cost`. The inputs are plain numbers and the formula
is text; nothing is stored that could have been computed.
