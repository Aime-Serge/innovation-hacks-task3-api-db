# Security Policy

## Supported versions

Only the latest commit on `main` is supported. There are no maintained release
branches; the tags `task-2-baseline` and `task-3-submission` are historical
submission snapshots for the Innovation Hacks internship, not supported
releases.

| Version | Supported |
| --- | --- |
| `main` (latest) | Yes |
| Anything else (including the submission tags) | No |

## Reporting a vulnerability

Please do not open a public GitHub issue for a suspected security
vulnerability.

Instead, report it privately to: <set-me>

Include, where possible:

- A description of the vulnerability and its potential impact
- Steps to reproduce, or a proof of concept
- The affected commit or tag

You should receive an acknowledgement within a reasonable time. There is no
formal SLA for this project, since it is a training/internship codebase
(<set-me> to fill in an actual response-time commitment if this repo starts
handling real user data).

## Scope notes specific to this repository

This project stores credentials only via environment variables
(`.env`, never committed) and the PostgreSQL data layer described in
`docs/standards/task3-standards-pack.md` (see section 9, "Data security and
threat model", and section 8, "Configuration, migrations and operations").
Known, already-documented limitations are listed in `README.md` under
"Known limitations" and are not necessary to report again (for example: the
in-process rate limiter, hard deletes, non-revocable tokens).

## Secret scanning

This repository is intended to be scanned with
[gitleaks](https://github.com/gitleaks/gitleaks) (see `make secrets` and
`make db-security` in the `Makefile`). Gitleaks was **not** run as part of
this documentation pass because it is not installed in that environment; if
you are verifying this policy, run `make secrets` or `gitleaks detect` before
relying on this document's guarantees.
