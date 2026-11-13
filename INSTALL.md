# Install

There is no installer, because there is nothing to install.

---

## What you need

| Requirement | Detail |
|---|---|
| Python | 3.9 or newer — for the command line |
| A browser | for `studio.html`, and for running any generated app |
| Disk | under 1 MB |
| Packages | none |
| Network | none |

Check what you have:

```bash
python3 -V
python3 -m kiln doctor
```

---

## Get the files

```bash
git clone https://github.com/drsamonline/KILN.git
cd KILN
```

No git? Download the ZIP from the repository page and unpack it. Same folder, same result.

---

## Per platform

| Platform | Command | Note |
|---|---|---|
| Linux | `python3 -m kiln doctor` | python3 is usually present |
| macOS | `python3 -m kiln doctor` | the system python3 works |
| Windows | `python -m kiln doctor` | use `py -3` if `python` is not on PATH |
| WSL | `python3 -m kiln doctor` | same as Linux |
| Android / iOS | open `studio.html` | no Python needed |
| Any machine with no Python | open `studio.html` | the whole builder is one file |

There is no `pip install`, no virtualenv requirement, no PATH change, no service to start.

---

## Verify the install

```bash
python3 -m unittest discover -s tests     # 291 tests
python3 -m kiln verify --all              # every spec builds
python3 -m kiln audit                     # 268 guards
```

All three should pass on a clean checkout. If `node` is absent, one check reports `SKIP`
rather than passing — that is deliberate, and it does not fail the run.

---

## Optional extras

| Extra | Enables | Without it |
|---|---|---|
| `node` | syntax-checking emitted JavaScript | that one check reports `SKIP` |
| `git` | `verify --at <sha>`, `preflight` | those two commands are unavailable |
| `shellcheck` | the shell lint guard | that guard reports `SKIP` |

---

## Put it on a phone

| Step | Detail |
|---|---|
| 1 | copy `studio.html` (50 KB) to the phone — email, AirDrop, USB, a local server |
| 2 | open it from local storage in the browser |
| 3 | fill the form, tap **Build app** |
| 4 | open the downloaded file, then *Add to Home Screen* |

No app store, no account, no network at any step.

---

## Uninstall

Delete the folder. There is no registry entry, no service, no config outside the folder,
and nothing written to your home directory. Generated apps and their data live where you
put them, and in your browser's storage for that file.
