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
been a guess. It has since settled: 30 archetypes, 50 capabilities, 33 specs and 574 tests,
all green. The owner released `v1.0.14` on 2026-11-14.

---

## What is true today

| Artifact | Available |
|---|---|
| Source | yes — clone the repository |
| Generated apps | yes — `kiln build` |
| The landing page and demo | yes — Pages, on `main` |
| Tagged releases, source zip | **yes — `v1.0.14`** |
| Printable changelog | yes — attached to the release, and at `docs/changelog.html` |
| EXE / APK builds | not wired |

---

## Published releases

| Version | Date | Commit | What it was |
|---|---|---|---|
| v1.0.14 | 2026-11-14 | first release | the 30-archetype catalogue complete, the handover written, every gate green |

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
