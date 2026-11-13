# Materia Medica Quiz

```json kiln
{
  "id": "app-materia-quiz",
  "name": "Materia Medica Quiz",
  "tier": 2,
  "category": "reference",
  "pattern": "quiz",
  "pitch": "Twenty keynotes, one at a time, and a score you can trust.",
  "features": ["crud", "quiz", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "question",
      "label": "Question",
      "fields": [
        {"name": "title", "label": "Question", "type": "text", "required": true},
        {"name": "options", "label": "Options", "type": "tags"},
        {"name": "answer", "label": "Correct option", "type": "text", "required": true},
        {"name": "body", "label": "Why", "type": "longtext"}
      ]
    }
  ],
  "quiz": {"answer": "answer", "prompt": "title", "explain": "body"},
  "storage": {"kind": "localstorage", "namespace": "materia-quiz"},
  "accent": "#a78bfa",
  "done_means": [
    "three questions with two right answers show 2 of 3 at the end",
    "each question shows its options as buttons, one question at a time",
    "picking an option shows the next question",
    "the again button returns to the first question with a zero score"
  ],
  "not": ["network calls", "accounts", "sync", "spaced repetition", "clinical advice"]
}
```

## Pitch

Twenty keynotes, one at a time, and a score you can trust.

## The job

- Write a question with a few options and one right answer
- Answer one at a time, without seeing the rest
- See the score at the end
- Run it again from the start
- Take the question bank out as a file

## The mechanic

A question is an ordinary record. The options are a tags field, the answer is a text field,
and the score is counted from the picks at the end — never stored, so a retake is honest.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No spaced repetition, no difficulty weighting, one correct answer
- No clinical advice

## What it does when things go wrong

- **bad input** — a question without an answer refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the question stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:materia-quiz:corrupt`, the bank resets

## Done means

- Three questions with two right answers show 2 of 3 at the end
- Each question shows its options as buttons, one question at a time
- Picking an option shows the next question
- The again button returns to the first question with a zero score

## The data

Stored in `localStorage` under `kiln:materia-quiz`. The answer is plain text and is matched
case-insensitively, so it must match one of the options exactly.
