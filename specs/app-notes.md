# Notes

```json kiln
{
  "id": "app-notes",
  "name": "Notes",
  "tier": 1,
  "category": "productivity",
  "pitch": "Write a note, find it again, keep it on the device.",
  "features": ["crud", "search", "tags", "export", "import", "theme", "stats"],
  "entities": [
    {
      "name": "note",
      "label": "Note",
      "fields": [
        {"name": "title", "label": "Title", "type": "text", "required": true},
        {"name": "body", "label": "Body", "type": "longtext"},
        {"name": "tags", "label": "Tags", "type": "tags"},
        {"name": "created", "label": "Created", "type": "date"}
      ]
    }
  ],
  "storage": {"kind": "localstorage", "namespace": "notes"},
  "accent": "#7c9cff",
  "done_means": [
    "creating a note and reloading the page shows the note in the list",
    "typing a query that no note contains hides every row",
    "exporting then importing the file restores the same number of notes",
    "toggling the theme and reloading keeps the chosen theme"
  ],
  "not": ["network calls", "accounts", "sync", "rich text formatting"]
}
```

## Pitch

One place for a thought, a list, a paragraph. It stays on the device.

## The job

- Write a note with a title and a body
- Tag it so it can be found later
- Find it by any word in the title or body
- Take every note out as a file, and put them back
- Read it in the dark

## The mechanic

A note is one record in one list. The list, the form, the search index and the
export all read the same field declaration, so a field added to the spec appears
in all four without being wired by hand.

## What it must NOT do

- No account, no sign-in
- No network request of any kind
- No sync between devices
- No rich text editor

## What it does when things go wrong

- **bad input** — a note without a title refuses to save and the form names the field
- **no network** — nothing changes; a line says the network is not needed
- **storage full** — the note stays in memory, a banner says it will not survive a reload, export is offered
- **corrupt state** — the raw value is copied to `kiln:notes:corrupt:<timestamp>`, the app resets, a banner says where it went

## Done means

- Creating a note and reloading the page shows the note in the list
- Typing a query that no note contains hides every row
- Exporting then importing the file restores the same number of notes
- Toggling the theme and reloading keeps the chosen theme

## The data

Stored in `localStorage` under `kiln:notes`. Nothing leaves the device unless the
user exports it, and the export is a file the user chooses to keep.
