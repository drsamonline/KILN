# Distance

```json kiln
{
  "id": "app-distance",
  "name": "Distance",
  "tier": 1,
  "category": "utility",
  "pattern": "converter",
  "pitch": "Kilometres to miles, metres to feet, without opening a browser tab.",
  "features": ["convert", "theme", "a11y"],
  "entities": [
    {
      "name": "conversion",
      "label": "Conversion",
      "fields": [
        {"name": "title", "label": "Note", "type": "text"}
      ]
    }
  ],
  "converter": {
    "label": "Distance",
    "units": [
      {"id": "mm", "label": "Millimetres", "short": "mm", "factor": 0.001},
      {"id": "cm", "label": "Centimetres", "short": "cm", "factor": 0.01},
      {"id": "m", "label": "Metres", "short": "m", "factor": 1},
      {"id": "km", "label": "Kilometres", "short": "km", "factor": 1000},
      {"id": "in", "label": "Inches", "short": "in", "factor": 0.0254},
      {"id": "ft", "label": "Feet", "short": "ft", "factor": 0.3048},
      {"id": "mi", "label": "Miles", "short": "mi", "factor": 1609.344}
    ],
    "default_amount": 1,
    "default_from": "km",
    "default_to": "mi",
    "decimals": 3,
    "note": "Factors are exact to the definition, not rounded. A mile is 1609.344 metres."
  },
  "storage": {"kind": "localstorage", "namespace": "distance"},
  "accent": "#38bdf8",
  "done_means": [
    "1 kilometre shows 0.621 miles",
    "switching the target to feet shows 3280.840",
    "a mile shows 1.609 kilometres in the other direction",
    "clearing the amount shows a message instead of a number"
  ],
  "not": ["network calls", "accounts", "history", "temperature, which needs an offset"]
}
```

## Pitch

Kilometres to miles, metres to feet, without opening a browser tab.

## The job

- Type an amount
- Pick the unit it is in
- Pick the unit to show
- Read the answer

## The mechanic

One base unit and a factor per unit. The conversion is `amount × factor_from ÷ factor_to`,
evaluated when the input changes. The factors are data in the spec, so a wrong factor is a
wrong spec, not a wrong program.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No history: a conversion is not a record
- No temperature: that needs an offset, and this pattern does not do offsets

## What it does when things go wrong

- **bad input** — a blank or non-numeric amount shows a message instead of a number
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — nothing is stored, so nothing can fail to store
- **corrupt state** — there is no saved state; the app opens at its defaults

## Done means

- 1 kilometre shows 0.621 miles
- Switching the target to feet shows 3280.840
- A mile converts back to 1.609 kilometres
- Clearing the amount shows a message instead of a number

## The data

Nothing is stored except the theme preference. There is no list to export.
