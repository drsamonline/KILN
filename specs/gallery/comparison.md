# Remedy Comparison

```json kiln
{
  "id": "app-remedy-comparison",
  "name": "Remedy Comparison",
  "tier": 2,
  "category": "reference",
  "pattern": "comparison",
  "pitch": "Four remedies side by side, with the strongest potency marked.",
  "features": ["crud", "comparison", "search", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "option",
      "label": "Option",
      "fields": [
        {"name": "title", "label": "Remedy", "type": "text", "required": true},
        {"name": "potency", "label": "Potency", "type": "select",
         "options": ["6C", "30C", "200C", "1M"]},
        {"name": "price", "label": "Price", "type": "currency_cents"},
        {"name": "rating", "label": "Rating", "type": "number"},
        {"name": "stock", "label": "In stock", "type": "bool"}
      ]
    }
  ],
  "comparison": {
    "columns": ["potency", "price", "rating", "stock"],
    "highlight": {"price": "min", "rating": "max"}
  },
  "storage": {"kind": "localstorage", "namespace": "remedy-comparison"},
  "accent": "#38bdf8",
  "done_means": [
    "the cheapest remedy shows a mark and no other price does",
    "the highest rating shows a mark in its column",
    "the table shows one row per remedy and one column per chosen field",
    "searching for a word no remedy contains hides every row"
  ],
  "not": ["network calls", "accounts", "sync", "a verdict", "clinical advice"]
}
```

## Pitch

Four remedies side by side, with the strongest potency marked.

## The job

- Put a shortlist side by side
- Compare price, rating and stock without scrolling a list
- See which is cheapest and which is best rated
- Narrow the shortlist by typing
- Take the table out as a file

## The mechanic

The columns are chosen in the spec, so the table stays readable. Each numeric column marks
its best value — `min` for a price, `max` for a rating — and nothing else is marked.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No verdict: the app marks the extremes, it does not choose
- No clinical advice

## What it does when things go wrong

- **bad input** — an option without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the change stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:remedy-comparison:corrupt`, the table resets

## Done means

- The cheapest remedy is marked and no other price is
- The highest rating is marked in its column
- The table shows one row per remedy and one column per chosen field
- Searching for a word no remedy contains leaves the table empty

## The data

Stored in `localStorage` under `kiln:remedy-comparison`. Prices are integer cents, formatted
when drawn. Nothing leaves the device unless the user exports it.
