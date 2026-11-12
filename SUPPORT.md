# Support

KILN is maintained by one person. Support is honest about what it is: careful replies,
no service-level agreement, and a strong preference for issues that come with the command
you ran and the output you got.

---

## Where to go

| You need | Go to | Response |
|---|---|---|
| A bug report | [new issue](https://github.com/drsamonline/KILN/issues/new/choose) | usually within a few days |
| A question, or an idea | [discussions](https://github.com/drsamonline/KILN/discussions) | when there is time |
| A security problem | [SECURITY.md](SECURITY.md) — privately | acknowledged within days |
| A commercial licence | [COMMERCIAL.md](COMMERCIAL.md) | a real answer, with a price if there is one |
| Something about another project in the estate | [drsamonline](https://github.com/drsamonline) | that project's own issues |

## What makes a good report

Paste these four things and the reply is usually a fix rather than a question:

```bash
python3 -m kiln doctor
python3 -m kiln audit
# the command you ran, verbatim
# the output you got, verbatim
```

Plus the spec itself, if the problem is in a build. A spec is one file and it is the whole
input — there is nothing else to guess at.

## What support is not

| Not offered | Why |
|---|---|
| A guaranteed response time | one maintainer, and promises that cannot be kept are worse than none |
| Help designing your app | the catalogue is the design space; `kiln catalog` lists it |
| Debugging a model's output | `kiln adopt` reports every repair it makes — that report is the answer |
| Recovery of data from a cleared browser | there is no copy to recover from |
| Legal or clinical review of what you build | see [`DISCLAIMER.md`](DISCLAIMER.md) |

## Support the project

| Shape | Cost |
|---|---|
| Use it and report what broke | free, and the most useful |
| Star the repository | free |
| Tell one person who builds small tools | free |
| Translate the docs or a spec into another language | your time |

### Money, if you want to

| | |
|---|---|
| UPI (India) | `drsohilboi@ybl` — payee Dr Sohil Momin, open amount, or scan [the QR](docs/assets/upi-qr.svg) |
| GitHub Sponsors | [github.com/sponsors/drsamonline](https://github.com/sponsors/drsamonline) |
| Ko-fi | [ko-fi.com/matneo](https://ko-fi.com/matneo) |
| PayPal | [paypal.me/drsohilmomin](https://paypal.me/drsohilmomin?locale.x=en_GB&country.x=IN) |
| My books | [Amazon author store](https://www.amazon.com/stores/author/B08ZT331LY/allbooks?ccs_id=aed72b9f-71d9-41dc-adee-e9368a317acc) |
| More apps | [drsamonline.github.io](https://drsamonline.github.io/) |

A donation buys no priority, no support window and no influence over the roadmap. It buys
the time to keep the tests green, and nothing else is promised.
