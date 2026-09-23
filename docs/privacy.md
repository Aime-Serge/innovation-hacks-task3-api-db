# Privacy: data map

A factual inventory of what personal data this repository stores and
processes, built by reading `app/domain/models.py`,
`database/docs/data-dictionary.md`, and `app/core/logging.py` directly. This
is not a legal privacy policy; it documents what is actually implemented.

## Tables holding personal data

| Table | Personal data fields | Notes |
| --- | --- | --- |
| `users` | `name`, `email`, `password_hash`, `avatar_url` (optional) | `email` is unique and used for login. `password_hash` is an argon2id hash (`app/core/config.py`: `ARGON2_TIME_COST`, `ARGON2_MEMORY_KIB`), never the plaintext password. `password_hash` is explicitly excluded from equality/repr on the `User` dataclass (`app/domain/models.py`, ADR-315) so it cannot leak through incidental logging of the object itself. The Task 3 registration profile block (`given_name`, `family_name`, `profile` JSON — see `app/domain/models.py` comment) is also personal data when populated. |
| `projects` | `owner_id` (FK to `users.id`) | Links a project to the person who owns it; no other personal fields on this table. |
| `tasks` | `assignee_id` (optional FK to `users.id`) | Links a task to the person assigned to it; no other personal fields on this table. |
| `activity` | `actor_id` (FK to `users.id`) | Records which user performed an action, for the audit trail. |

`projects.name`/`description` and `tasks.title`/`description` are
user-authored content, not identity data per se, but may incidentally
contain personal data if a user types it there; this repository applies no
special handling to that case beyond the standard length/format checks in
`database/docs/data-dictionary.md`.

## What is NOT collected

- No payment, financial, or government-ID data — no such fields exist in
  `app/domain/models.py`.
- No location, biometric, or device-fingerprint data.
- No analytics/tracking cookies (this is an API with no client-side session
  state beyond the bearer JWT).

## Logging

`app/core/logging.py` is explicit: "Never logs bodies, passwords or
tokens" (NFR-217, file header comment, read directly). Structured JSON logs
carry only the fixed field set `requestId, method, path, status,
durationMs, userId, errorType, fingerprint` — `userId` (a UUID) is logged,
but not `email`, `name`, or any request/response body. Slow queries are
logged "with a fingerprint and duration, never their values"
(`.env.example` comment on `DB_SLOW_QUERY_MS`, confirmed against
`app/core/config.py`).

## Backups

`database/scripts/backup.sh` produces a `pg_dump` that necessarily contains
the same personal data as the live tables (its own comment says so: "The
dump holds password hashes and personal data ... treat it as a secret").
Backups are written outside the repository, are git-ignored by construction
(written to `$HOME/.devdash-backups` by default), and are not committed.

## Third-party and AI data flows

Verified by `grep -rniE "openai|anthropic|third.?party|external.?api|webhook" app/`
during this pass: **no matches**. This repository makes no outbound calls to
any AI service or third-party API. The only external dependency in the
running system is the PostgreSQL database it owns (`DATABASE_URL`). No
personal data leaves this system boundary as implemented today.

## Data subject controls implemented in code

- Users can be read/updated via the documented `/api/v1/users/*` endpoints
  (see `docs/openapi.json` for the exact operations); this pass did not
  re-enumerate every endpoint's exact semantics here — see the OpenAPI
  document and Swagger UI (`/docs`) for the authoritative, generated list.
- No separate "export my data" or "delete my account" endpoint was found by
  this pass — if one exists it was not located in `app/api/v1/`;
  **UNVERIFIED / not confirmed present**, note as a gap rather than
  asserting it exists.

## Retention

No automated data-retention or deletion job was found in `Makefile`,
`scripts/`, or `database/scripts/` during this pass. Data persists until
explicitly deleted through the API or the database directly. This is a
factual gap, not a claim either way about whether one is required.
