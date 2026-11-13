# Remedy Directory

```json kiln
{
  "id": "app-remedy-directory",
  "name": "Remedy Directory",
  "tier": 2,
  "category": "reference",
  "pattern": "search-directory",
  "pitch": "Type three letters of a remedy and read its keynote, without a book.",
  "features": ["crud", "search", "directory", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "remedy",
      "label": "Remedy",
      "fields": [
        {"name": "title", "label": "Remedy", "type": "text", "required": true},
        {"name": "potency", "label": "Potency", "type": "select",
         "options": ["6C", "30C", "200C", "1M"]},
        {"name": "body", "label": "Keynote", "type": "longtext"}
      ]
    }
  ],
  "directory": {"subtitle": "potency", "body": "body"},
  "storage": {"kind": "localstorage", "namespace": "remedy-directory"},
  "accent": "#a78bfa",
  "done_means": [
    "opening the app shows the count, not the list, with the cursor in the search box",
    "typing three letters shows only the remedies whose name contains them",
    "the matching letters show a highlight inside the card",
    "clearing the box shows the count again, not the whole list"
  ],
  "not": ["network calls", "accounts", "sync", "prescribing", "clinical advice"]
}
```

## Pitch

Type three letters of a remedy and read its keynote, without a book.

## The job

- Find a remedy by part of its name
- Read its keynote without opening a form
- See which potency you recorded
- Keep adding remedies as you learn them
- Take the directory out as a file

## The mechanic

The list is a lookup, not a browse. The search box takes focus on open, and the list stays
quiet until you type — so the first keystroke is the search, not a scroll.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No prescribing, no clinical advice
- No sort or filter controls: this view has one control on purpose

## What it does when things go wrong

- **bad input** — a remedy without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the remedy stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:remedy-directory:corrupt`, the directory resets

## Done means

- Opening the app shows the count and puts the cursor in the search box
- Typing three letters shows only the remedies whose name contains them
- The matching letters are marked inside the card
- Clearing the box shows the count again, not the whole list

## The data

Stored in `localStorage` under `kiln:remedy-directory`. Nothing leaves the device unless the
user exports it.
