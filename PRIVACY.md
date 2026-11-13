# Privacy

**Version** 1.0 · **Effective** 13 November 2026 · **Owner** Dr Sohil Momin · **Applies to** the KILN compiler, `studio.html`, `index.html`, `demo.html` and every application they generate.

---

## The short version

KILN collects nothing. It has no analytics, no telemetry, no crash reporting, no accounts,
no cookies and no network code. Everything it does happens on the machine you run it on.

---

## What KILN itself does with data

| Question | Answer |
|---|---|
| Does it send anything anywhere? | No. There is no HTTP client in the compiler, and no `fetch` in the pages |
| Does it phone home on first run? | No |
| Does it create an account or identifier? | No |
| Does it read files outside the folder you run it in? | No. It reads `specs/`, `catalogue/`, `templates/` and writes where you tell it |
| Does it log what you do? | Only to `RUNS.jsonl` in the repository, on your own disk, and only build results |
| Does the prompt bridge call a model? | No. It prints text. You paste it wherever you choose |

## What the generated applications do with data

A generated app stores records in your browser's `localStorage`, under a key of the form
`kiln:<namespace>`. That data:

- stays on the device where you opened the file;
- is readable by anything else running on that device under the same browser profile;
- is never transmitted, because the app contains no network code;
- leaves only if you use **Export**, which writes a file you then control.

**To erase it:** open the app, delete the records you do not want, or clear site data for
that file in your browser. There is no server-side copy to delete, because there is no server.

## What happens when you use a model with the prompt bridge

KILN is not involved in that exchange. You copy a prompt into a service of your choosing,
under that service's terms and privacy policy. Whatever you type into it leaves your device
and goes to them, not to KILN. Read their policy before you paste anything sensitive.

## Personal data and Indian law

KILN is a local tool with no server, no accounts and no collection, so the obligations that
attach to a data fiduciary handling personal data do not arise in its ordinary use. If you
build an app that holds other people's data — a clinic log, for instance — **you** are the
one handling that data, on your own device, and the obligations are yours. No data leaves
the device unless you export it, and the export is a plain file you are responsible for.

This section states what the software does. It is not legal advice, and no compliance
conclusion should be drawn from it without your own counsel.

## Children

KILN is a developer tool and is not directed at children. It collects no data from anyone.

## Changes

Material changes to this policy will be recorded in [`CHANGELOG.md`](CHANGELOG.md) and the
version and effective date above will change in the same commit.

## Contact

Dr Sohil Momin — sohilmomin2000@gmail.com — or open an issue at
[github.com/drsamonline/KILN/issues](https://github.com/drsamonline/KILN/issues).
