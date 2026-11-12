# Licensing

Three tiers for the compiler, and one rule that applies to all of them: **an app you generate is
yours**. What changes between tiers is the attribution inside the app, not your rights to it.

---

## What each tier puts in a generated app

| | `free` | `commercial` | `corporate` | `demo` (online only) |
|---|---|---|---|---|
| Cost | nothing | a written licence | a written licence | nothing |
| Features | all 14 | all 14 | all 14 | capped: crud, search, sort, theme |
| Sponsor block (UPI, Ko-fi, Sponsors, books) | yes | no | no | yes |
| Visible attribution | "Built with KILN", hyperlinked | one line in About: "Built with KILN" | none | "Built with KILN", hyperlinked |
| Build comment in the file | yes | yes | yes | yes |
| Build fingerprint | yes | yes | yes | yes |
| Export and import | yes | yes | yes | **no** |

The build comment stays in every tier. It names the compiler, the spec and the fingerprint —
it is evidence of origin, not an advertisement, and it is not visible to a user of the app.

---

## The free tier

Nothing to do. `kiln build` with no licence produces a free build.

| Inside the app | Where |
|---|---|
| Licence line, "Built with KILN" | About |
| UPI `drsohilboi@ybl`, GitHub Sponsors, Ko-fi, books | About |
| Fingerprint and spec id | About, plus the file's head comment |

Free builds are for personal, academic, hobby and non-profit use, under the PolyForm
Noncommercial licence in [`LICENSE`](LICENSE).

---

## The commercial tier

Buys one thing: the sponsor block disappears and the attribution shrinks to a single line.

| Inside the app | Where |
|---|---|
| `Built with KILN` — one line, hyperlinked | About |
| Nothing else about the author | — |

### How it works

| Step | Who | Command |
|---|---|---|
| 1 | owner, once | `kiln licence keygen` — writes `~/.kiln/private.key` (chmod 600) and pins the public key in `catalog/licence-key.json` |
| 2 | owner, per customer | `kiln licence issue --to "Acme Clinic Pvt Ltd" --tier commercial --days 365` |
| 3 | customer | `kiln licence activate KILN1.…` |
| 4 | customer | `kiln build specs/app-x.md` — the tier is picked up from the licence |

The key is Ed25519-signed and verified **offline**, with no packages and no network: the
compiler carries a small, tested implementation of the signature check. Expiry is enforced at
build time.

---

## The corporate tier

For a business that cannot carry anyone else's name in its product.

| Inside the app | Where |
|---|---|
| No About button at all | — |
| The build comment only, in the file's head | not visible to a user |

Issued exactly like the commercial tier, with `--tier corporate`.

---

## The demo tier

Not for sale and not selectable. It exists so the online demo can show a real app without
giving away the full one.

| Difference | Detail |
|---|---|
| Features | only `crud`, `search`, `sort`, `theme` survive |
| Export, import, filters, print, reminders | removed at build time, not hidden |
| Banner | the app says it is a demo build, on every load |

`demo.html` lists every spec in the repository and refuses to run the ones whose category is
`clinical` or `health` — a public page is the wrong place for a patient-data model.

---

## What this is, and what it is not

| It is | It is not |
|---|---|
| A clear statement of what a build carries | DRM |
| A signed licence that verifies offline | unbreakable |
| A fingerprint that shows a file was edited after it was built | encryption |
| A deterrent with an evidence trail | a technical control you can rely on |

The compiler is source-available. Anyone can edit it and remove the attribution. That is
stated here, in [`SECURITY.md`](SECURITY.md) and in [`COMMERCIAL.md`](COMMERCIAL.md), because
a licensing page that pretends otherwise is worse than no page.

What the fingerprint does give you: if a customer's build turns up modified, the file says so,
and the hash in the head comment can be checked against the spec it names.

---

## Buying a licence

Email **sohilmomin2000@gmail.com** with the subject `KILN commercial`. See
[`COMMERCIAL.md`](COMMERCIAL.md) for what to include.

There is no price list. The terms depend on whether the compiler ships to your customers or
only the generated apps.
