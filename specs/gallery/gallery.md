# Remedy Gallery

```json kiln
{
  "id": "app-remedy-gallery",
  "name": "Remedy Gallery",
  "tier": 1,
  "category": "reference",
  "pattern": "gallery",
  "pitch": "A wall of remedies, each with its picture and one line.",
  "features": ["crud", "gallery", "search", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "card",
      "label": "Card",
      "fields": [
        {"name": "title", "label": "Remedy", "type": "text", "required": true},
        {"name": "image", "label": "Picture", "type": "image"},
        {"name": "caption", "label": "One line", "type": "text"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "gallery": {"image": "image", "caption": "caption"},
  "storage": {"kind": "localstorage", "namespace": "remedy-gallery"},
  "accent": "#4ade80",
  "done_means": [
    "four records with image urls show four cards, each with an img element",
    "a record with no image shows a placeholder instead of a hole",
    "searching shows only the matching cards in the grid",
    "clicking a card opens it for editing"
  ],
  "not": ["network calls", "accounts", "sync", "image upload", "clinical advice"]
}
```

## Pitch

A wall of remedies, each with its picture and one line.

## The job

- Keep a card per remedy, with a picture
- See them as a grid, not a list
- Read one line under each picture
- Find a card by typing
- Take the cards out as a file

## The mechanic

An image is a url, stored as text. Nothing is uploaded and nothing is fetched at build time,
so the grid is only as fast as wherever the pictures live. A missing image degrades to a
placeholder, not a hole in the grid.

## What it must NOT do

- No network request of any kind, except the images the browser loads
- No accounts, no sync
- No upload, no cropping, no zoom, no lightbox
- No clinical advice

## What it does when things go wrong

- **bad input** — a card without a name refuses to save and names the field
- **no network** — the cards still open; only the pictures that are not cached are missing
- **storage full** — the card stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:remedy-gallery:corrupt`, the grid resets

## Done means

- Four records with image urls show four cards, each with an img element
- A record with no image shows a placeholder instead of a hole
- Searching narrows the grid to the matching cards
- Clicking a card opens it for editing

## The data

Stored in `localStorage` under `kiln:remedy-gallery`. An image is a url string: `https://…` or
a `data:` uri for something small enough to carry inside the file.
