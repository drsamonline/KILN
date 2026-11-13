# Clinic Account

```json kiln
{
  "id": "app-clinic-account",
  "name": "Clinic Account",
  "tier": 2,
  "category": "clinical",
  "pattern": "register",
  "pitch": "Money in and money out, and the balance after every entry.",
  "features": ["crud", "running", "print", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "entry",
      "label": "Entry",
      "fields": [
        {"name": "title", "label": "Entry", "type": "text", "required": true},
        {"name": "date", "label": "Day", "type": "date", "required": true},
        {"name": "amount", "label": "Amount", "type": "currency_cents"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "running": {"field": "amount", "date": "date"},
  "currency": "₹",
  "storage": {"kind": "localstorage", "namespace": "clinic-account"},
  "accent": "#4ade80",
  "done_means": [
    "three entries of 500, -200 and -100 show 500, 300 and 200 as balances",
    "the strip shows the closing balance",
    "the entries are shown in date order, not the order they were typed",
    "an entry with no amount shows the same balance as the row before it"
  ],
  "not": ["network calls", "accounts", "sync", "reconciliation", "categories"]
}
```

## Pitch

Money in and money out, and the balance after every entry.

## The job

- Record each receipt and payment with a date
- See the balance after every entry
- See the closing balance
- Print it like a statement
- Take the register out as a file

## The mechanic

Entries are ordered by date, then by id, and the balance is the running sum of a signed amount.
Nothing is stored but the entries, so the balance cannot drift from them.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No reconciliation, no categories, no opening balance
- No currency conversion

## What it does when things go wrong

- **bad input** — an entry without a date refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the entry stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:clinic-account:corrupt`, the register resets

## Done means

- Three entries of 500, −200 and −100 show 500, 300 and 200 as balances
- The strip shows the closing balance
- The entries are shown in date order, not the order they were typed
- An entry with no amount leaves the balance where it was

## The data

Stored in `localStorage` under `kiln:clinic-account`. Amounts are integer cents and may be
negative, so a payment and a receipt are the same kind of record.
