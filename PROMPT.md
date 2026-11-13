# PROMPT — how to get a spec out of any LLM

KILN does not need a model. This file is the only bridge to one, and it is a
copy-paste bridge, not an integration.

---

## The four steps

| Step | What you do |
|---|---|
| 1 | Copy the prompt block below into any chat window — local, hosted, phone, terminal |
| 2 | Replace the five `[[...]]` placeholders with your own words |
| 3 | Paste the reply into a file, e.g. `specs/app-thing.md` |
| 4 | `python3 -m kiln adopt specs/app-thing.md` — it repairs, validates, then builds |

If the model rambles, adds a preamble, uses YAML, forgets a section, or invents a
feature that does not exist, `kiln adopt` fixes or rejects it and tells you what it
changed. A sloppy model cannot produce a broken app.

---

## The prompt

```text
You are writing a KILN specification for a small offline application.

CONSTRAINTS
- The app runs from one HTML file, opened from disk. No server, no account, no network.
- It stores data in the browser's localStorage on the user's own device.
- It must work with the network unplugged.

MY IDEA
  App idea:        [[APP_IDEA]]
  Who uses it:     [[WHO_USES_IT]]
  What they record:[[WHAT_THEY_RECORD]]
  Where they use it:[[PLATFORM]]
  It must never:   [[MUST_NOT]]

OUTPUT FORMAT — follow exactly, nothing before it and nothing after it

1. A level-one heading with the app name.
2. One fenced block tagged `json kiln` containing a JSON object with these keys:
   id, name, tier, category, pitch, features, entities, storage, accent, done_means, not
3. Then these level-two sections, in this order:
   ## Pitch
   ## The job
   ## The mechanic
   ## What it must NOT do
   ## What it does when things go wrong
   ## Done means
   ## The data

FIELD RULES
- id: "app-" followed by lowercase letters and hyphens. It must match the file name.
- name: 1 to 40 characters.
- tier: 1, 2 or 3. Use 1 for a single-list utility.
- category: one of productivity, utility, health, education, finance, reference,
  creative, clinical, community.
- pitch: one sentence, 10 to 140 characters, in the user's words.
- features: choose ONLY from the catalogue below, using the exact ids. Include the
  features the app genuinely needs, not all of them.
- entities: a list with one or more objects: {"name","label","fields"}.
  Entity and field names are lowercase, no spaces.
- fields: each {"name","label","type"} with type one of
  text, longtext, number, date, bool, select, tags.
  A select field needs "options": a list of at least two strings.
  Mark at most two fields "required": true.
  The first field is the row title and should be a text field.
- storage: {"kind": "localstorage", "namespace": "<lowercase-hyphen-slug>"}
- If the app is used in more than one language, add "i18n": {"languages": ["en", "hi"]}
  and include the i18n feature. Known dictionaries: en, hi, gu. English must be first.
- If the app will be used by real people over time, include the a11y and feedback
  features: a skip link, a focus ring, and honest banners about size and backups.
- If the app is ONE CALCULATION with no list (a converter, a rate, a dose), use
  "pattern": "calculator" with "entities": [] and a "calculator" object:
  {"inputs": [{"name","label","default","min","max"}], "formula": "<expression>",
  "output": {"label","unit","decimals"}}. Include the formula feature. The formula may
  use + - * / % ^, parentheses, and min max abs round floor ceil sqrt pow.
- If the app is a LIST OF THINGS THAT GET DONE (packing, chores, an opening routine),
  also add: "pattern": "checklist" and "progress": {"field": "<bool field>",
  "label": "done"}, and include the progress and toggle features.
- If the app records ONE NUMBER PER DAY (water, weight, mood, sleep), also add:
  "pattern": "tracker" and "tracker": {"field": "<numeric field>", "goal": <number>,
  "window": 7, "unit": "<short unit>"}, and include the derived and chart features.
- accent: a hex colour like "#7c9cff".
- done_means: two to four sentences. Each must name something a person can watch
  happen, using one of: shows, hides, saves, reloads, exports, imports, returns,
  refuses, blocks, counts, sorts, filters, deletes, restores, opens, prints, renders,
  persists, replaces. Never write "works as expected" or "as described".
- not: at least one thing the app refuses to do.

FEATURE CATALOGUE — the only features that exist
| id | what it does | needs |
|---|---|---|
| crud | create, read, update, delete records | - |
| search | find records by typing | crud |
| export | download JSON and CSV | crud |
| import | restore from a JSON file | crud |
| theme | dark and light, remembered | - |
| pwa | installable, offline manifest | - |
| tags | tag chips on each record | crud |
| filters | facet filter per select or tag field | crud, search |
| sort | sort by any column | crud |
| stats | count and summary strip | crud |
| reminder | due dates with an overdue flag | crud |
| print | print stylesheet | crud |
| i18n | a second language toggle | theme |
| backup | one-click full backup and restore | export, import |
| derived | streak, average and goal percent | crud |
| chart | inline sparkline, no library | crud, derived |
| progress | how many rows are done, as a count and a percentage | crud |
| toggle | tick a row without opening the form | crud |
| formula | one calculation over named inputs, no list, no storage | - |
| a11y | skip link, focus ring, live regions, reduced motion | - |
| feedback | a size warning and a backup reminder | crud |

FAILURE SECTION — required, one bullet each, no placeholders
- **bad input** — what happens when a value cannot be used, and what the user sees
- **no network** — what still works, and what it says about what does not
- **storage full** — whether the write fails loudly or the app degrades
- **corrupt state** — whether it refuses, resets, or recovers, and which

Write the document now. No commentary, no apology, no markdown outside the structure above.
```

---

## Worked example

Paste this as `specs/app-tea-log.md` after the model replies:

````markdown
# Tea Log

```json kiln
{
  "id": "app-tea-log",
  "name": "Tea Log",
  "tier": 1,
  "category": "utility",
  "pitch": "Which tea, how strong, and whether to buy it again.",
  "features": ["crud", "search", "tags", "export", "theme"],
  "entities": [
    {"name": "tea", "label": "Tea", "fields": [
      {"name": "title", "label": "Name", "type": "text", "required": true},
      {"name": "body", "label": "Notes", "type": "longtext"},
      {"name": "tags", "label": "Tags", "type": "tags"},
      {"name": "amount", "label": "Steep seconds", "type": "number"}
    ]}
  ],
  "storage": {"kind": "localstorage", "namespace": "tea-log"},
  "accent": "#c08b5c",
  "done_means": [
    "saving a tea and reloading the page shows the tea in the list",
    "typing a word no tea contains hides every row"
  ],
  "not": ["network calls", "accounts", "ratings out of five"]
}
```

## Pitch
…
````

Then:

```bash
python3 -m kiln adopt specs/app-tea-log.md
python3 -m kiln build specs/app-tea-log.md -o out
```

---

## If you have no model at all

| Path | Command |
|---|---|
| One sentence | `python3 -m kiln new "a tea log with tags and search"` |
| A form, on a phone | open `studio.html`, fill it, tap Build |
| A template | copy a spec from `specs/` and edit it |

All three produce the same document this prompt produces. The model is a
convenience, not a dependency.
