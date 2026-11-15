# NTET Practice

A fleet app, rebuilt as a spec. The quiz half of
[`ntet-homoeopathy-cbt`](https://github.com/drsamonline/ntet-homoeopathy-cbt).

```json kiln
{
  "id": "app-ntet-practice",
  "name": "NTET Practice",
  "tier": 2,
  "category": "education",
  "pattern": "quiz",
  "pitch": "Eighty questions, one at a time, and a score you can trust.",
  "features": ["crud", "quiz", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "question",
      "label": "Question",
      "fields": [
        {"name": "title", "label": "Question", "type": "text", "required": true},
        {"name": "options", "label": "Options", "type": "tags", "required": true},
        {"name": "answer", "label": "Correct option", "type": "text", "required": true},
        {"name": "body", "label": "Why", "type": "longtext"}
      ]
    }
  ],
  "quiz": {"answer": "answer", "prompt": "title", "explain": "body"},
  "storage": {"kind": "localstorage", "namespace": "ntet-practice"},
  "accent": "#7c9cff",
  "done_means": [
    "answering three of five correctly shows 3 of 5 at the end",
    "a wrong answer shows the explanation",
    "a question with no options is skipped and counted"
  ],
  "not": ["network calls", "accounts", "sync", "proctoring"]
}
```

## Pitch

Eighty questions, one at a time, and a score you can trust.

## The job

A candidate practises on a phone with no signal and wants to know what they got wrong.

## The mechanic

One question per screen, the options as buttons, the score at the end. The score is
derived from the picks, never stored.

## What it must NOT do

- call the network
- upload results
- claim to be an official exam

## What it does when things go wrong

- a question with no correct option marked: skip it and say how many were skipped
- a question with no options: the same

## Done means

- answering three of five correctly shows 3 of 5 at the end
- a wrong answer shows the explanation
- a question with no options is skipped and counted

## The data

The question bank is the records. The score is computed on the fly and never persisted.
