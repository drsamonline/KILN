# Practice Log

```json kiln
{
  "id": "app-practice-log",
  "name": "Practice Log",
  "tier": 1,
  "category": "education",
  "pattern": "log",
  "pitch": "How long each practice ran, and how much it adds up to.",
  "features": ["crud", "search", "sort", "stats", "totals", "export", "theme"],
  "entities": [
    {
      "name": "session",
      "label": "Session",
      "fields": [
        {"name": "title", "label": "What", "type": "text", "required": true},
        {"name": "date", "label": "Day", "type": "date"},
        {"name": "minutes", "label": "Length", "type": "duration"},
        {"name": "body", "label": "Notes", "type": "longtext"}
      ]
    }
  ],
  "totals": {"field": "minutes", "format": "duration", "label": "practised"},
  "storage": {"kind": "localstorage", "namespace": "practice-log"},
  "accent": "#f59e0b",
  "done_means": [
    "entering 90 minutes shows 1h 30m on the row",
    "two sessions of 30 and 90 minutes show a total of 2h",
    "sorting by length puts the longest session first",
    "exporting writes the length in minutes, not as 1h 30m"
  ],
  "not": ["network calls", "accounts", "sync", "a stopwatch", "charts"]
}
```

## Pitch

How long each practice ran, and how much it adds up to.

## The job

- Log a session with a length in minutes
- Read the length as hours and minutes
- See the running total of everything logged
- Sort by length or by date
- Take the log out as a file that opens in a spreadsheet

## The mechanic

Minutes are stored as whole numbers and formatted only when drawn. The total is the sum of
one field over every row, recomputed when the page is drawn — never stored.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No stopwatch: you type the minutes
- No charts: that is the tracker archetype

## What it does when things go wrong

- **bad input** — a negative or non-numeric length refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the session stays in memory, a banner says it will not survive a reload, export is offered
- **corrupt state** — the raw value is copied to `kiln:practice-log:corrupt`, the log resets, a banner says where it went

## Done means

- Entering 90 minutes shows 1h 30m on the row
- Two sessions of 30 and 90 minutes show a total of 2h
- Sorting by length puts the longest session first
- Exporting writes the length in minutes, not as 1h 30m

## The data

Stored in `localStorage` under `kiln:practice-log`. Durations are stored as whole minutes.
Nothing leaves the device unless the user exports it.
