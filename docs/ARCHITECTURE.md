# ARCHITECTURE

## The pipeline

```
 phrase / form / template
          |
          v
   intake  (kiln/intent.py)        deterministic: aliases, tf-idf, slot fill
          |
          v
   spec    (kiln/spec.py)          one JSON block + prose contract, schema checked
          |
          v
   compose (kiln/compose.py)       spec -> file plan, features closed over requires
          |
          v
   emit    (kiln/emit.py)          file plan -> files, refuses empty output
          |
          v
   verify  (kiln/verify.py)        reads the artifact, prints evidence, exits 1 on a defect
```

The LLM, when present, sits **beside** `intake` and may write only into `specs/`. It cannot write `out/`.

---

## Why this shape

| Property | How it is obtained |
|---|---|
| Deterministic | no randomness, no clock in the model, no dict iteration without ordering |
| No network | every import is stdlib; every runtime is inline |
| Testable | the compiler is a function from spec to files; the output is text |
| Replaceable parts | a template is one file; a feature is one catalog entry |
| Bounded | a feature that is not in the catalog cannot be requested |

---

## The layers

| Layer | Files | Rule |
|---|---|---|
| Contract | `SPEC-SHAPE.md`, `schema/spec.schema.json` | One shape. A second shape is an error |
| Catalog | `catalog/*.json` | A feature without an emitter and an assertion cannot exist |
| Compiler | `kiln/*.py` | No I/O except read spec, write files |
| Runtime | `templates/app/index.html` | One file. No external reference. Handles all four failure paths |
| Proof | `templates/app/smoke.py`, `kiln/verify.py` | Behaviour, not size |
| Guards | `kiln/guards.py` | One function per Forge defect |

---

## The generated app runtime

| Concern | Implementation | Why not a library |
|---|---|---|
| State | one array of rows in `localStorage` under `kiln:<namespace>` | a library would be a dependency the user cannot inspect |
| Forms | generated from `entities[].fields` | the field list is the only source of truth |
| Search | linear scan over declared fields | for a few thousand rows this is faster than an index and has no build step |
| Export | Blob + object URL, JSON and CSV | works offline, no server |
| Corruption | `JSON.parse` in try/catch, raw value copied to `:corrupt:` | a reset must never silently destroy data |
| Quota | `setItem` in try/catch, banner + export offer | the user must be told, not surprised |
| Offline | `navigator.onLine` listener, and no network code at all | the banner is a courtesy; the design is the guarantee |

---

## Extension points

| To add | Touch |
|---|---|
| A feature | `catalog/features.json` + a gate in the runtime + an assertion |
| A field type | `FIELD_TYPES` in `spec.py`, `fieldInput` and `readForm` in the runtime |
| An output format (EXE, APK) | a new entry in `compose.plan`, never a change to `emit` |
| A new stack | a second template directory; `compose` picks by `spec["target"]` when that key lands |

---

## What is deliberately absent

| Absent | Reason |
|---|---|
| A plugin system | the catalog is the plugin system |
| A database | the output is one file |
| A server | the thesis is offline |
| An agent loop | the failure class that produced Forge's 10 false completions |
