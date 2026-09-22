# Demo script: Task 3 database integration (about 4 minutes)

Record the screen with the terminal on the left and the browser (Swagger UI) on the right. Say the
line in quotes, then do the action.

## Set up before recording

```bash
make env          # writes .env with freshly generated passwords (git-ignored)
make db-up        # PostgreSQL 16 in Docker, three roles created
make db-migrate   # applies the migrations
python -m app.seed --profile default --reset --yes
make run
```

Open http://127.0.0.1:8000/docs in the browser. The demo password lives only in your shell.

## 1. The database, not just the API (40 s)

"Task 2 kept everything in memory. Task 3 replaces that with PostgreSQL, and the API contract does
not change — the Task 1 dashboard and every Task 2 test still pass against it."

- Show `database/docs/erd.mmd` rendered, or `database/docs/data-dictionary.md`: four tables, six
  foreign keys with deliberate delete rules, and the constraints the database itself enforces
  (lengths, enums, a unique lower-case email, `completed_at` set exactly when a task is `done`).

## 2. Migrations, not a hand-run script (45 s)

"Schema changes are Alembic migrations, written by hand and reviewed, each with a downgrade."

In the terminal:

```bash
make db-check     # alembic check: naming rules and column types match the models
```

"The gate runs every migration up, down and up again, on an empty database and on a seeded one,
before it's trusted."

## 3. Data survives a restart (50 s)

"This is the part memory storage couldn't do."

- **POST /api/v1/projects**, then **POST /api/v1/tasks** in Swagger UI. Note the id.
- Stop the API (`Ctrl-C`), restart it with `make run`, no reseed.
- **GET /api/v1/tasks/{taskId}**: the same task, same id, still there.

## 4. Roles, not one shared login (45 s)

"The API connects as `ih_app`, which can read and write rows but cannot alter the schema. A
separate role, `ih_migrator`, owns the schema and is the only one `make db-migrate` uses. Neither
role, and no connection string, is hard-coded anywhere in the repository — everything comes from
the environment, and the app refuses to start without it."

- Show `.env.example`: `DATABASE_URL`, `MIGRATION_DATABASE_URL`, each a placeholder.
- Optional: `make secrets` (gitleaks) returning clean.

## 5. The database-level gate (35 s)

"Everything above is proven by a database test suite, not just assumed."

Run `make db-gate` (or, if time is short, name its parts): migration round-trips, integrity
(constraint bypass tests written as raw SQL), concurrency, restore-and-verify with a checksum
comparison, and drift-checked docs.

## Say honestly at the end (15 s)

"The rate limiter is still per process — one API instance runs. Task 4 brings this database and the
Task 2 API together with the Task 1 frontend into one deployed platform."

## Before you upload

- [ ] The recording shows no real password, connection string or token (blur the Authorize dialog
      and any terminal `.env` output if in doubt)
- [ ] The README has the demo link, and `docs/openapi.json` is committed and matches the app
      (`make spec-check`)
