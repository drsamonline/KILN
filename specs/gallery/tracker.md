# Water Log

```json kiln
{
  "id": "app-water-log",
  "name": "Water Log",
  "tier": 1,
  "category": "health",
  "pattern": "tracker",
  "pitch": "How much water, how many days in a row, and whether this week beat the goal.",
  "features": ["crud", "search", "sort", "stats", "derived", "chart", "theme"],
  "entities": [
    {
      "name": "entry",
      "label": "Entry",
      "fields": [
        {"name": "date", "label": "Day", "type": "date", "required": true},
        {"name": "litres", "label": "Litres", "type": "number", "required": true},
        {"name": "note", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "tracker": {"field": "litres", "goal": 2.5, "window": 7, "unit": "L"},
  "storage": {"kind": "localstorage", "namespace": "water-log"},
  "accent": "#38bdf8",
  "done_means": [
    "logging today and reloading shows a streak of 1 day",
    "three days logged in a row show a streak of 3 days",
    "two entries of 1 and 3 litres show an average of 2",
    "the sparkline draws one bar for every day in the window",
    "a full week at the goal shows a goal of 100%"
  ],
  "not": ["network calls", "accounts", "sync", "medical advice"]
}
```

## Pitch

How much water, how many days in a row, and whether this week beat the goal.

## The job

- Log a day's water in one number
- See how many days in a row have been logged
- See the average per logged day
- See the week against a goal set once
- Find an old day by typing
- Take the log to a doctor's appointment as a file

## The mechanic

One number per day, and the arithmetic done at view time. The streak counts backwards
from today; the average divides the sum by the days that were actually logged, not by
the days in the window; the goal is the week's total against goal × window. Nothing is
stored except what the user typed.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No medical advice, no targets it invented
- No reminders it cannot deliver

## What it does when things go wrong

- **bad input** — a day without a number refuses to save and the form names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the entry stays in memory, a banner says it will not survive a reload, export is offered
- **corrupt state** — the raw value is copied to `kiln:water-log:corrupt`, the log resets, a banner says where it went

## Done means

- Logging today and reloading shows a streak of 1 day
- Three days logged in a row show a streak of 3 days
- Two entries of 1 and 3 litres show an average of 2
- The sparkline draws one bar for every day in the window
- A full week at the goal shows a goal of 100%

## The data

Stored in `localStorage` under `kiln:water-log`. The streak, the average, the goal
percentage and the sparkline are computed when the page is drawn; none of them is stored.
Nothing leaves the device unless the user exports it.
