# Patient Book

```json kiln
{
  "id": "app-patient-book",
  "name": "Patient Book",
  "tier": 3,
  "category": "clinical",
  "pattern": "master-detail",
  "pitch": "Each patient, and every visit that belongs to them, in one place.",
  "features": ["crud", "multi", "relation", "detail", "search", "export", "theme", "a11y"],
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
        {"name": "title", "label": "Reason", "type": "text", "required": true},
        {"name": "patient", "label": "Patient", "type": "lookup", "entity": "patient"},
        {"name": "date", "label": "Day", "type": "date"},
        {"name": "body", "label": "Notes", "type": "longtext"}
      ]
    }
  ],
  "master_detail": {"master": "patient", "child": "visit", "field": "patient"},
  "detail": {"field": "body"},
  "storage": {"kind": "localstorage", "namespace": "patient-book"},
  "accent": "#4ade80",
  "done_means": [
    "the visit form shows a patient select, not a text box",
    "opening a patient lists that patient's visits and no one else's",
    "a visit pointing at a patient shows the patient's name on the row",
    "switching to visits shows every visit with its patient named"
  ],
  "not": ["network calls", "accounts", "sync", "nested children", "clinical advice"]
}
```

## Pitch

Each patient, and every visit that belongs to them, in one place.

## The job

- Keep a list of patients
- Record a visit against a patient
- Open a patient and see every visit that belongs to them
- Find a patient by typing
- Take both lists out as one file

## The mechanic

The visit carries a pointer, not a copy. The id is stored, the name is shown, so renaming a
patient does not rewrite the visits. The parent's read view lists its children.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No nesting deeper than one level
- No cascade on delete: a deleted patient leaves its visits pointing at nothing

## What it does when things go wrong

- **bad input** — a visit without a reason refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the change stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:patient-book:corrupt`, both lists reset

## Done means

- The visit form shows a patient select, not a text box
- Opening a patient lists that patient's visits and no one else's
- A visit pointing at a patient shows the patient's name on the row
- Switching to visits shows every visit with its patient named

## The data

Stored in `localStorage` under `kiln:patient-book` as one object of two lists. A visit stores
the patient's id in its `patient` field. Nothing leaves the device unless the user exports it.
