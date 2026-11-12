# PORTABILITY — desktop, phone, Linux, or nothing at all

Short answer: **it runs anywhere, and it needs nothing from GitHub.**

---

## Three entry points, one result

| Entry point | Runs on | Needs | Produces |
|---|---|---|---|
| `python3 -m kiln` | Linux, macOS, Windows, WSL | Python 3.9+ | spec, app, zip |
| `studio.html` | any browser: Android, iOS, Windows, macOS, Linux | a browser | app file, spec file |
| a hand-written spec | anything that writes text | nothing | app, once built |

The Python CLI and the studio share the same catalogue and the same runtime
template — `kiln studio` generates the second from the first, and `kiln audit`
fails if they drift.

---

## The compiler

| Requirement | Detail |
|---|---|
| Python | 3.9 or newer |
| Packages | none, standard library only |
| Network | none |
| Node | optional, only to syntax-check emitted JavaScript |
| Git | optional, only for `verify --at <sha>` and `preflight` |
| Disk | under 1 MB for the whole folder |

| OS | Status |
|---|---|
| Linux | yes — the CI runner |
| macOS | yes — same interpreter, same code |
| Windows | yes — `pathlib` throughout, no shell dependency in the compiler path |
| WSL | yes |
| FreeBSD and other POSIX | expected to work, untested |

---

## The studio, on a phone

| Step | Detail |
|---|---|
| Get the file | email it to yourself, AirDrop, USB, or `kiln studio -o studio.html` |
| Open it | any mobile browser, from local storage |
| Use it | fill the form, tap Build, the app downloads |
| Install the result | open the downloaded `index.html`, *Add to Home Screen* |
| Network | none, at any point |

The studio is 50 KB and carries the catalogue and the runtime inside it. It has no
build step and no service worker, because a local file needs neither.

---

## The generated apps

| Host | Status | Note |
|---|---|---|
| Any browser, any OS | yes | one `index.html`, opened from disk |
| Windows | yes | plus EXE via your `app-builder` |
| Android | yes | browser, home-screen install, plus APK via `app-builder` |
| iOS | yes | browser and home-screen install; no store build today |
| macOS / Linux desktop binary | not yet | see the gap below |
| A server | not needed | there is nothing to serve |

---

## GitHub's role

| Uses GitHub | Does not use GitHub |
|---|---|
| CI: tests, verify-all, audit, studio drift | writing a spec |
| Releases and artifacts | building an app |
| Pages, if you publish one | running an app |
| Optional packaging workflow | verifying an app |

With no network and no account, `new`, `prompt`, `adopt`, `compose`, `build`,
`verify`, `studio` and `audit` all still work.

---

## The macOS / Linux desktop gap

| Option | Trade-off |
|---|---|
| Ship the folder + a one-line launcher | zero work, opens in the default browser |
| Tauri build | a real binary, needs a Rust toolchain in CI |
| Electron | simple, ~100 MB per app, against the estate's size ethos |
| Do nothing | honest: the browser is the runtime on every OS |

Default: do nothing for now. One file that runs everywhere is a stronger claim
than three binaries that each need a build.

---

## Size budget

| Artifact | Target | Actual |
|---|---|---|
| `index.html` (generated app) | under 60 KB | 21 KB |
| `studio.html` | under 80 KB | 50 KB |
| KILN source | under 400 KB | 210 KB |
| Whole repo with history | under 1 MB | 0.3 MB |
