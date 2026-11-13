# Journal

```json kiln
{
  "id": "app-journal",
  "name": "Journal",
  "tier": 1,
  "category": "creative",
  "pattern": "journal",
  "pitch": "A page a day, kept on the device, read at a comfortable width.",
  "features": ["crud", "search", "detail", "sort", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "entry",
      "label": "Entry",
      "fields": [
        {"name": "title", "label": "Day", "type": "date", "required": true},
        {"name": "body", "label": "What happened", "type": "longtext"},
        {"name": "tags", "label": "Tags", "type": "tags"}
      ]
    }
  ],
  "detail": {"field": "body"},
  "storage": {"kind": "localstorage", "namespace": "journal"},
  "accent": "#a78bfa",
  "done_means": [
    "clicking a day opens the entry read-only, with the text as paragraphs",
    "saving an entry and reloading keeps it in the list",
    "typing a word from the text hides every entry that does not contain it",
    "the read view offers Edit and Close, and Edit opens the form"
  ],
  "not": ["network calls", "accounts", "sync", "rich text", "images"]
}
```

## Pitch

A page a day, kept on the device, read at a comfortable width.

## The job

- Write an entry against a date
- Read it back full-width, not squeezed into a row
- Find something written months ago by typing a word
- Tag an entry so a theme can be followed
- Take the whole journal out as a file

## The mechanic

The list is for finding; the detail view is for reading. One long text field carries the
writing, and the read view gives it the width of the dialog instead of a row.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No rich text, no images
- No claim of encryption: the file is plain text

## What it does when things go wrong

- **bad input** — an entry without a date refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the entry stays in memory, a banner says it will not survive a reload, export is offered
- **corrupt state** — the raw value is copied to `kiln:journal:corrupt`, the journal resets, a banner says where it went

## Done means

- Clicking a day opens the entry read-only, with the text as paragraphs
- Saving an entry and reloading keeps it in the list
- Typing a word from the text hides every entry that does not contain it
- The read view offers Edit and Close, and Edit opens the form

## The data

Stored in `localStorage` under `kiln:journal`. Nothing leaves the device unless the user
exports it, and the export is plain text in a JSON or CSV file.
