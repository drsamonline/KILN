# Consultation Invoice

```json kiln
{
  "id": "app-consultation-invoice",
  "name": "Consultation Invoice",
  "tier": 2,
  "category": "clinical",
  "pattern": "invoice",
  "pitch": "Lines of quantity and rate, an amount each, and a total you can print.",
  "features": ["crud", "amount", "print", "export", "theme", "a11y"],
  "entities": [
    {
      "name": "line",
      "label": "Line",
      "fields": [
        {"name": "title", "label": "Description", "type": "text", "required": true},
        {"name": "qty", "label": "Quantity", "type": "number"},
        {"name": "rate", "label": "Rate", "type": "currency_cents"},
        {"name": "body", "label": "Note", "type": "longtext"}
      ]
    }
  ],
  "amount": {"qty": "qty", "rate": "rate"},
  "currency": "₹",
  "storage": {"kind": "localstorage", "namespace": "consultation-invoice"},
  "accent": "#38bdf8",
  "done_means": [
    "three lines of 2 x 500, 1 x 1200 and 3 x 250 show 3150 as the total",
    "each line shows its own amount next to the quantity and the rate",
    "the print button produces a page with the lines and the total",
    "a line with no quantity shows an amount of zero, not a blank"
  ],
  "not": ["network calls", "accounts", "sync", "tax", "invoice numbering", "payment status"]
}
```

## Pitch

Lines of quantity and rate, an amount each, and a total you can print.

## The job

- Type each line of a bill: what, how many, at what rate
- See the amount per line without a calculator
- See the total
- Print it or take it out as a file
- Keep it on the device, with no service in the middle

## The mechanic

Quantity times rate, rounded once at the line, in integer cents. The total is the sum of the
amounts that are shown, so what you read is what you add up.

## What it must NOT do

- No network request of any kind
- No accounts, no sync
- No tax, no discount, no currency conversion
- No invoice numbering, no due dates, no payment status

## What it does when things go wrong

- **bad input** — a line without a description refuses to save and names the field
- **no network** — nothing changes; the app says the network is not needed
- **storage full** — the line stays in memory, a banner says it will not survive a reload
- **corrupt state** — the raw value is copied to `kiln:consultation-invoice:corrupt`, the bill resets

## Done means

- Three lines of 2 × 500, 1 × 1200 and 3 × 250 show 3150 as the total
- Each line shows its own amount next to the quantity and the rate
- The print button produces a page with the lines and the total
- A line with no quantity shows an amount of zero, not a blank

## The data

Stored in `localStorage` under `kiln:consultation-invoice`. Rates and amounts are integer
cents; the quantity is a plain number.
