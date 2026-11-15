# Today Card

A fleet app, rebuilt as a spec. The original is
[`today-card`](https://github.com/drsamonline/today-card): one card for the day.

```json kiln
{
  "id": "app-today-card",
  "name": "Today Card",
  "tier": 1,
  "category": "personal",
  "pattern": "journal",
  "pitch": "One card for the day: the date, one intention, and what actually happened.",
  "features": ["crud", "detail", "search", "sort", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "day",
      "label": "Day",
      "fields": [
        {"name": "title", "label": "Date", "type": "date", "required": true},
        {"name": "body", "label": "One intention", "type": "longtext"},
        {"name": "note", "label": "What happened", "type": "longtext"}
      ]
    }
  ],
  "detail": {"field": "body"},
  "storage": {"kind": "localstorage", "namespace": "today-card"},
  "accent": "#f59e0b",
  "done_means": [
    "opening the app shows the newest day first",
    "a long intention shows as paragraphs in the read view",
    "a day with no note still shows in the list"
  ],
  "not": ["network calls", "accounts", "sync", "reminders"]
}
```

## Pitch

One card for the day: the date, one intention, and what actually happened.

## The job

A person writes one intention in the morning and one line about the day in the evening.
Nothing else. The app opens on the list, newest first.

## The mechanic

A list sorted by date. The first record is today if it exists, and the form is one
keystroke away.

## What it must NOT do

- call the network
- ask for an account
- remind you at a time

## What it does when things go wrong

- storage full: say so, keep the note in memory, offer export
- a day with no note: show the date, leave the note empty

## Done means

- opening the app shows the newest day first
- a long intention shows as paragraphs in the read view
- a day with no note still appears in the list

## The data

One record per day. The date is the key, and the intention is the thing you read back.
