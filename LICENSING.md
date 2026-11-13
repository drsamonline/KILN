# Editions

Two editions of the compiler. One rule under both: **an app you generate is yours**.

| | **Personal** | **Commercial** |
|---|---|---|
| Price | free | a written licence |
| Licence | PolyForm Noncommercial 1.0.0 | commercial, per agreement |
| Who it is for | personal, academic, hobby, non-profit use | businesses, paid work, products you sell |
| Features | all 14 | all 14, unlocked |
| Sponsor block in the app (UPI, Ko-fi, Sponsors, books) | **yes** | no |
| Author block in the app | **yes** | no |
| Compiler credit | "Built with KILN", hyperlinked | one line, "Built with KILN" |
| Build comment and fingerprint in the file | yes | yes |
| Available to try online | **yes** — the live demo | no |

There is no third edition, no per-seat tier and nothing to configure beyond these two.

---

## Personal edition

Free for personal use. Nothing to buy and nothing to activate.

| What it is | Detail |
|---|---|
| Command | `kiln build specs/app-x.md` |
| Needs a key | no |
| What lands in the app | a licence line, "Built with KILN", and an author block with the UPI id, GitHub Sponsors, Ko-fi and the books link |
| Where it appears | the app's **About** panel, plus a comment in the file's head |
| Features | all fourteen |
| Try it | [demo.html](demo.html) — a gallery of every spec, capped, with export switched off |

The author block is the price of the free edition. It is one panel, it is honest, and it is
how the compiler gets paid for when nobody is paying for it.

## Commercial edition

Buys one thing: the author block disappears and the credit shrinks to a single line.

| What it is | Detail |
|---|---|
| Command | `kiln licence activate KILN1.…` then `kiln build specs/app-x.md` |
| Needs a key | yes, issued by the owner |
| What lands in the app | one line in About: "Built with KILN", hyperlinked |
| Features | all fourteen, unlocked |
| Validity | checked at build time; an expired key falls back to Personal |

### How a key is issued

| Step | Who | Command |
|---|---|---|
| 1 | owner, once per machine | `kiln licence keygen` — private key to `~/.kiln/private.key` (chmod 600), public half pinned in `catalogue/licence-key.json` |
| 2 | owner, per customer | `kiln licence issue --to "Acme Clinic Pvt Ltd" --tier commercial --days 365` |
| 3 | customer | `kiln licence activate KILN1.…` |
| 4 | customer | `kiln build specs/app-x.md` — the edition comes from the licence |

Keys are Ed25519-signed and verified **offline**, with no packages and no network. The
signature check is a small, tested implementation in `kiln/ed25519.py`, checked against the
RFC 8032 vector in `tests/test_licence.py`.

---

## The demo is not an edition

`demo.html` is the Personal edition, capped, so it can sit on a public page.

| Difference | Detail |
|---|---|
| Features | only `crud`, `search`, `sort`, `theme` survive the build |
| Export and import | removed at build time, not hidden |
| Banner | the app says it is a demo build, on every load |
| Which specs run | all are listed; a spec whose category is `clinical` or `health` is refused, with the reason |

---

## What this is, and what it is not

| It is | It is not |
|---|---|
| A clear statement of what a build carries | DRM |
| A signed licence that verifies offline | unbreakable |
| A fingerprint that shows a file was edited after it was built | encryption |
| A deterrent with an evidence trail | a technical control you can rely on |

The compiler is source-available. Anyone can edit it and remove the author block. That is
stated here, in [`SECURITY.md`](SECURITY.md) and in [`COMMERCIAL.md`](COMMERCIAL.md), because
a licensing page that pretends otherwise is worse than no page.

What the fingerprint does give you: if a build turns up modified, the file says so, and the
hash in the head comment can be checked against the spec it names.

---

## Buying a licence

**On request.** There is no price list, and no checkout. Email
**sohilmomin2000@gmail.com** with the subject `KILN commercial`.

| What you tell me | What it changes |
|---|---|
| What you are building | the scope |
| Whether the compiler ships to your customers, or only the generated apps | redistribution terms |
| How many people would run it | seat count, if any |
| Whether it is a one-off project or an ongoing product | perpetual vs annual |
| Whether you need the author block gone, or just a licence to sell | which edition |

You get a written answer with a number in it, or an honest "this is not a fit". No sales
call, no trial that expires, no invoice before you have agreed a scope.

### What never changes with money

| Stays the same | Why |
|---|---|
| The compiler is the same code | there is no "pro" build with features held back |
| Generated apps are yours | the licence covers the compiler, not your work |
| The tests, the guards and the source stay visible | a licensed edition that you cannot inspect is a worse product |
| Personal use stays free | that is the point of the free edition |

---

## Releases

None are published until the owner says so. See [`RELEASE.md`](RELEASE.md).
