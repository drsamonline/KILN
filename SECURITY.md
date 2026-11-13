# Security policy

**Version** 1.0 · **Effective** 13 November 2026

---

## Reporting a vulnerability

**Please do not open a public issue for a security problem.**

| Channel | Detail |
|---|---|
| Email | sohilmomin2000@gmail.com — subject line `KILN security` |
| GitHub | [private vulnerability report](https://github.com/drsamonline/KILN/security/advisories/new) |
| What to include | the version or commit, what you did, what happened, and what you expected |

You will get an acknowledgement within a few days. There is no bounty and no formal SLA;
this is a single-maintainer project and honesty about that is better than a promise.

## Scope

| In scope | Why |
|---|---|
| The compiler (`kiln/`) | it writes files and reads specs |
| The runtime template (`templates/app/index.html`) | it renders user data in a browser |
| The studio (`studio.html`) | it handles pasted text and builds files in the browser |
| The verifier and guards | a guard that can be bypassed is a defect |

| Out of scope | Why |
|---|---|
| A generated app holding data you put in it | it is your app, on your device |
| `localStorage` being readable by other software on the same device | that is how browsers work |
| Anything a third-party model writes into a spec | `kiln adopt` validates it; it is not a trust boundary for content |
| Denial of service against your own machine by a huge spec | not a security property |

## What is already true, by design

| Property | How it is enforced |
|---|---|
| No network code in the compiler | no HTTP client is imported anywhere |
| No network code in a generated app | `verify` fails the build if `http://`, `https://`, `fetch(` or `XMLHttpRequest` appears |
| No external asset in a generated app | same check, plus no CDN, no fonts, no icons |
| User data is escaped before it reaches the DOM | one `esc()` helper, applied to every interpolated value |
| Nothing is silently skipped | a guard that cannot run reports `SKIP`, never `ok` |
| Specs are validated before they are written | `kiln adopt` refuses rather than emitting something broken |

## Known limitations, stated plainly

| Limitation | Consequence |
|---|---|
| Generated apps use `localStorage` | another page on the same origin, or a browser extension, could read it. Use a separate browser profile for sensitive data |
| The single HTML file is unsigned | verify where it came from before you open it |
| `kiln adopt` parses untrusted text | it parses JSON and validates it; it never executes it |
| No sandbox around a spec | a spec can only describe data, not code |

## Protection and watermark

This section states what is implemented, so it can be checked against the code. Anything not
built is not described here as if it were.

| Claim | Where it lives | Enforced by |
|---|---|---|
| Every build carries a build record: tier, compiler version, spec id, fingerprint | `const BUILD` in the emitted file | `verify` fails a build without it |
| The fingerprint is a hash of the model the file was built from | `compose.fnv1a64(canonical(model))` | `tests/test_licence.py` |
| The app recomputes the hash on boot and says so if it does not match | `tampered()` in the runtime | the app itself, visibly |
| A Personal build carries the sponsor and author block; Commercial carries one line | `licence.describe()` | `verify` checks sponsor presence against the edition |
| A paid tier cannot be selected without a valid key | `licence.resolve()` | the build refuses with an explanation |
| Keys are Ed25519-signed and verified offline, no packages | `kiln/ed25519.py` | RFC 8032 test vector in `tests/test_licence.py` |
| The private signing key never enters the repository | `~/.kiln/private.key`, chmod 600 | guard `C12` |

### What it is not

| Not this | Why not |
|---|---|
| DRM | the compiler is source-available; anyone can edit it and remove the attribution |
| Encryption of your app | the app is a plain HTML file by design |
| A guarantee of authorship | the fingerprint is evidence of a build, not proof of who holds the copyright |
| Tamper-proof | a determined edit can remove every marker; the point is that the file then disagrees with itself |

The honest summary: a build that has been modified will say so, and a customer build can be
checked against the spec it names. That is a deterrent and an evidence trail, and it is worth
having. It is not a lock.

## Supported versions

The `main` branch is the supported version. Fixes land there and are recorded in
[`CHANGELOG.md`](CHANGELOG.md).
