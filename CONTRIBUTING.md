# Contributing

This repository is the Task 3 (PostgreSQL persistence layer) submission of the
Innovation Hacks Full Stack Development Internship, built on top of Task 2.
It follows the *Persistent Data Layer Engineering Standards Pack (Task 3)*
(`docs/standards/task3-standards-pack.md`) and the Task 2 pack it extends.

## Setup

You need [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 for you).

```bash
uv sync --frozen                                                                 # 1. install
export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')  # 2. configure
SEED_PROFILE=default uv run uvicorn app.main:create_app --factory --reload       # 3. run, with demo data
```

This starts the API against the in-memory backend. To work against PostgreSQL:

```bash
make env          # writes .env with freshly generated passwords (git-ignored)
make db-up        # starts PostgreSQL 16 in Docker and creates the three roles
make db-migrate   # applies the Alembic migrations
make run          # starts the API against STORAGE_BACKEND=sql
```

See `README.md` ("Configuration", "Database") for the full environment
variable reference, and `.env.example` for every variable with placeholders.

## Database migrations (Alembic)

This repository uses **Alembic** for schema migrations (`migrations/`,
`alembic.ini`). Per `migrations/README`:

- Migrations are written by hand from `app/repositories/sql/models.py`
  (BR-310 in the standards pack): autogenerate a draft, then read and correct
  it by hand.
- Every revision must have a working `downgrade`.
- Constraint and index names follow the naming convention baked into
  `models.py` and are wrapped in `op.f()` so Alembic never silently renames
  them.
- A model change and its migration belong in the same commit.

Commands:

```bash
make db-migrate     # alembic upgrade head, as the migration role
make db-check       # alembic check + naming/type tests
make db-roundtrip   # up, down, up again on an empty and a seeded database
make db-docs        # regenerate database/docs/erd.mmd and data-dictionary.md
```

## Commit convention

Commits in this repository's history follow Conventional-Commits-style
`type(scope): description`, for example (from `git log`):

```
feat(api): registration may set role=lead, defaults to developer
fix(web): the landing page said Task 2, held in memory, and linked the wrong repo
docs(docs): add the Task 4 handoff notes ...
test(db): check each unset compose secret on its own ...
perf(db): count large lists only when the page is full ...
```

Scopes used in the standards pack for Task 3 work: `db`, `env`, `docs`,
`deploy`. Commit file-by-file in logical groups rather than one large
changeset.

## Pull request process

Per the standards pack (section 12, "Pull request definition of done"):

- List the requirement IDs (`FR-3##`, `NFR-3##`, `BR-3##`) the change touches.
- Include the migration and make sure it is reversible, if the schema
  changed.
- Regenerate the ERD and data dictionary (`make db-docs`) if the schema
  changed.
- Add or update tests.
- `docs/openapi.json` is unchanged, or the diff is explained
  (`make spec-check`, `make spec-diff`).
- Update `README.md` if setup changed.
- Tick the relevant Standards Gate items (`docs/standards/task3-standards-pack.md`,
  section 11).

## Definition of done

A change is done when:

1. `make gate` passes locally (lint, types, layers, tests, spec checks,
   contract tests, security, postman, load, and `make db-gate` for anything
   touching the data layer).
2. Requirement IDs are referenced in the commit message or PR description.
3. Tests were added or updated for the behaviour that changed.
4. Documentation (`README.md`, ADRs under `docs/adr/`, generated DB docs)
   reflects the change.
5. No product code change ships without a passing gate; no secret is
   committed (`.env` stays git-ignored, `.env.example` holds placeholders
   only).

## Architecture Decision Records

Non-trivial or non-obvious decisions are recorded as ADRs in `docs/adr/`
(see `docs/adr/README.md` for the index). Add a new `ADR-NNN-slug.md` file
for a new decision rather than editing history in place.

<!-- TODO(human): add anything project-specific to your workflow here (e.g. a
     preferred review turnaround, required reviewers, or CI quirks) that
     wasn't already captured in the standards pack. -->
