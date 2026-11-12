# Clinic Log

```json kiln
{
  "id": "app-clinic-log",
  "name": "Clinic Log",
  "tier": 2,
  "category": "clinical",
  "pitch": "A visit log for a small clinic that never leaves the desk.",
  "features": ["crud", "search", "filters", "sort", "stats", "export", "import", "print", "theme"],
  "entities": [
    {
      "name": "visit",
      "label": "Visit",
      "fields": [
        {"name": "title", "label": "Patient", "type": "text", "required": true},
        {"name": "date", "label": "Visit date", "type": "date"},
        {"name": "category", "label": "Complaint", "type": "select", "options": ["acute", "chronic", "follow-up", "review"]},
        {"name": "body", "label": "Notes", "type": "longtext"},
        {"name": "amount", "label": "Fee", "type": "number"},
        {"name": "done", "label": "Closed", "type": "bool"}
      ]
    }
  ],
  "storage": {"kind": "localstorage", "namespace": "clinic-log"},
  "accent": "#4ade80",
  "done_means": [
    "saving a visit and reloading the page shows the visit in the list",
    "filtering by the acute complaint shows only visits carrying that complaint",
    "the summary strip count equals the number of rows rendered",
    "printing hides the controls and keeps the list"
  ],
  "not": ["network calls", "cloud backup", "patient identifiers beyond a name", "prescriptions"]
}
```

## Pitch

A visit log for one desk, one doctor, one machine. No cloud, no account.

## The job

- Record a visit against a patient name and date
- Mark what kind of complaint it was
- Find a past visit by any word
- Narrow to one complaint type
- Print the day's list
- Take the whole log out as a file

## The mechanic

One visit, one row. The complaint list lives in the field declaration, so the
filter, the form and the summary strip cannot disagree about what a complaint is.

## What it must NOT do

- No network request
- No cloud backup
- No clinical decision support
- No prescription generation

## What it does when things go wrong

- **bad input** — a visit without a patient name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the visit stays in memory, a banner warns it will be lost, export is offered
- **corrupt state** — the raw value is copied to `kiln:clinic-log:corrupt:<timestamp>`, the log resets, the banner says where the old data went

## Done means

- Saving a visit and reloading the page shows the visit in the list
- Filtering by the acute complaint shows only visits carrying that complaint
- The summary strip count equals the number of rows rendered
- Printing hides the controls and keeps the list

## The data

Stored in `localStorage` under `kiln:clinic-log`. A patient name is the only
identifier kept. Nothing leaves the device except an export the user makes.
