# Guide — licensing

> **TL;DR** — two editions. **Personal** is free under PolyForm Noncommercial and puts your
> sponsor block and author line inside every app it generates. **Commercial** is paid, and
> replaces all of that with one line: *Built with KILN*.

---

## The two editions

| | **Personal** | **Commercial** |
|---|---|---|
| Price | free | a written licence |
| Licence | PolyForm Noncommercial 1.0.0 | commercial, per agreement |
| Use | personal, academic, hobby, non-profit | business, paid work, products you sell |
| Sponsor block in the app | **yes** | no |
| Author line in the app | **yes** | no |
| Compiler credit | "Built with KILN", hyperlinked | one line, "Built with KILN" |
| Features | all of them | all of them |
| Needs a key | no | yes |

The full table, and what counts as commercial, is in [`LICENSING.md`](LICENSING.md).

## Using the personal edition

Nothing to do. It is the default:

```bash
python3 -m kiln build specs/app-notes.md -o out
python3 -m kiln licence            # edition  personal  (default)
```

The generated app carries an About panel with the licence line, the sponsor block and the
build fingerprint. That is the trade: the app is free, and it says who made the compiler.

## Using the commercial edition

The owner issues a key; you activate it once:

```bash
# the owner, once: a signing key, and the public half pinned in the repo
python3 -m kiln licence keygen

# the owner, per customer: a key for a named licensee and a term
python3 -m kiln licence issue --to "Test Clinic" --days 365

# the customer, once
python3 -m kiln licence activate KILN1.eyJleHBpcmVzIjoi…

# then every build is commercial
python3 -m kiln licence status     # edition  commercial  (licence)
python3 -m kiln build specs/app-notes.md -o out
```

Once a key is active, `build` is commercial **by default**. Pass
`--tier personal` to build the free edition again without deactivating.

`build --tier commercial` without a valid key is refused, and says why.

## What a key is, and is not

| Is | Is not |
|---|---|
| an Ed25519 signature over the licensee, the edition and an expiry | a phone-home check |
| verified offline, in 0.07 s, with no packages | proof the key was not shared |
| pinned to a public key you commit once | a secret that has to travel with the app |

A key is a licence document, not DRM. The source is readable, so a determined person can edit
it; the point is that an honest customer has a clean way to comply, and a generated app can
prove where it came from.

## Checking what a build will carry

```bash
python3 -m kiln explain specs/app-notes.md          # pattern, capabilities, size
python3 -m kiln licence tiers                       # the table above, from code
```

## Common mistakes

| Message | Fix |
|---|---|
| `a commercial build needs a licence` | `kiln licence activate <key>`, or build `--tier personal` |
| `no key pinned` | the owner runs `kiln licence keygen` once and commits `catalogue/licence-key.json` |
| `key is expired` | ask for a new key; the expiry is in the payload |
| the About panel is missing | the build is commercial: its About panel is one line, deliberately |
| `build` is suddenly commercial | a key is active. `kiln licence status` says so; `--tier personal` overrides it |

## Links

- [`LICENSING.md`](LICENSING.md) — the editions, in full
- [`COMMERCIAL.md`](COMMERCIAL.md) — what a commercial licence covers
- [`TERMS.md`](TERMS.md) — the terms both editions sit under
- [`PRIVACY.md`](PRIVACY.md) — nothing is collected, in either edition
