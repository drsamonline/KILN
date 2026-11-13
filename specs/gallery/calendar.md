# Appointment Book

```json kiln
{
  "id": "app-appointment-book",
  "name": "Appointment Book",
  "tier": 2,
  "category": "clinical",
  "pattern": "calendar",
  "pitch": "The month at a glance, one cell per day, and who is coming in.",
  "features": ["crud", "calendar", "search", "sort", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "appointment",
      "label": "Appointment",
      "fields": [
        {"name": "title", "label": "Patient", "type": "text", "required": true},
        {"name": "date", "label": "Day", "type": "date", "required": true},
        {"name": "body", "label": "Reason", "type": "longtext"}
      ]
    }
  ],
  "calendar": {"field": "date"},
  "storage": {"kind": "localstorage", "namespace": "appointment-book"},
  "accent": "#4ade80",
  "done_means": [
    "an appointment dated the 13th shows in the cell for the 13th",
    "the next month button shows a different set of days",
    "a day with three appointments shows two names and +1 more",
    "clicking an empty day opens the form with that date filled in"
  ],
  "not": ["network calls", "accounts", "sync", "times of day", "recurring entries"]
}
```

## Pitch

The month at a glance, one cell per day, and who is coming in.

## The job

- See the month as a grid
- Spot the empty days and the crowded ones
- Click a day to book someone in
- Find a patient by typing
- Take the month out as a file

## The mechanic

One date field, one cell. The grid is six rows of seven days, Monday first, computed in UTC
from the month you are looking at, so the same data draws the same grid on any machine.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No times of day: one date field, one cell
- No recurring entries, no spans across days

## What it does when things go wrong

- **bad input** — an appointment without a day refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the appointment stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:appointment-book:corrupt`, the book resets, a banner says where it went

## Done means

- An appointment dated the 13th shows in the cell for the 13th
- The next month button shows a different set of days
- A day with three appointments shows two names and +1 more
- Clicking an empty day opens the form with that date filled in

## The data

Stored in `localStorage` under `kiln:appointment-book`. A day is a `YYYY-MM-DD` string, so
grouping is a string comparison and cannot drift across a timezone.
