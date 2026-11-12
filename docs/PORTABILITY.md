# PORTABILITY — any OS, or just GitHub?

Short answer: **any OS, and GitHub is optional.**

---

## KILN itself

| Requirement | Detail |
|---|---|
| Python | 3.9 or newer |
| Packages | none. Standard library only |
| Network | none, for every command except `kiln llm` |
| Node | optional, used only to syntax-check emitted JavaScript |
| Git | optional, used only by `verify --at <sha>` and `preflight` |

| OS | Status |
|---|---|
| Linux | yes — the CI runner |
| macOS | yes — same interpreter, same code |
| Windows | yes — no shell scripts in the compiler path, no path assumptions beyond `pathlib` |
| WSL | yes |
| Android / iOS | no — a phone is not a build machine |

Run from a folder, a USB stick, or a checkout. There is nothing to install.

---

## The generated apps

| Host | Status | Note |
|---|---|---|
| Any browser, any OS | yes | one `index.html`, opened from disk |
| Windows | yes | plus EXE via `app-builder` |
| Android | yes | browser, home-screen install, plus APK via `app-builder` |
| iOS | yes | browser and home-screen install; no store build today |
| macOS / Linux desktop binary | not yet | gap, see below |
| A server | not needed | there is nothing to serve |

---

## GitHub's role

| Uses GitHub | Does not use GitHub |
|---|---|
| CI (tests, verify-all, audit) | writing a spec |
| Releases and artifacts | building an app |
| Pages, if you publish one | running an app |
| The estate's reusable workflows | verifying an app |

With no network and no GitHub account, `kiln new`, `compose`, `build` and `verify` all still work.

---

## The macOS / Linux desktop gap

| Option | Trade-off |
|---|---|
| Ship the folder + a one-line launcher | zero work, opens in the default browser |
| Tauri build | a real binary, needs a Rust toolchain in CI |
| Electron | simple, ~100 MB per app, against the estate's size ethos |
| Do nothing | honest: the browser is the runtime on every OS |

Default: do nothing for now. A single file that runs everywhere is a stronger
claim than three binaries that each need a build.

---

## Size budget

| Artifact | Target | Why |
|---|---|---|
| `index.html` | under 60 KB | fits on a floppy, opens instantly, emails fine |
| Whole app folder | under 100 KB | the estate's single-file ethos |
| KILN source | under 200 KB | a compiler small enough to read in an afternoon |
