# Clinic Board

```json kiln
{
  "id": "app-clinic-board",
  "name": "Clinic Board",
  "tier": 2,
  "category": "clinical",
  "pattern": "kanban",
  "pitch": "Every case on one board, from first call to closed.",
  "features": ["crud", "board", "search", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "case",
      "label": "Case",
      "fields": [
        {"name": "title", "label": "Patient", "type": "text", "required": true},
        {"name": "stage", "label": "Stage", "type": "select",
         "options": ["new", "history", "remedy", "follow-up", "closed"]},
        {"name": "date", "label": "Opened", "type": "date"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "board": {"field": "stage"},
  "storage": {"kind": "localstorage", "namespace": "clinic-board"},
  "accent": "#38bdf8",
  "done_means": [
    "three cases across two stages show two columns, with 2 and 1 on the headers",
    "pressing the right arrow on a card shows it in the next column",
    "the left arrow on the first column shows the card where it was",
    "a case with no stage shows in a column called Unplaced"
  ],
  "not": ["network calls", "accounts", "sync", "drag and drop", "clinical advice"]
}
```

## Pitch

Every case on one board, from first call to closed.

## The job

- See every open case, grouped by stage
- Move a case on when it advances
- Find a patient by typing
- Read the note on a card without opening the form
- Take the board out as a file

## The mechanic

The columns are the options of one select field, in the order the spec lists them. A move is
a write to that field, so the board and the list are the same data seen two ways.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No drag and drop: two buttons per card, which also works from a keyboard
- No clinical advice

## What it does when things go wrong

- **bad input** — a case without a patient name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the move stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:clinic-board:corrupt`, the board resets, a banner says where it went

## Done means

- Three cases across two stages show two columns, with 2 and 1 on the headers
- Pressing the right arrow on a card moves it to the next stage
- The left arrow on the first column leaves the card where it is
- A case with no stage shows in a column called Unplaced

## The data

Stored in `localStorage` under `kiln:clinic-board`. The stage is a string, not a number, so a
column can be renamed without rewriting rows.
