# New Patient

```json kiln
{
  "id": "app-new-patient",
  "name": "New Patient",
  "tier": 2,
  "category": "clinical",
  "pattern": "wizard",
  "pitch": "The intake form, in three short steps instead of one long one.",
  "features": ["crud", "steps", "search", "sort", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "patient",
      "label": "Patient",
      "fields": [
        {"name": "title", "label": "Name", "type": "text", "required": true},
        {"name": "date", "label": "Date of birth", "type": "date"},
        {"name": "phone", "label": "Phone", "type": "text"},
        {"name": "category", "label": "Complaint", "type": "select", "options": ["acute", "chronic", "follow-up"]},
        {"name": "body", "label": "History", "type": "longtext"},
        {"name": "done", "label": "Intake complete", "type": "bool"}
      ]
    }
  ],
  "wizard": {
    "steps": [
      {"title": "Who", "fields": ["title", "date", "phone"]},
      {"title": "Why", "fields": ["category", "body"]},
      {"title": "Done", "fields": ["done"]}
    ]
  },
  "storage": {"kind": "localstorage", "namespace": "new-patient"},
  "accent": "#4ade80",
  "done_means": [
    "the first step shows Back hidden and Next shown",
    "leaving the name blank refuses to advance and names the field",
    "the last step shows Save instead of Next",
    "a saved patient appears in the list after the third step"
  ],
  "not": ["network calls", "accounts", "sync", "clinical advice", "prescriptions"]
}
```

## Pitch

The intake form, in three short steps instead of one long one.

## The job

- Take a name, a date of birth and a phone number
- Then the complaint and the history
- Then mark the intake complete
- Find a patient later by typing

## The mechanic

The same fields, split into steps in the spec. Each step validates only its own fields, so
the error is always next to the field that caused it, and the draft survives stepping back.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No clinical advice, no prescription output
- No conditional steps: every step is always shown

## What it does when things go wrong

- **bad input** — a blank required field refuses to advance and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the patient stays in memory, a banner says it will not survive a reload, export is offered
- **corrupt state** — the raw value is copied to `kiln:new-patient:corrupt`, the list resets, a banner says where it went

## Done means

- The first step shows Back hidden and Next shown
- Leaving the name blank refuses to advance and names the field
- The last step shows Save instead of Next
- A saved patient appears in the list after the third step

## The data

Stored in `localStorage` under `kiln:new-patient`. A name is the only identifier kept. Nothing
leaves the device unless the user exports it.
