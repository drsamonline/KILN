# Handover

Written 2026-11-14 at v1.0.14. This file is for whoever picks the repository up next,
human or model. It says where things are, what is true, and what is deliberately not done.

---

## State, measured

| Gate | Result |
|---|---|
| `kiln audit` | **455 guards, 0 failed**, 1 skipped (shellcheck, when the machine lacks it) |
| `kiln verify --all` | **33 specs, 0 failing** |
| `python3 -m unittest discover -s tests` | **566 tests, OK** |
| CI | **10 jobs, all green** |
| Releases and tags | **zero**, by policy in [`RELEASE.md`](RELEASE.md) |
| Largest generated app | 57 KB, against a 100 KB ceiling |
| `kiln report --json` | `ok: true` |

Reproduce all of it with one command: `python3 -m kiln report`.

---

## The five things to know first

1. **There are no dependencies.** Python 3.9+ standard library, and Node only for the tests
   that run extracted JavaScript. Do not add a package; the self-containment is the product.
2. **The output is one file.** A generated app is one `index.html`. No build step, no assets,
   no network, ever.
3. **`@only` markers are load-bearing.** `templates/app/index.html` is sliced per capability
   at emit time by a line scanner with a stack, in `kiln/emit.py`. Read that function before
   touching the template.
4. **Guards are the contract.** `kiln/guards.py` holds 455 checks that encode every mistake
   this project has made. A guard is cheaper than a paragraph of documentation.
5. **Do not hand-maintain a number.** Counts, sizes, the changelog page, the status page and
   the badge are all generated and guarded. If a number is in a document, a command wrote it.

---

## Where everything lives

| Path | What it is |
|---|---|
| `kiln/` | the compiler: `spec`, `catalog`, `intent`, `compose`, `emit`, `verify`, `guards`, `cli` |
| `templates/app/index.html` | the single-file runtime, sliced per capability |
| `templates/studio/index.html` | the browser builder, 209 KB, one file |
| `templates/demo/index.html` | the gallery, 355 KB, 33 specs listed, 4 run live |
| `catalogue/` | 50 capabilities, 84 registry entries, 24 pattern descriptors |
| `specs/gallery/` | 30 working specs, one per archetype |
| `tests/` | 566 tests; `tests/_extract.py` pulls a JS function out by boundary |
| `docs/status.html` | every gate, measured. `kiln report --write` |
| `docs/changelog.html` | every version, print-ready. `kiln changelog --write` |
| `docs/badge.json` | shields endpoint. `kiln report --badge` |
| `status` branch | `status.json`, republished by CI on every push to main |

---

## The bug classes, and the guard that stops each

| Class | How it appeared | Guard |
|---|---|---|
| a name used by a capability that does not declare it | the app rendered blank, four times | **C18** |
| a derived figure computed inside the row loop | 1000 rows took 1198 ms | **C19** |
| a stated size that drifted | the README claimed 21 KB for a 50 KB app | **C20** |
| a generated page that went stale | the printable changelog | **C21** |
| an em dash used as a connector | 77 of them across 30 documents | **C22** |
| a status page from an older version | — | **C23** |
| a hand-maintained badge | said 452 when the count was 455, twice | **C24** (tests, not audit) |
| a capability declared without its block | a spec built with a missing feature | `spec.py` validation |
| shared CSS gated to one capability | cards rendered unstyled | base CSS, not `@only` |

---

## Rules that were learned the hard way

- **Never `str.replace` on a code fragment that appears twice.** Verify uniqueness first, or
  the change lands in the wrong function.
- **A guard cannot judge two files it also generates.** C24 lives in the tests for that reason.
- **A generated file must contain nothing that changes when it is committed.** No commit hash,
  no commit count, no clock.
- **Do not ask CI to prove something machine-dependent.** The status page records skips, and a
  skip depends on what the machine has.
- **A test that asserts the wrong thing is worse than no test.** When a test and the code
  disagree, decide which is right and say so in the commit.

---

## What is deliberately not done

| Not done | Why |
|---|---|
| No GitHub release or tag | [`RELEASE.md`](RELEASE.md): the owner publishes, not the build |
| No pinned licence key committed | an orphan public key would lock every customer out. Run `kiln licence keygen` and commit `catalogue/licence-key.json` yourself |
| No network, no telemetry, no model call | the whole point |
| No third-party action in CI | every `uses:` is version-pinned; publishing uses plain `git` |
| `crypto` capability absent | the fleet's four encrypted apps implement AES-GCM separately. This is the top candidate for the next batch |

---

## The next three things worth doing

1. **`crypto` as a capability.** AES-256-GCM at rest, one implementation instead of four. It
   needs a new field type or a `crypto` block, a guard, and a spec. The fleet repos that hold
   it today: `app-encrypted-case-log`, `seance`, `lockhtml`.
2. **`specs/fleet/`.** Three fleet apps were rebuilt as specs on 2026-11-14 and all three
   compiled: `today-card`, the BMI calculator, and the NTET quiz. They are not in the
   repository yet. Adding them proves the absorption path on real code.
3. **The fleet index.** Every generated app in one page, installable as a PWA. The pieces
   exist in three repos; nothing joins them.

---

## Reading order for a new contributor

1. [`GUIDE-QUICKSTART.md`](GUIDE-QUICKSTART.md) — five minutes, one command.
2. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — how a spec becomes a file.
3. [`GUIDE-CONTRIBUTE.md`](GUIDE-CONTRIBUTE.md) — the five touches for a capability.
4. [`docs/PATTERNS.md`](docs/PATTERNS.md) — every archetype, with pros and cons.
5. [`AUDIT-FORGE.md`](AUDIT-FORGE.md) — why the guards exist.
