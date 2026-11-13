# Case History

```json kiln
{
  "id": "app-case-history",
  "name": "Case History",
  "tier": 1,
  "category": "clinical",
  "pattern": "timeline",
  "pitch": "Everything that happened, grouped by the month it happened in.",
  "features": ["crud", "timeline", "search", "sort", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "event",
      "label": "Event",
      "fields": [
        {"name": "title", "label": "Event", "type": "text", "required": true},
        {"name": "date", "label": "Day", "type": "date", "required": true},
        {"name": "kind", "label": "Kind", "type": "select",
         "options": ["consultation", "remedy", "follow-up", "note"]},
        {"name": "body", "label": "Detail", "type": "longtext"}
      ]
    }
  ],
  "timeline": {"field": "date"},
  "storage": {"kind": "localstorage", "namespace": "case-history"},
  "accent": "#a78bfa",
  "done_means": [
    "two events in November and one in October show two month headings",
    "the newest month is shown first",
    "an event with no date is shown under Undated",
    "searching for a word no event contains hides every row"
  ],
  "not": ["network calls", "accounts", "sync", "clinical advice"]
}
```

## Pitch

Everything that happened, grouped by the month it happened in.

## The job

- Record an event with a date
- Read the history as months, not as a flat list
- Find an event by typing
- Keep the detail on the event
- Take the history out as a file

## The mechanic

The same records as a list, grouped by the first seven characters of the date and sorted
newest first. A record without a date is not hidden; it goes into a group called Undated.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No year headings, no counts per month
- No clinical advice

## What it does when things go wrong

- **bad input** — an event without a day refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the event stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:case-history:corrupt`, the history resets

## Done means

- Two events in November and one in October show two month headings
- The newest month is shown first
- An event with no date is shown under Undated
- Searching for a word no event contains hides every row

## The data

Stored in `localStorage` under `kiln:case-history`. A day is a `YYYY-MM-DD` string, so the
grouping is a string comparison and cannot drift across a timezone.
