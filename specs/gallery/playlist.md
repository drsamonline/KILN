# Consultation Queue

```json kiln
{
  "id": "app-consultation-queue",
  "name": "Consultation Queue",
  "tier": 1,
  "category": "clinical",
  "pattern": "playlist",
  "pitch": "The running order for the evening, and how long it takes to get through.",
  "features": ["crud", "sequence", "search", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "slot",
      "label": "Slot",
      "fields": [
        {"name": "title", "label": "Patient", "type": "text", "required": true},
        {"name": "position", "label": "Position", "type": "number"},
        {"name": "minutes", "label": "Length", "type": "duration"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "sequence": {"order": "position", "duration": "minutes"},
  "storage": {"kind": "localstorage", "namespace": "consultation-queue"},
  "accent": "#a78bfa",
  "done_means": [
    "three slots of 10, 15 and 20 minutes show 45m as the total",
    "each row shows its position in the running order and the time to reach it",
    "changing a position reorders the list on the next render",
    "a slot with no length shows the same running total as the row before it"
  ],
  "not": ["network calls", "accounts", "sync", "drag and drop", "playback"]
}
```

## Pitch

The running order for the evening, and how long it takes to get through.

## The job

- Put the evening in an explicit order
- Give each slot a length
- See the time to reach each slot
- See the total for the evening
- Take the queue out as a file

## The mechanic

An explicit `position` number decides the order, so an edit cannot shuffle the list. The
running time is the sum of the lengths up to and including each row, derived on every render.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No drag and drop: the order is a number you type
- No playback, no shuffle, no repeat

## What it does when things go wrong

- **bad input** — a slot without a patient refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the slot stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:consultation-queue:corrupt`, the queue resets

## Done means

- Three slots of 10, 15 and 20 minutes show 45m as the total
- Each row shows its position in the running order and the time to reach it
- Changing a position reorders the list on the next render
- A slot with no length adds nothing to the running total

## The data

Stored in `localStorage` under `kiln:consultation-queue`. A position is a plain number; a
length is in minutes.
