# Two Remedies, Side by Side

```json kiln
{
  "id": "app-two-remedies",
  "name": "Two Remedies, Side by Side",
  "tier": 2,
  "category": "reference",
  "pattern": "comparison-of-records",
  "pitch": "Pick two remedies and see every difference on one screen.",
  "features": ["crud", "versus", "search", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "remedy",
      "label": "Remedy",
      "fields": [
        {"name": "title", "label": "Remedy", "type": "text", "required": true},
        {"name": "potency", "label": "Potency", "type": "select",
         "options": ["6C", "30C", "200C", "1M"]},
        {"name": "price", "label": "Price", "type": "currency_cents"},
        {"name": "rating", "label": "Rating", "type": "number"},
        {"name": "body", "label": "Keynote", "type": "longtext"}
      ]
    }
  ],
  "versus": {"fields": ["potency", "price", "rating"],
             "better": {"price": "lower", "rating": "higher"}},
  "currency": "₹",
  "storage": {"kind": "localstorage", "namespace": "two-remedies"},
  "accent": "#a78bfa",
  "done_means": [
    "two remedies differing on a price show which is cheaper",
    "a field where both agree shows dimmed, and only the cheaper price is marked",
    "the two pickers show any two records side by side",
    "a list with only one record shows a note that two are needed"
  ],
  "not": ["network calls", "accounts", "sync", "scoring", "a verdict"]
}
```

## Pitch

Pick two remedies and see every difference on one screen.

## The job

- Keep a shortlist of remedies
- Pick any two and compare them field by field
- See which is cheaper and which is rated higher
- See at a glance where they are the same
- Take the list out as a file

## The mechanic

Two pickers choose the records; the fields named in the spec are laid side by side. A field
where both agree is dimmed; where two numbers differ, the lower is marked.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No scoring, no weighting, no verdict
- No three-way comparison

## What it does when things go wrong

- **bad input** — a remedy without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the remedy stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:two-remedies:corrupt`, the list resets

## Done means

- Two remedies differing on a price show which is cheaper
- A field where both agree is dimmed rather than marked
- The two pickers let any two records be compared
- A list with only one record says two are needed

## The data

Stored in `localStorage` under `kiln:two-remedies`. The comparison reads the records; it never
writes to them.
