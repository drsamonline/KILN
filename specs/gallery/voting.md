# Remedy Vote

```json kiln
{
  "id": "app-remedy-vote",
  "name": "Remedy Vote",
  "tier": 1,
  "category": "clinical",
  "pattern": "voting",
  "pitch": "Six remedies, a show of hands, and the winner in green.",
  "features": ["crud", "tally", "search", "sort", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "option",
      "label": "Option",
      "fields": [
        {"name": "title", "label": "Remedy", "type": "text", "required": true},
        {"name": "votes", "label": "Votes", "type": "number"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "tally": {"field": "votes"},
  "storage": {"kind": "localstorage", "namespace": "remedy-vote"},
  "accent": "#4ade80",
  "done_means": [
    "options with 5, 3 and 2 votes show 10 total and the 5 marked as leading",
    "each row shows a bar and a percentage for its share of the vote",
    "a tie shows every leading option in green and a count of how many are tied",
    "an option with no votes shows a zero share, not a missing bar"
  ],
  "not": ["network calls", "accounts", "sync", "ballots across devices", "clinical advice"]
}
```

## Pitch

Six remedies, a show of hands, and the winner in green.

## The job

- List the options on the table
- Put a count against each
- See the share and the leader without arithmetic
- Change a count and see it re-drawn
- Take the result out as a file

## The mechanic

The count is a number you type, and everything else is derived: the total, the share of the
total, the width of the bar against the leader, and which row leads. A tie marks every leader.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No ballots across devices: one device, one room
- No weighting, no ranking, no rounds
- No clinical advice

## What it does when things go wrong

- **bad input** — an option without a name refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the option stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:remedy-vote:corrupt`, the vote resets

## Done means

- Options with 5, 3 and 2 votes show 10 total and the 5 marked as leading
- Each row shows its share of the vote as a bar and a percentage
- A tie marks every leading option and says how many are tied
- An option with no votes shows a zero share, not a missing bar

## The data

Stored in `localStorage` under `kiln:remedy-vote`. A count is a plain number; a negative or
missing count is treated as zero rather than as a vote.
