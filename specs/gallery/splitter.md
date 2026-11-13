# Dinner Bill

```json kiln
{
  "id": "app-dinner-bill",
  "name": "Dinner Bill",
  "tier": 1,
  "category": "personal",
  "pattern": "splitter",
  "pitch": "One bill, four people, and nobody argues about the last rupee.",
  "features": ["crud", "split", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "share",
      "label": "Person",
      "fields": [
        {"name": "title", "label": "Person", "type": "text", "required": true},
        {"name": "weight", "label": "Weight", "type": "number"},
        {"name": "body", "label": "What they had", "type": "longtext"}
      ]
    }
  ],
  "split": {"weight": "weight", "total": 10000},
  "currency": "₹",
  "storage": {"kind": "localstorage", "namespace": "dinner-bill"},
  "accent": "#f59e0b",
  "done_means": [
    "an amount of 100 split by 1, 1 and 1 shows 34, 33 and 33",
    "the strip shows the shares adding up to the whole amount exactly",
    "a person with a weight of zero shows a share of zero",
    "changing one weight shows a new share on every row on the next render"
  ],
  "not": ["network calls", "accounts", "sync", "tax", "rounding to whole rupees"]
}
```

## Pitch

One bill, four people, and nobody argues about the last rupee.

## The job

- List who was there and how much they had
- Give each a weight: one unit, two units, or their share
- See what each owes
- See that the parts add up to the bill
- Take it out as a file

## The mechanic

Largest-remainder apportionment. Every share is floored, and the units left over go to the
largest fractional parts, in order. The parts therefore always add up to the whole, exactly.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No tax, no tip, no adjustment lines
- No rounding to whole rupees

## What it does when things go wrong

- **bad input** — a person without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the person stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:dinner-bill:corrupt`, the split resets

## Done means

- An amount of 100 split by 1, 1 and 1 shows 34, 33 and 33
- The shares in the strip add up to the whole amount exactly
- A person with a weight of zero shows a share of zero
- Changing one weight re-splits every row on the next render

## The data

Stored in `localStorage` under `kiln:dinner-bill`. The total is one number in the spec; the
weights are numbers on the rows.
