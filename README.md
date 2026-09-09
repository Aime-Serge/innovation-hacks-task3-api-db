# Users, Projects & Tasks API

Task 2 of the Innovation Hacks Full Stack Development Internship — a REST API for managing users, projects, and tasks, built with **Python + FastAPI**. This is the backend that Task 1's dashboard and Task 4's platform will consume.

## Technology Stack

- **Python 3.14**
- **FastAPI** — routing, request/response validation, OpenAPI generation
- **Pydantic v2** / **pydantic-settings** — data validation and environment-based configuration
- **Uvicorn** — ASGI server
- **pytest** + **httpx** (via FastAPI's `TestClient`) — test suite

## Features

- User management: create, list, get, update, delete
- Project management: create, list (with optional `owner_id` filter), get by id
- Task management: create, list (with optional `project_id`/`status` filters), get by id, update, delete
- Dedicated task status-transition endpoint (`todo` / `in-progress` / `done`)
- Centralized error handling — every error response shares one JSON shape
- Input validation on every write operation via Pydantic models
- Environment-variable-driven configuration, no hardcoded secrets
- Auto-generated interactive API docs at `/docs` and `/redoc`

## Architecture Notes

- **Storage**: in-memory repositories (`app/repositories/`) behind a fixed interface. Task 3 will swap these for a real database-backed implementation without changing any router code.
- **Relationships**: `Project.owner_id` references a `User`; `Task.project_id` references a `Project`. Creating a project/task with a non-existent owner/project returns `404`.
- **Auth-readiness**: each router is registered with `dependencies=[]`. Task 4 adds the auth dependency at the router level, with no changes to individual handlers.
- **No authentication in Task 2**: user passwords are stored hashed (PBKDF2-HMAC-SHA256, salted) for forward compatibility, but there is no login/token endpoint — that's Task 4's explicit "Authentication" requirement.

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

### 3. Configure environment variables

```bash
cp .env.example .env
```

`.env` is gitignored — never commit real secrets. See [Environment Variables](#environment-variables) below for what each key means.

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`. Interactive docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Run the tests

```bash
pytest -v
```

## Environment Variables

| Variable | Purpose | Status |
|---|---|---|
| `APP_ENV` | `development` / `production` flag | active |
| `HOST` | Bind address | active |
| `PORT` | Bind port | active |
| `LOG_LEVEL` | Logging verbosity | active |
| `DATABASE_URL` | Database connection string | placeholder — unused until Task 3 |
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

## Screenshots

_Add screenshots of `/docs` (Swagger UI) and a few example requests/responses here before submitting._

## Demo

_Add the demo video link here before submitting._
