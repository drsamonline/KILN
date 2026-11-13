# Guide — contributing a feature or an archetype

> **TL;DR** — five touches for a capability, six for an archetype, and the build fails if
> any is missing. One archetype per pull request, never two.

---

## The five touches for a capability

| # | Touch | File | Checked by |
|---|---|---|---|
| 1 | register it | `catalogue/capabilities.json` — id, label, aliases, requires, kit, **assertion** | `catalog.load()` |
| 2 | list it in the prompt | `PROMPT.md`, the catalogue table | guard `B6` |
| 3 | gate the runtime | `templates/app/index.html`, wrapped in `/* @only <id> */ … /* @end only */` | emit strips it when unused |
| 4 | add a verify check | `kiln/verify.py`, `if "<id>" in model["features"]` | the check runs on every build |
| 5 | add a test | `tests/`, including the emitted JavaScript run under node where there is maths | CI |

Then:

```bash
python3 -m kiln studio && python3 -m kiln demo     # the pages embed the template
python3 -m kiln audit --write                      # refresh the index
python3 -m unittest discover -s tests
python3 -m kiln audit
```

## The six touches for an archetype

| # | Touch | File |
|---|---|---|
| 1 | descriptor | `catalogue/patterns/<id>.json` — requires, defaults, pros, cons, best_for, avoid_if |
| 2 | sample spec | `specs/gallery/<id>.md` |
| 3 | screenshot | `docs/gallery/<id>.png`, rendered from the built sample |
| 4 | block + seed row | `docs/PATTERNS.md` |
| 5 | recipe | `GUIDE-COOKBOOK.md` |
| 6 | test | `tests/test_<id>.py` — builds, verifies, under 40 KB, and the maths under node |

## The checklist a reviewer runs

- [ ] the capability has an assertion a person could watch happen
- [ ] the capability has an entry in the registry if it introduces a field type
- [ ] the emitted app is under 40 KB (`tests/test_calculator.py::TestSizeBudget`)
- [ ] unused code is inside `@only` markers, so a spec that does not need it does not ship it
- [ ] the two generated guides are current (`python3 -m kiln guide --check`)
- [ ] `PROMPT.md` lists the capability
- [ ] no new dependency — `python3 -m kiln doctor` still shows none
- [ ] determinism holds: two builds, one hash

## What will be declined

| Proposal | Why |
|---|---|
| a dependency | the value is zero dependencies |
| a second archetype in one PR | §5 |
| an emitted feature with no assertion | it cannot be verified |
| a `planned` entry quietly emitted | the registry would lie |
| `eval` or `new Function` in a generated app | the calculator's parser exists so this never happens |
| a feature outside the catalogue | a bounded catalogue is what makes the output reliable |

## Links

- [`CONTRIBUTING.md`](CONTRIBUTING.md) — the inbound licence grant and the four CI steps
- [`docs/PATTERNS.md`](docs/PATTERNS.md) — the archetype template
- [`AUDIT-FORGE.md`](AUDIT-FORGE.md) — why the guards exist
