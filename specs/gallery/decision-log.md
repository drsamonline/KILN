# Practice Decisions

```json kiln
{
  "id": "app-practice-decisions",
  "name": "Practice Decisions",
  "tier": 1,
  "category": "clinical",
  "pattern": "decision-log",
  "pitch": "What was decided, from which options, and why — while you still remember.",
  "features": ["crud", "decide", "search", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "decision",
      "label": "Decision",
      "fields": [
        {"name": "title", "label": "Decision", "type": "text", "required": true},
        {"name": "options", "label": "Options considered", "type": "tags"},
        {"name": "choice", "label": "Chosen", "type": "text"},
        {"name": "why", "label": "Why", "type": "longtext"},
        {"name": "date", "label": "Day", "type": "date"}
      ]
    }
  ],
  "decide": {"choice": "choice", "why": "why"},
  "storage": {"kind": "localstorage", "namespace": "practice-decisions"},
  "accent": "#a78bfa",
  "done_means": [
    "a decision with a choice shows what was chosen and why",
    "a decision with no choice is shown as still open and counted in the strip",
    "the options still show after a choice is made",
    "searching for a word no decision contains hides every row"
  ],
  "not": ["network calls", "accounts", "sync", "voting", "approval steps"]
}
```

## Pitch

What was decided, from which options, and why — while you still remember.

## The job

- Record a decision while it is fresh
- Keep the options that were considered, not just the winner
- Write the reason next to it
- See which decisions are still open
- Take the log out as a file

## The mechanic

The choice is a text field and the reason is a long text field, shown on the row. A decision
with no choice is counted as open in the strip, so the log doubles as a to-decide list.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No voting: the options are text, not tallies
- No approval steps, no superseding

## What it does when things go wrong

- **bad input** — a decision without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the decision stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:practice-decisions:corrupt`, the log resets

## Done means

- A decision with a choice shows what was chosen and why
- A decision with no choice is shown as still open and counted in the strip
- The options stay visible after a choice is made
- Searching for a word no decision contains hides every row

## The data

Stored in `localStorage` under `kiln:practice-decisions`. Options are a list of short strings;
the choice is one of them, kept as text so the record reads as a sentence.
