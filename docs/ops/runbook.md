# Operations runbook: migrate, rollback, backup/restore

This runbook only documents what is actually implemented in `Makefile`,
`migrations/`, `scripts/`, and `database/` in this repository, as read
during a documentation closeout pass on 2026-09-23. Anything not directly
observed in those files is marked UNVERIFIED rather than assumed.

## Local database lifecycle

```bash
make env          # scripts/make_env.sh: writes .env with generated passwords (git-ignored)
make db-up        # docker compose -f database/docker-compose.yml up -d --wait db
                   # fails fast if .env is missing (Makefile db-up target)
make db-migrate   # alembic upgrade head, run as the migration role (MIGRATION_DATABASE_URL)
make run          # starts the API (STORAGE_BACKEND=sql picks up DATABASE_URL)
make db-down      # docker compose down
```

`database/docker-compose.yml` starts a single `postgres:16.4` container,
bound to `127.0.0.1:5432` only, with a named volume `db-data` for
persistence and `database/init/roles.sh` mounted as a compose
`docker-entrypoint-initdb.d` script. That script (read directly) creates
three roles on first container start: `ih_migrator` (owns the database),
`ih_app` (row-level DML only, via `ALTER DEFAULT PRIVILEGES ... GRANT
SELECT, INSERT, UPDATE, DELETE`), and `ih_readonly` (`USAGE` on schema
only; its actual table grants are applied later, in a migration, per the
script's own comment — this runbook does not know which migration without
reading `migrations/versions/*` individually beyond what was already
reviewed: `0003_reporting_grants.py` by its filename appears to be that
migration, but its contents were not read for this runbook — UNVERIFIED).

## Migrate

- Tool: **Alembic** (`alembic.ini`, `migrations/env.py`,
  `migrations/versions/`). Confirmed migrations present, in order:
  `0001_initial_schema.py`, `0002_indexes.py`, `0003_reporting_grants.py`,
  `0004_task_creation_order_index.py`, `0005_full_registration_profile.py`.
- Migrations are written by hand from `app/repositories/sql/models.py`
  (`migrations/README`, read directly): autogenerate a draft, then
  hand-correct it; constraint/index names are wrapped in `op.f()` so
  Alembic never renames them silently.
- Apply: `make db-migrate` (`alembic upgrade head`, using
  `MIGRATION_DATABASE_URL`, loaded from `.env` via the Makefile's
  `WITHENV` helper).
- Verify no drift: `make db-check` (`alembic check`, plus
  `tests/db/test_migrations.py -k "naming or alembic_check or types"`).
- Round-trip check (up/down/up on empty and seeded databases):
  `make db-roundtrip` (`tests/db/test_migrations.py -k "tc370 or tc371"`).
  This runbook did not execute this command; it only confirms the target
  exists and what it calls.

## Rollback a migration

Every revision is documented (in `migrations/README` and the standards
pack, FR-319/NFR-310) as having a working `downgrade`. Alembic's standard
rollback commands apply:

```bash
# roll back one revision
MIGRATION_DATABASE_URL=... uv run alembic downgrade -1

# roll back to a specific revision
MIGRATION_DATABASE_URL=... uv run alembic downgrade <revision>
```

There is no dedicated `make` target for a single-step rollback (only
`make db-roundtrip`, which exercises up/down/up as a test, not as an
operator command) — UNVERIFIED whether this is intentional or a gap; not
guessed further here.

## Backup

`make db-backup` runs `database/scripts/backup.sh` (read directly):

```bash
make db-backup
```

- Requires `BACKUP_DATABASE_URL` (the Makefile derives it from
  `MIGRATION_DATABASE_URL` via `scripts/libpq_url.sh`).
- Writes a compressed `pg_dump --format=custom --compress=9 --no-owner`
  file to `${BACKUP_DIR:-$HOME/.devdash-backups}` (outside the repository),
  with `umask 077`.
- The dump contains password hashes and personal data (script's own
  comment) — treat it as a secret, store it encrypted, and never commit it.

## Restore (verified)

`make db-restore-test` runs `scripts/restore_test.sh` (read directly):

```bash
make db-restore-test
```

- Dumps the running compose database (`pg_dump` inside the container, no
  host client tools needed).
- Creates a scratch database (`devdash_restore_$$`) and restores the dump
  into it with `pg_restore`.
- Compares a fingerprint per table (`users`, `projects`, `tasks`,
  `activity`): row count plus an `md5` of the comma-joined, id-ordered
  primary keys, source vs. restored.
- Exits non-zero and prints a diff on mismatch; cleans up the scratch
  database and temp dump directory on exit either way (`trap cleanup EXIT`).
- Documented recovery objectives (from the standards pack, section 8, not
  independently tested here): RPO 24 hours, RTO 1 hour, using daily dumps.

## Outage behaviour

Per the standards pack (NFR-312, not re-verified by running it in this
pass): `/readyz` should return 503 when the database is down, and the API
should recover without a restart once the database returns. This runbook
does not confirm this behaviour was exercised during this documentation
pass — UNVERIFIED.

## What this runbook does not cover

- Production deployment specifics beyond `render.yaml` and the README's
  "Deploying" section (not re-verified here).
- Point-in-time recovery (the standards pack notes a managed provider's
  PITR, if available, "tightens" the RPO figure above it — no such provider
  is configured in this repository).
- Any of this was not executed end-to-end during this pass; all commands
  above were confirmed to exist and read for their documented behaviour,
  not run.
