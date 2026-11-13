# Releases

**No releases are published until the owner says so.**

---

## The policy

| Rule | Detail |
|---|---|
| Who publishes | the owner, by hand |
| What a release needs | the owner's explicit instruction, in writing |
| What CI does | tests, verify, audit — and stops there |
| What a tag means right now | nothing. There are no published releases |

The reason is simple: a release is a promise about a version, and this compiler is still
changing fast enough that a version number would be a guess. The repository is the delivery
mechanism until that changes.

---

## What is true today

| Artifact | Available |
|---|---|
| Source | yes — clone the repository |
| Generated apps | yes — `kiln build` |
| The landing page and demo | yes — Pages, on `main` |
| Tagged releases, zips, binaries | **no** |
| EXE / APK builds | not wired |

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
