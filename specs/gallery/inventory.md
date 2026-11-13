# Store Room

```json kiln
{
  "id": "app-store-room",
  "name": "Store Room",
  "tier": 3,
  "category": "clinical",
  "pattern": "inventory",
  "pitch": "What is on the shelf, what came in, what went out, and what to reorder.",
  "features": ["crud", "multi", "relation", "detail", "balance", "search", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "item",
      "label": "Item",
      "fields": [
        {"name": "title", "label": "Item", "type": "text", "required": true},
        {"name": "unit", "label": "Unit", "type": "select", "options": ["bottle", "box", "strip"]},
        {"name": "reorder", "label": "Reorder at", "type": "number"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    },
    {
      "name": "movement",
      "label": "Movement",
      "fields": [
        {"name": "title", "label": "What", "type": "text", "required": true},
        {"name": "item", "label": "Item", "type": "lookup", "entity": "item"},
        {"name": "qty", "label": "Quantity", "type": "number"},
        {"name": "date", "label": "Day", "type": "date"}
      ]
    }
  ],
  "master_detail": {"master": "item", "child": "movement", "field": "item"},
  "balance": {"master": "item", "child": "movement", "field": "qty",
              "lookup": "item", "reorder": "reorder", "unit": ""},
  "detail": {"field": "body"},
  "storage": {"kind": "localstorage", "namespace": "store-room"},
  "accent": "#f59e0b",
  "done_means": [
    "three movements of 10, -3 and -2 show a balance of 5 on the item",
    "an item at or below its reorder level shows a reorder count in the strip",
    "opening an item lists the movements that produced the balance",
    "switching to movements shows every movement with its item named"
  ],
  "not": ["network calls", "accounts", "sync", "valuation", "lot numbers", "expiry dates"]
}
```

## Pitch

What is on the shelf, what came in, what went out, and what to reorder.

## The job

- Keep a list of items and a reorder level for each
- Record a movement: positive for a receipt, negative for an issue
- See the balance on the item, computed from its movements
- See how many items are at or below their reorder level
- Take both lists out as one file

## The mechanic

The balance is never stored. It is the signed sum of the movements that point at the item, so
it cannot disagree with the history that produced it.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No valuation, no lot numbers, no expiry dates
- No audit trail: deleting a movement changes history

## What it does when things go wrong

- **bad input** — a movement without a quantity refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the movement stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:store-room:corrupt`, both lists reset

## Done means

- Three movements of 10, -3 and -2 show a balance of 5 on the item
- An item at or below its reorder level shows a reorder count in the strip
- Opening an item lists the movements that produced the balance
- Switching to movements shows every movement with its item named

## The data

Stored in `localStorage` under `kiln:store-room` as one object of two lists. A movement stores
the item's id and a signed quantity. Nothing leaves the device unless the user exports it.
