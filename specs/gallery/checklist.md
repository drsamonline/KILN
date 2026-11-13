# Clinic Opening

```json kiln
{
  "id": "app-clinic-opening",
  "name": "Clinic Opening",
  "tier": 1,
  "category": "clinical",
  "pattern": "checklist",
  "pitch": "The nine things that must be true before the first patient walks in.",
  "features": ["crud", "search", "sort", "progress", "toggle", "export", "theme"],
  "entities": [
    {
      "name": "task",
      "label": "Task",
      "fields": [
        {"name": "title", "label": "Task", "type": "text", "required": true},
        {"name": "done", "label": "Done", "type": "bool"},
        {"name": "area", "label": "Area", "type": "select", "options": ["room", "stock", "records", "staff"]},
        {"name": "note", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "progress": {"field": "done", "label": "done"},
  "storage": {"kind": "localstorage", "namespace": "clinic-opening"},
  "accent": "#4ade80",
  "done_means": [
    "ticking a task and reloading keeps it ticked",
    "two of four tasks done shows 2 of 4 and 50%",
    "ticking the last task shows 100% and zero left",
    "searching for a word no task contains hides every row"
  ],
  "not": ["network calls", "accounts", "sync", "patient data", "clinical advice"]
}
```

## Pitch

The nine things that must be true before the first patient walks in.

## The job

- Work through the opening list, one tap per task
- See how many are left without counting them
- Keep a note on a task that needs explaining
- Find a task by typing
- Print the list, or take it out as a file

## The mechanic

One row, one boolean. The bar is the count of true rows over all rows, computed when the
page is drawn. A tick writes immediately — there is no save button, because a checklist you
have to save is a checklist people forget to save.

## What it must NOT do

- No network request of any kind
- No accounts, no sync between devices
- No patient data, ever
- No clinical advice or thresholds it invented

## What it does when things go wrong

- **bad input** — a task without a name refuses to save and the form names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the tick stays in memory, a banner says it will not survive a reload, export is offered
- **corrupt state** — the raw value is copied to `kiln:clinic-opening:corrupt`, the list resets, a banner says where it went

## Done means

- Ticking a task and reloading keeps it ticked
- Two of four tasks done shows 2 of 4 and 50%
- Ticking the last task shows 100% and zero left
- Searching for a word no task contains hides every row

## The data

Stored in `localStorage` under `kiln:clinic-opening`. The count and the percentage are
computed when the page is drawn; neither is stored. Nothing leaves the device unless the
user exports it.
