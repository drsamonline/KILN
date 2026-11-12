# Field Survey

```json kiln
{
  "id": "app-field-survey",
  "name": "Field Survey",
  "tier": 2,
  "category": "community",
  "pitch": "Collect answers in a village with no signal, then hand over one file.",
  "features": ["crud", "search", "tags", "filters", "stats", "export", "import", "backup", "theme"],
  "entities": [
    {
      "name": "response",
      "label": "Response",
      "fields": [
        {"name": "title", "label": "Household", "type": "text", "required": true},
        {"name": "date", "label": "Collected on", "type": "date"},
        {"name": "tags", "label": "Tags", "type": "tags"},
        {"name": "priority", "label": "Follow-up", "type": "select", "options": ["none", "soon", "urgent"]},
        {"name": "body", "label": "Answers", "type": "longtext"}
      ]
    }
  ],
  "storage": {"kind": "localstorage", "namespace": "field-survey"},
  "accent": "#f59e0b",
  "done_means": [
    "saving a response with the device offline and reloading shows the response",
    "tagging a response with two tags shows two chips on the row",
    "a backup file restored into an empty store reproduces every response",
    "selecting the urgent follow-up filter shows only urgent responses"
  ],
  "not": ["network calls", "accounts", "location tracking", "photographs"]
}
```

## Pitch

Answers collected where there is no signal, handed over later as one file.

## The job

- Record a household response
- Tag it by whatever the enumerator needs
- Mark a follow-up level
- See how many are collected
- Hand the whole set to the office as one file
- Restore a file if the device is replaced

## The mechanic

The record is the unit. Tags and follow-up levels are declared once, so the
filter, the chips and the export agree without being wired separately.

## What it must NOT do

- No network request, ever
- No location capture
- No photographs
- No accounts

## What it does when things go wrong

- **bad input** — a response without a household refuses to save and names the field
- **no network** — the app says so in one line and keeps working, which is the normal case
- **storage full** — the response stays in memory, a banner says so, a backup is offered
- **corrupt state** — the raw value is copied to `kiln:field-survey:corrupt:<timestamp>`, the store resets, the banner says where it went

## Done means

- Saving a response with the device offline and reloading shows the response
- Tagging a response with two tags shows two chips on the row
- A backup file restored into an empty store reproduces every response
- Selecting the urgent follow-up filter shows only urgent responses

## The data

Stored in `localStorage` under `kiln:field-survey`. Nothing leaves the device
except the file the enumerator hands over.
