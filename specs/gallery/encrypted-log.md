# Sealed Case Log

```json kiln
{
  "id": "app-sealed-log",
  "name": "Sealed Case Log",
  "tier": 2,
  "category": "clinical",
  "pattern": "crud-list",
  "pitch": "Patient notes that stay unreadable on disk without your passphrase.",
  "features": ["crud", "crypto", "search", "sort", "stats", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "case",
      "label": "Case",
      "fields": [
        {"name": "title", "label": "Patient", "type": "text", "required": true},
        {"name": "seen", "label": "Seen", "type": "date"},
        {"name": "body", "label": "Notes", "type": "longtext"}
      ]
    }
  ],
  "crypto": {"iterations": 250000},
  "storage": {"kind": "localstorage", "namespace": "sealed-log"},
  "accent": "#a78bfa",
  "done_means": [
    "opening the file asks for a passphrase before it shows any record",
    "the stored value shows no patient name when read as text",
    "a wrong passphrase shows an error and opens nothing"
  ],
  "not": ["network calls", "accounts", "sync", "passphrase recovery"]
}
```

## Pitch

Patient notes that stay unreadable on disk without your passphrase.

## The job

A clinician keeps notes on a shared laptop. If the file is copied, the notes should be
unreadable without the passphrase, and there is no server to hold a key.

## The mechanic

PBKDF2-SHA256 turns the passphrase and a random salt into an AES-GCM key. Every save seals
the whole store. Nothing readable reaches the disk.

## What it must NOT do

- store the passphrase anywhere
- offer a recovery route, because there is no safe one
- transmit anything

## What it does when things go wrong

- a wrong passphrase: say so, open nothing, and keep the sealed blob intact
- a missing salt: say the file cannot be opened on this device
- storage full: keep the change in memory and offer export

## Done means

- opening the file asks for a passphrase before it shows any record
- the value stored on the device contains no patient name in readable form
- a wrong passphrase shows an error and opens nothing

## The data

One record per case. The whole store is sealed as one blob, so a single record cannot be
read out of it.
