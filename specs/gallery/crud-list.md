# Clinic Stock

```json kiln
{
  "id": "app-clinic-stock",
  "name": "Clinic Stock",
  "tier": 1,
  "category": "clinical",
  "pattern": "crud-list",
  "pitch": "What is on the shelf, what it cost, and what to reorder before Thursday.",
  "features": ["crud", "search", "sort", "stats", "export", "theme",
               "i18n", "a11y", "feedback"],
  "entities": [
    {
      "name": "item",
      "label": "Item",
      "fields": [
        {"name": "title", "label": "Remedy", "type": "text", "required": true},
        {"name": "potency", "label": "Potency", "type": "select", "options": ["6C", "30C", "200C", "1M"]},
        {"name": "amount", "label": "Unit price", "type": "currency_cents"},
        {"name": "qty", "label": "On hand", "type": "number"},
        {"name": "created", "label": "Added", "type": "date"}
      ]
    }
  ],
  "i18n": {"languages": ["en", "hi", "gu"]},
  "storage": {"kind": "localstorage", "namespace": "clinic-stock"},
  "currency": "₹",
  "accent": "#4ade80",
  "done_means": [
    "saving an item and reloading the page shows the item in the list",
    "entering 12.50 as a price stores 1250 and shows ₹12.50",
    "typing a remedy no item contains hides every row",
    "exporting writes one row per item, with the price as a decimal",
    "switching language shows at least one label in the other language",
    "pressing Tab from the top shows a skip link before the header buttons"
  ],
  "not": ["network calls", "accounts", "prescriptions", "patient data"]
}
```

## Pitch

What is on the shelf, what it cost, and what to reorder before Thursday.

## The job

- Add a remedy with its potency, unit price and quantity
- Find one by typing part of its name
- Sort by price or by quantity
- See how many lines the shelf holds
- Take the list to the wholesaler as a file

## The mechanic

One item, one row, one price in paise. The list, the form, the sort and the export
read the same field declaration, so the price can never be shown as a float sum of
floats — it is an integer count of paise, formatted only when it is drawn.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No patient data, ever
- No prescription output

## What it does when things go wrong

- **bad input** — a remedy without a name refuses to save and the form names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the item stays in memory, a banner says it will not survive a reload, export is offered
- **corrupt state** — the raw value is copied to `kiln:clinic-stock:corrupt`, the list resets, a banner says where it went

## Done means

- Saving an item and reloading the page shows the item in the list
- Entering 12.50 as a price stores 1250 and shows ₹12.50
- Typing a remedy no item contains hides every row
- Exporting writes one row per item, with the price as a decimal

## The data

Stored in `localStorage` under `kiln:clinic-stock`. Money is stored as integer paise.
Nothing leaves the device unless the user exports it.
