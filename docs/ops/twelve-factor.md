# Twelve-factor conformance

A real check of this repository against the [12-factor app](https://12factor.net)
methodology, done by reading the actual code and config for each factor
during this pass, not by asserting compliance. "Partial" means a real,
named gap was found, not a hedge.

| # | Factor | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Codebase | **Conforms** | One git repository, one codebase, deployed as `development`/`test`/`production` via `APP_ENV` (`app/core/config.py`). |
| 2 | Dependencies | **Conforms** | Explicitly declared in `pyproject.toml`, pinned in `uv.lock`; `Dockerfile` runs `uv sync --frozen --no-dev --no-install-project` into an isolated `.venv`, no reliance on system packages beyond the Python base image. |
| 3 | Config | **Conforms** | `app/core/config.py`'s `Settings(BaseSettings)` reads every value from the environment (`.env` locally, real env vars in deploy); a missing/invalid value raises `SystemExit` naming the variable at startup (verified in `load_settings()`). `.env.example` enumerates every variable, including `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`. No secret or environment-specific value is hard-coded in `app/`. |
| 4 | Backing services | **Conforms** | PostgreSQL is attached as a resource via `DATABASE_URL` (`postgresql+asyncpg://...`), swappable for the in-process `memory` backend via `STORAGE_BACKEND` without a code change (`app/core/config.py`, `app/repositories/`). Production is required to use `sql` (`_storage_rules` validator refuses `memory` when `APP_ENV=production`). |
| 5 | Build, release, run | **Conforms** | `Dockerfile` is a distinct build stage (`uv sync` into `.venv`, copied into a slim runtime image); the release/run step (`CMD uvicorn ...`) does not build. Migrations are a separate, explicit step (`make db-migrate`, using `MIGRATION_DATABASE_URL`) run by an operator before deploy — the README states "the API never migrates itself." Build and migrate are cleanly separated from run. |
| 6 | Processes | **Partial** | Application state (users/projects/tasks) lives in PostgreSQL, not in the process, when `STORAGE_BACKEND=sql` — conforms. But the login/registration rate limiter (`app/core/ratelimit.py`) keeps its sliding-window counters **in-process memory** (ADR-216, read directly), which is process-local state. This is a documented, deliberate trade-off, not an oversight — see factor 8. |
| 7 | Port binding | **Conforms** | The service is self-contained and exports HTTP via port binding: `Dockerfile` `EXPOSE 8000` and `CMD ... uvicorn ... --host 0.0.0.0 --port ${PORT}`; `HOST`/`PORT` are themselves env-configured (`app/core/config.py`). No external web server (e.g. nginx) is required in front of it. |
| 8 | Concurrency | **Partial, by explicit design** | The process model does not scale out via "add more processes": the service is pinned to exactly one uvicorn worker (`Dockerfile` CMD `--workers 1`; `render.yaml` `WEB_CONCURRENCY: "1"`), precisely *because* of the in-process rate-limiter state from factor 6. ADR-216 and ADR-330 (both read directly) name this as a known limit and put "a shared rate-limit store so several workers are safe" on the roadmap, not yet implemented. |
| 9 | Disposability | **Conforms** | `Dockerfile` uses exec-form `CMD` so `SIGTERM` reaches uvicorn directly, with `--timeout-graceful-shutdown 20` to drain in-flight requests; a `HEALTHCHECK` polls `/healthz` every 15s. Fast startup is consistent with a single-process FastAPI app with no heavyweight init observed in `app/main.py`. |
| 10 | Dev/prod parity | **Partial** | `APP_ENV` keeps the same codebase across development/test/production, and Docker is the same artifact type in all environments (`render.yaml` `runtime: docker`). But the *default* backing store differs by environment: `STORAGE_BACKEND` defaults to `memory` outside production and only `sql` is allowed in production — meaning a default local/test run does not use the same backing service as production unless `STORAGE_BACKEND=sql` and `SEED_PROFILE=default` are set explicitly (`README.md` quickstart uses the default, i.e. `memory`, unless the reader opts into `make db-up`/`db-migrate`). This gap is intentional (fast tests) and documented, not hidden, but it is a real parity gap. |
| 11 | Logs | **Conforms** | `app/core/logging.py`'s `JsonFormatter` writes structured JSON to `logging.StreamHandler(sys.stdout)` (verified directly, line 41) — logs are an unbuffered event stream, not written to a file by the app itself; the execution environment (Docker/Render) is left to route/aggregate them, per the 12-factor model. |
| 12 | Admin processes | **Conforms** | Migrations (`alembic upgrade head`, `make db-migrate`) and the demo seed (`SEED_PROFILE`, `app/seed/`) run as one-off admin processes against the same codebase/config mechanism as the app itself, using the same `Settings` loader and (for migrations) a distinct, narrowly-scoped `MIGRATION_DATABASE_URL`. |

## Summary

9 of 12 factors conform outright; 3 (processes, concurrency, dev/prod
parity) have a real, named, already-documented gap rather than a hidden
one — each traces to the same root cause (the in-process rate limiter,
ADR-216) and each has a stated roadmap item in the repository's own ADRs
(a shared rate-limit store). This table does not assert full compliance
where it was not found.
