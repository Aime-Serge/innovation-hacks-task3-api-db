# Users, Projects & Tasks API

Task 3 of the Innovation Hacks Full Stack Development Internship — a REST API for managing users, projects, and tasks, built with **Python + FastAPI** and backed by **PostgreSQL**. This is the backend that Task 1's dashboard and Task 4's platform will consume.

## Technology Stack

- **Python 3.14**
- **FastAPI** — routing, request/response validation, OpenAPI generation
- **Pydantic v2** / **pydantic-settings** — data validation and environment-based configuration
- **PostgreSQL 16** — persistent data store (Docker for local dev)
- **SQLAlchemy 2.0** — ORM / data access layer
- **Alembic** — versioned, hand-written schema migrations
- **Uvicorn** — ASGI server
- **pytest** + **httpx** (via FastAPI's `TestClient`) — test suite, run against a real Postgres instance

## Features

- User management: create, list, get, update, delete
- Project management: create, list (with optional `owner_id` filter), get by id, update, delete
- Task management: create, list (with optional `project_id`/`status` filters), get by id, update, delete
- Dedicated task status-transition endpoint (`todo` / `in-progress` / `done`)
- Centralized error handling — every error response shares one JSON shape,
  including framework-raised errors (unmatched route, wrong HTTP method),
  not just application-raised ones
- Input validation on every write operation via Pydantic models
- CORS configured for the frontend origin (`CORS_ORIGINS`)
- Environment-variable-driven configuration, no hardcoded secrets
- Auto-generated interactive API docs at `/docs` and `/redoc`

## Architecture Notes

- **Storage**: PostgreSQL via SQLAlchemy (`app/db/`), behind repositories (`app/repositories/`) that expose the same method signatures Task 2's in-memory store used. `app/routers/` started as a **zero-line diff** from Task 2; `PATCH`/`DELETE /projects/{id}` were added on top once persistence made full CRUD on every entity possible (Task 2's in-memory store deliberately left projects create/read-only).
- **Relationships**: `Project.owner_id` references a `User`; `Task.project_id` references a `Project`. Creating a project/task with a non-existent owner/project returns `404` (API-layer check, unchanged from Task 2) — and the foreign keys enforce it at the schema level too.
- **Cascade rule**: both foreign keys are `ON DELETE CASCADE` — deleting a user deletes their projects (and those projects' tasks); deleting a project deletes its tasks. This preserves Task 2's existing `DELETE /users/{id}` behavior (which already deletes unconditionally, with no ownership check) instead of introducing a new FK-violation error path, and `DELETE /projects/{id}` relies on the exact same mechanism for its own tasks.
- **Auth-readiness**: each router is registered with `dependencies=[]`. Task 4 adds the auth dependency at the router level, with no changes to individual handlers.
- **No authentication yet**: user passwords are stored hashed (PBKDF2-HMAC-SHA256, salted) for forward compatibility, but there is no login/token endpoint — that's Task 4's explicit "Authentication" requirement.

## Known Gaps / Assumptions

- **Check-then-act races, mitigated at the database layer**: each repository call opens and commits its own transaction (`session_scope()`), so a router's "does the referenced row exist?" check and the write that follows it aren't one atomic unit. A request racing in between (e.g. two `POST /users` with the same email, or a `DELETE` landing between another request's existence check and its own write) is still possible — but the database's own constraints (the unique index on `email`, the `ON DELETE CASCADE` foreign keys) are the actual source of truth, and every write path that can hit one translates the resulting `IntegrityError` (or a vanished row) into the same clean 409/404 the pre-check would have raised, instead of letting it surface as an uncaught 500. See `tests/test_race_conditions.py`.
- **No pagination**: `GET /users`, `GET /projects`, and `GET /tasks` return every matching row with no `limit`/`offset`. Fine at this task's scale, not for a real deployment.
- **No rate limiting**: combined with no auth, nothing currently prevents a client from hammering any endpoint.
- **`psycopg2-binary`**: fine for local dev/tests, but discouraged for production per its own docs (prefer building `psycopg2` from source against the target platform's OpenSSL/libpq).

## Schema / ER Diagram

```mermaid
erDiagram
    USERS ||--o{ PROJECTS : owns
    PROJECTS ||--o{ TASKS : contains

    USERS {
        uuid id PK
        varchar_100 name
        varchar_320 email UK
        varchar_255 password_hash
        timestamptz created_at
    }
    PROJECTS {
        uuid id PK
        varchar_150 name
        text description
        uuid owner_id FK
        timestamptz created_at
    }
    TASKS {
        uuid id PK
        varchar_200 title
        text description
        uuid project_id FK
        enum status
        timestamptz created_at
        timestamptz updated_at
    }
```

- `projects.owner_id -> users.id`, `ON DELETE CASCADE`
- `tasks.project_id -> projects.id`, `ON DELETE CASCADE`
- `tasks.status` is a native Postgres enum (`todo` / `in-progress` / `done`), independent of the Pydantic-level check
- Indexes: `users.email` (unique), `projects.owner_id`, `tasks.project_id`, `tasks.status`, composite `(project_id, status)` for the combined filter used by Task 1's search/filter feature

## Getting Started

### 1. Create an isolated virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Postgres (Docker — never a shared/production database)

```bash
docker compose up -d
# or: docker run --name ih-task3-db -e POSTGRES_PASSWORD=devpassword \
#       -e POSTGRES_DB=ih_task3 -p 127.0.0.1:5432:5432 -d postgres:16
```

A free-tier managed host (Supabase / Neon / Railway) works too — just put its connection string in `DATABASE_URL` in the next step.

### 4. Configure environment variables

```bash
cp .env.example .env
# then set DATABASE_URL, e.g.:
# DATABASE_URL=postgresql+psycopg2://postgres:devpassword@localhost:5432/ih_task3
```

`.env` is gitignored — never commit real secrets. See [Environment Variables](#environment-variables) below for what each key means.

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Seed sample data (optional)

```bash
python -m app.seed
```

Inserts 3 users, 4 projects, and 10 tasks across all three statuses. Safe to re-run — it's a no-op if the `users` table already has rows.

### 7. Run the server

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`. Interactive docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 8. Run the tests

```bash
pytest -v
```

`pytest` applies migrations and truncates all tables before every test (see `tests/conftest.py`), so it needs `DATABASE_URL` pointed at a real, reachable Postgres — point it at a database you don't mind being wiped, or use a separate one (e.g. `ih_task3_test`) if you want seeded data to survive alongside test runs.

## Environment Variables

| Variable | Purpose | Status |
|---|---|---|
| `APP_ENV` | `development` / `production` flag | active |
| `HOST` | Bind address | active |
| `PORT` | Bind port | active |
| `LOG_LEVEL` | Logging verbosity | active |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | active |
| `DATABASE_URL` | SQLAlchemy Postgres connection string | **active** — required, no hardcoded fallback |
| `SECRET_KEY` | Auth signing key | placeholder — unused until Task 4 |

See `.env.example` for the full template (keys only, no real values).

## Route Table

All error responses share this shape:

```json
{"error": {"code": "not_found", "message": "...", "details": null}}
```

### Users

| Method | Path | Purpose | Success | Failure |
|---|---|---|---|---|
| POST | `/users` | Create a user | 201 | 422, 409 |
| GET | `/users` | List users | 200 | — |
| GET | `/users/{user_id}` | Get user by id | 200 | 404 |
| PATCH | `/users/{user_id}` | Partially update a user | 200 | 404, 422, 409 |
| DELETE | `/users/{user_id}` | Delete a user | 204 | 404 |

### Projects

| Method | Path | Purpose | Success | Failure |
|---|---|---|---|---|
| POST | `/projects` | Create a project | 201 | 422, 404 (owner not found) |
| GET | `/projects` | List projects (optional `?owner_id=`) | 200 | — |
| GET | `/projects/{project_id}` | Get project by id | 200 | 404 |
| PATCH | `/projects/{project_id}` | Update a project's name/description | 200 | 404, 422 |
| DELETE | `/projects/{project_id}` | Delete a project (cascades to its tasks) | 204 | 404 |

### Tasks

| Method | Path | Purpose | Success | Failure |
|---|---|---|---|---|
| POST | `/tasks` | Create a task | 201 | 422, 404 (project not found) |
| GET | `/tasks` | List tasks (optional `?project_id=`, `?status=`) | 200 | — |
| GET | `/tasks/{task_id}` | Get task by id | 200 | 404 |
| PATCH | `/tasks/{task_id}` | Update task title/description | 200 | 404, 422 |
| PATCH | `/tasks/{task_id}/status` | Transition task status (`todo`/`in-progress`/`done`) | 200 | 404, 422 |
| DELETE | `/tasks/{task_id}` | Delete a task | 204 | 404 |

### Health

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Service health check |

## Status Code Policy

- **200** — successful GET/PATCH
- **201** — successful POST (resource created)
- **204** — successful DELETE (no body)
- **404** — path id not found, or a body field referencing another resource (`owner_id`, `project_id`) doesn't exist
- **409** — conflict (duplicate user email)
- **422** — Pydantic validation failure (missing/invalid field, bad enum value) — FastAPI's native behavior, kept as-is rather than remapped to 400
- **500** — unhandled server error, generic message only; full traceback logged server-side

## Deployment

The API deploys to **Render** (free tier) from the included
[`render.yaml`](render.yaml); the database is an external free Postgres,
for example [Neon](https://neon.com). Render allows only one free
Postgres per workspace, so this Blueprint deliberately doesn't create one.

1. **Create the database.** On Neon (or any Postgres host) create a
   project and copy its connection string, for example
   `postgresql://user:password@host/dbname?sslmode=require`. Use the
   direct (non-pooled) connection string.
2. **Create the service.** render.com → **New → Blueprint** → select this
   repo (branch `main`). It reads `render.yaml` and creates `ih-task3-api`.
3. **Fill in the prompted values:** `DATABASE_URL` (the string from step 1)
   and `CORS_ORIGINS` (the origin of whatever will call this API from a
   browser, or `http://localhost:3000`).
4. The build runs `pip install` then `alembic upgrade head`, creating the
   schema on first deploy. The service only goes **Live** once `/health`
   can reach the database.
5. Open `https://<your-service>.onrender.com/` — the landing page has a
   "Run live checks" button that exercises the deployed API and database.
   `/docs` is the Swagger UI.
6. Optional: load sample data from a Shell on the service with
   `python -m app.seed`.

Things to know:

- Data persists across restarts and redeploys (unlike Task 2).
- The free web service sleeps after 15 minutes idle (the next request
  takes up to a minute), and Neon's free compute also suspends when idle,
  so the first database query after a quiet period is a little slower.

## Screenshots

All captured against the real running app — Swagger UI's own "Try it
out" hitting a live server backed by real Postgres, not mocked
examples. Note the `projects` group now includes the `PATCH`/`DELETE`
endpoints added after the initial build (see [Architecture
Notes](#architecture-notes)).

| Swagger UI overview |
| --- |
| ![Swagger UI overview](docs/screenshots/01-swagger-overview.png) |

| `POST /users` expanded | Real request/response via "Try it out" |
| --- | --- |
| ![Create user expanded](docs/screenshots/02-create-user-expanded.png) | ![Create user response](docs/screenshots/03-create-user-response.png) |

## Demo

- **Demo video**: _add link here after recording_ — see
  [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) for the timestamped shot list
  (3–3:30 min, per the internship's Demo Video Requirements).
