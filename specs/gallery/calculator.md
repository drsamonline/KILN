# Reading Time

```json kiln
{
  "id": "app-reading-time",
  "name": "Reading Time",
  "tier": 1,
  "category": "utility",
  "pattern": "calculator",
  "pitch": "How long this chapter will take, at the speed you actually read.",
  "features": ["formula", "theme"],
  "entities": [],
  "calculator": {
    "inputs": [
      {"name": "words", "label": "Words", "type": "number", "default": 1000, "min": 0},
      {"name": "wpm", "label": "Words per minute", "type": "number", "default": 200, "min": 1}
    ],
    "formula": "words / wpm",
    "output": {"label": "Reading time", "unit": "min", "decimals": 1},
    "note": "Your own pace is the only honest input here. Time one page, count its words, divide."
  },
  "storage": {"kind": "localstorage", "namespace": "reading-time"},
  "accent": "#a78bfa",
  "done_means": [
    "1000 words at 200 words per minute shows 5.0 min",
    "changing the pace to 100 shows 10.0 min",
    "setting words per minute to 0 refuses and shows a message",
    "a pace of 250 with 750 words shows 3.0 min"
  ],
  "not": ["network calls", "accounts", "history", "a reading speed it guessed"]
}
```

## Pitch

How long this chapter will take, at the speed you actually read.

## The job

- Put in a word count
- Put in your own reading speed
- Read the answer in minutes
- Change one input and watch the answer change

## The mechanic

Two numbers and one expression. The expression lives in the spec as text and is evaluated
by a small parser in the page — no `eval`, no library, no network. Nothing is stored,
because a calculator that remembers is a spreadsheet with worse manners.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No history, no saved results
- No estimate of your reading speed: it asks, it does not guess

## What it does when things go wrong

- **bad input** — a blank or zero pace refuses to calculate and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — nothing is stored, so nothing can fail to store
- **corrupt state** — there is no saved state to corrupt; the app opens at its defaults

## Done means

- 1000 words at 200 words per minute shows 5.0 min
- Changing the pace to 100 shows 10.0 min
- Setting words per minute to 0 refuses and shows a message
- A pace of 250 with 750 words shows 3.0 min

## The data

Nothing is stored. The inputs are held in the page while it is open and are gone when it
closes. There is no `localStorage` key for this app and nothing to export.
