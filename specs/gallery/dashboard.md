# Clinic Desk

```json kiln
{
  "id": "app-clinic-desk",
  "name": "Clinic Desk",
  "tier": 2,
  "category": "clinical",
  "pattern": "dashboard",
  "pitch": "Patients and visits in one file, with the week's numbers on top.",
  "features": ["crud", "multi", "dashboard", "search", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "patient",
      "label": "Patient",
      "fields": [
        {"name": "title", "label": "Name", "type": "text", "required": true},
        {"name": "phone", "label": "Phone", "type": "text"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    },
    {
      "name": "visit",
      "label": "Visit",
      "fields": [
        {"name": "title", "label": "Patient", "type": "text", "required": true},
        {"name": "date", "label": "Day", "type": "date"},
        {"name": "minutes", "label": "Length", "type": "duration"},
        {"name": "category", "label": "Kind", "type": "select",
         "options": ["first", "follow-up", "acute"]}
      ]
    }
  ],
  "dashboard": {
    "cards": [
      {"label": "patients", "entity": "patient", "metric": "count"},
      {"label": "visits", "entity": "visit", "metric": "count"},
      {"label": "time in clinic", "entity": "visit", "metric": "sum",
       "field": "minutes", "format": "duration"},
      {"label": "average visit", "entity": "visit", "metric": "avg",
       "field": "minutes", "format": "duration"}
    ]
  },
  "storage": {"kind": "localstorage", "namespace": "clinic-desk"},
  "accent": "#4ade80",
  "done_means": [
    "two patients and three visits show 2 and 3 on two cards",
    "the time card shows the sum of the visit lengths",
    "switching to visits shows the visits, and switching back shows the patients",
    "adding a patient shows one more on the patient card and the same number on the visit card"
  ],
  "not": ["network calls", "accounts", "sync", "a link between a visit and a patient", "clinical advice"]
}
```

## Pitch

Patients and visits in one file, with the week's numbers on top.

## The job

- Keep a list of patients
- Keep a list of visits, separately
- See how many of each, and how long the visits ran
- Switch between the two lists without losing your place
- Take both lists out as one file

## The mechanic

Two lists, one storage key. The cards are computed over the whole of each list every time the
page is drawn, so they cannot go stale. The switcher changes which list is being edited; the
numbers do not change when you switch.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No link between a visit and a patient: the lists are independent
- No clinical advice

## What it does when things go wrong

- **bad input** — a record without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the change stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:clinic-desk:corrupt`, both lists reset, a banner says where it went

## Done means

- Two patients and three visits show 2 and 3 on two cards
- The visit lengths add up to the time card
- Switching to visits shows the visits, and switching back shows the patients
- Adding a patient changes the patient card and leaves the visit card alone

## The data

Stored in `localStorage` under `kiln:clinic-desk` as one object of two lists. Nothing leaves
the device unless the user exports it, and the export contains both lists.
