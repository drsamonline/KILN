# Disclaimer

**Version** 1.0 · **Effective** 13 November 2026

KILN is a compiler. It turns a specification into software. It does not know what you are
building, and it cannot tell whether the result is right for you.

---

## 1. Generated software is not reviewed

| Fact | Consequence |
|---|---|
| A generated app is produced from your spec by a template | it does what the template does, which is a fixed and small set of behaviours |
| KILN verifies wiring, references and behaviour assertions | that is a floor, not a review |
| Nothing checks whether your spec describes the right app | only you can |

Test a generated app with your own data before you depend on it. Especially before it holds
data you cannot recreate.

## 2. Specifications written by a model

`kiln adopt` accepts a document a model wrote and repairs it until it validates. That
guarantees the document is **structurally** valid. It does not guarantee that it describes
what you asked for. Read the spec before you build from it.

No model is called by KILN, and no output of a model is endorsed by KILN.

## 3. No professional advice

Nothing in this repository, its documentation, its examples or its generated apps is
medical, legal, financial, safety or psychological advice.

| Domain | What that means |
|---|---|
| Clinical use | a generated clinic log is a form and a list. It is not a medical device, it has no clinical decision support, and it is not a record of legal standing |
| Health data | if you put patient data into an app, you are the one handling it. See [`PRIVACY.md`](PRIVACY.md) |
| Legal use | a generated app is not a compliance control |
| Financial use | no calculation in any generated app has been audited |
| Safety-critical use | do not. There is no failsafe, no redundancy and no certification |

If you build for a regulated domain, get the app reviewed by someone qualified in that
domain, and write your own disclaimers into your own app.

## 4. Data durability

A generated app stores data in the browser's `localStorage` on one device.

| Risk | Reality |
|---|---|
| Clearing site data deletes everything | yes, with no copy anywhere |
| A private window loses it on close | yes |
| A different browser sees different data | yes |
| A corrupt value resets the store | the app keeps the bad value aside under a `:corrupt:` key, but it does not repair it |

Use **Export** regularly. That is the backup story, and it is deliberately manual.

## 5. No warranty, no liability

KILN is provided as is, without warranty, and the author is not liable for damages arising
from its use. The full text is in [`TERMS.md`](TERMS.md) sections 4 and 5.

## 6. If something in a generated app is wrong

Open an issue with the spec, the command and the output. A defect in the template is a real
bug and will be fixed. A defect in your spec is yours, but it is worth reporting anyway , 
it usually means the catalogue is missing something.
