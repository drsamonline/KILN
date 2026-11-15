# Fleet specs

Three apps that already exist as their own repositories, written as KILN specs and
compiled. The point is not to replace them. It is to show that the compiler covers what
the fleet already ships, on real apps rather than on samples.

Every one of these builds with `python3 -m kiln build specs/fleet/<name>.md`.

---

## What is here

| Spec | Fleet repo | Archetype | Size |
|---|---|---|---|
| [`today-card.md`](../specs/fleet/today-card.md) | [today-card](https://github.com/drsamonline/today-card) | `journal` + `detail` | 53 KB |
| [`clinical-calc.md`](../specs/fleet/clinical-calc.md) | [bmi-bmr-tdee-macros-fluid-calculator](https://github.com/drsamonline/bmi-bmr-tdee-macros-fluid-calculator) | `calculator` | 53 KB |
| [`ntet-practice.md`](../specs/fleet/ntet-practice.md) | [ntet-homoeopathy-cbt](https://github.com/drsamonline/ntet-homoeopathy-cbt) | `quiz` | 54 KB |

All three verify, and `kiln verify --all` includes them: the repository now builds
**37 specs**, not 34.

---

## What each one proves

| Spec | The thing it proves |
|---|---|
| today-card | a dated journal with a read view is one archetype, not a bespoke app |
| clinical-calc | a formula belongs in the spec: changing the calculation is a spec change |
| ntet-practice | a question bank with a derived score needs no stored state |

---

## What each one does not do

| App | Missing from the spec version |
|---|---|
| today-card | the original's reminder, and its single-card home screen |
| clinical-calc | BMR, TDEE and the macro split: three more calculators behind tabs |
| ntet-practice | the syllabus browser, the timer and the 800-question bank |

Those are real features, not gaps in the compiler. A spec that needs them needs more
capabilities, and that is the honest next step rather than a claim that the fleet is
already absorbed.

---

## Why they are in the repository

| Reason | Detail |
|---|---|
| They are the absorption test | if a fleet app cannot be written as a spec, the compiler has a gap worth naming |
| They are real, not samples | each one names the repository it came from |
| They run in CI | `kiln verify --all` builds them on every push, so they cannot rot |
