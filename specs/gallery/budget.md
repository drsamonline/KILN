# Clinic Budget

```json kiln
{
  "id": "app-clinic-budget",
  "name": "Clinic Budget",
  "tier": 2,
  "category": "clinical",
  "pattern": "budget",
  "pitch": "Eight envelopes, what you planned, what you spent, and what is left.",
  "features": ["crud", "variance", "search", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "envelope",
      "label": "Envelope",
      "fields": [
        {"name": "title", "label": "Envelope", "type": "text", "required": true},
        {"name": "planned", "label": "Planned", "type": "currency_cents"},
        {"name": "actual", "label": "Spent", "type": "currency_cents"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "variance": {"planned": "planned", "actual": "actual"},
  "currency": "₹",
  "storage": {"kind": "localstorage", "namespace": "clinic-budget"},
  "accent": "#4ade80",
  "done_means": [
    "planned 5000 and actual 3500 show 1500 left and a bar two thirds full",
    "an envelope that overspends is shown in the warning colour and counted in the strip",
    "the strip shows what is left across every envelope",
    "searching for a word no envelope contains hides every row"
  ],
  "not": ["network calls", "accounts", "sync", "transactions", "rollover between months"]
}
```

## Pitch

Eight envelopes, what you planned, what you spent, and what is left.

## The job

- Set a planned amount per envelope
- Record what was actually spent
- See what is left, without arithmetic
- See which envelopes overspent
- Take the month out as a file

## The mechanic

Two integer-cent amounts per row. Remaining and percent spent are derived on every render, so
they cannot drift from the two numbers that produced them.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No transactions, no ledger, no rollover
- No advice on money

## What it does when things go wrong

- **bad input** — an envelope without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the envelope stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:clinic-budget:corrupt`, the budget resets

## Done means

- Planned 5000 and actual 3500 show 1500 left and a bar two thirds full
- An envelope that overspends is shown in the warning colour and counted in the strip
- The strip shows what is left across every envelope
- Searching for a word no envelope contains hides every row

## The data

Stored in `localStorage` under `kiln:clinic-budget`. Amounts are integer cents, formatted on
draw, so a total is exact.
