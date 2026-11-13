# Clinic Maintenance

```json kiln
{
  "id": "app-clinic-maintenance",
  "name": "Clinic Maintenance",
  "tier": 2,
  "category": "clinical",
  "pattern": "scheduler",
  "pitch": "Everything that comes round again, and when it is next due.",
  "features": ["crud", "recur", "search", "sort", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "task",
      "label": "Task",
      "fields": [
        {"name": "title", "label": "Task", "type": "text", "required": true},
        {"name": "last", "label": "Last done", "type": "date"},
        {"name": "every", "label": "Every (days)", "type": "number"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "recur": {"last": "last", "every": "every"},
  "storage": {"kind": "localstorage", "namespace": "clinic-maintenance"},
  "accent": "#f59e0b",
  "done_means": [
    "last done 2026-11-01 every 30 days shows next 2026-12-01",
    "a task whose next date has passed is shown in the warning colour",
    "the strip counts what is due and what falls due this week",
    "a task with no interval shows no next date"
  ],
  "not": ["network calls", "accounts", "sync", "calendar rules", "notifications"]
}
```

## Pitch

Everything that comes round again, and when it is next due.

## The job

- List the things that need doing again
- Record when each was last done
- Record how often it should be done, in days
- See what is due, without counting on a calendar
- Take the list out as a file

## The mechanic

The next date is `last + every days`, computed in UTC on plain date strings, so it cannot
drift across a timezone. It is recomputed on every render, so it cannot go stale.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No calendar rules, no business days, no notifications
- No history beyond the last time

## What it does when things go wrong

- **bad input** — a task without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the task stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:clinic-maintenance:corrupt`, the list resets

## Done means

- Last done 2026-11-01 every 30 days shows next 2026-12-01
- A task whose next date has passed is shown in the warning colour
- The strip counts what is due and what falls due this week
- A task with no interval shows no next date

## The data

Stored in `localStorage` under `kiln:clinic-maintenance`. A date is a `YYYY-MM-DD` string and
an interval is a plain number of days.
