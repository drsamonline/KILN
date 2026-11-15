# Clinical Calculator

A fleet app, rebuilt as a spec. The original is
[`bmi-bmr-tdee-macros-fluid-calculator`](https://github.com/drsamonline/bmi-bmr-tdee-macros-fluid-calculator).

```json kiln
{
  "id": "app-clinical-calc",
  "name": "Clinical Calculator",
  "tier": 1,
  "category": "clinical",
  "pattern": "calculator",
  "pitch": "BMI from weight and height, with the working shown.",
  "features": ["formula", "theme", "a11y"],
  "entities": [],
  "calculator": {
    "inputs": [
      {"name": "weight", "label": "Weight (kg)", "type": "number", "default": 70, "min": 0},
      {"name": "height", "label": "Height (m)", "type": "number", "default": 1.75, "min": 0}
    ],
    "formula": "weight / (height * height)",
    "output": {"name": "bmi", "label": "BMI", "decimals": 2},
    "note": "weight in kg, height in metres. The formula is in the spec, not in the code."
  },
  "storage": {"kind": "localstorage", "namespace": "clinical-calc"},
  "accent": "#4ade80",
  "done_means": [
    "entering 70 and 1.75 shows 22.86",
    "an empty input shows a zero result, not an error",
    "a height of zero shows no result rather than infinity"
  ],
  "not": ["network calls", "accounts", "diagnosis", "patient identifiers"]
}
```

## Pitch

BMI from weight and height, with the working shown.

## The job

A clinician needs one number quickly and wants to see how it was reached.

## The mechanic

Two inputs, one formula, one result. The formula is written in the spec, so changing it is
a spec change, not a code change.

## What it must NOT do

- call the network
- store a patient identifier
- offer a diagnosis

## What it does when things go wrong

- an empty input: treat it as zero and say so
- a division by zero: show no result rather than infinity

## Done means

- entering 70 and 1.75 shows 22.86
- an empty input shows a zero result, not an error
- a height of zero shows no result rather than infinity

## The data

Nothing is stored. The app is the formula.
