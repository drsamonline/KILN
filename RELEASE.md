# Releases

**Releases are published on the owner's instruction.** The first is `v1.0.14`, on
2026-11-14.

---

## The policy

| Rule | Detail |
|---|---|
| Who publishes | the owner, by hand |
| What a release needs | the owner's explicit instruction, in writing |
| What CI does | tests, verify, audit, status page, status feed — and stops there |
| What a tag means | the tree that passed every gate, published under a version |

The policy was written when the compiler was changing daily and a version number would have
been a guess. It has since settled: 24 archetypes, 50 capabilities, 33 specs and 566 tests,
all green. The owner released `v1.0.14` on 2026-11-14.

---

## What is true today

| Artifact | Available |
|---|---|
| Source | yes — clone the repository |
| Generated apps | yes — `kiln build` |
| The landing page and demo | yes — Pages, on `main` |
| Tagged releases, source zip | **yes — `v1.0.14`** |
| **The apps themselves, pre-built** | **yes — `KILN-apps-1.0.14.zip`, 33 apps and an index** |
| The studio as one file | yes — `studio-1.0.14.html` |
| Printable changelog | yes — attached to the release, and at `docs/changelog.html` |
| EXE / APK builds | not wired |

---

## Published releases

| Version | Date | Assets | What it was |
|---|---|---|---|
| v1.0.14 | 2026-11-14 | source zip, **33 built apps**, studio, printable changelog | the 24-archetype catalogue complete, the handover written, every gate green |

### What each asset is for

| Asset | Who it is for | What to do with it |
|---|---|---|
| `KILN-1.0.14.zip` | anyone building their own | unzip, `python3 -m kiln build spec.md` |
| `KILN-apps-1.0.14.zip` | anyone who just wants the apps | unzip, open `index.html`, click an app. No Python, no server |
| `studio-1.0.14.html` | anyone who wants to build without a terminal | open it in a browser, pick capabilities, download the app. Works on a phone, offline |
| `KILN-changelog.pdf` | anyone checking the history | 22 A4 pages, every version |

---

## When the owner says go

| Step | Command |
|---|---|
| 1 | bump `__version__` in `kiln/__init__.py` and `MANIFEST.json` |
| 2 | add the `CHANGELOG.md` entry |
| 3 | `python3 -m unittest discover -s tests` and `python3 -m kiln audit` |
| 4 | `git tag vX.Y.Z && git push origin vX.Y.Z` |
| 5 | `gh release create vX.Y.Z <zip> --title … --notes …` |
| 6 | update the version table here |

Until step 1 happens by instruction, none of the rest does.
