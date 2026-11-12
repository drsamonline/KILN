Sure! Here is the specification you asked for. Let me know if you want changes.

```json
{
  "name": "Tea Log",
  "tier": "1",
  "category": "Food & Drink",
  "pitch": "Track teas you have tried, how long you steeped them, and whether you would buy again.",
  "features": ["create/edit/delete", "dark mode", "csv export", "filters", "tags", "telepathy"],
  "entities": {
    "name": "Tea",
    "fields": {
      "Name": "string",
      "Notes": "textarea",
      "Steep time": "integer",
      "Tried on": "datetime",
      "Would rebuy": "checkbox",
      "Strength": {"type": "enum", "choices": ["light", "medium", "strong"]}
    }
  },
  "accent": "#C08B5C",
  "done_means": ["it works as expected", "looks good"],
  "not": [],
}
```

## Pitch
Track teas.

## The job
- log a tea

I hope this helps!
