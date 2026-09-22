# LinkedIn post draft: Task 3

Post this once the demo video is recorded. Tag Innovation Hacks with LinkedIn's own @-mention: typed
text does not create a real tag. Select their page from the dropdown, and confirm it is their
official page first.

## Post copy

> Task 3 of my Full Stack Development Internship with @Innovation Hacks: replacing Task 2's in-memory storage with a real PostgreSQL database, without changing the API contract underneath it.
>
> What I'm proud of:
> - The database enforces what it can, not just the application: lengths, enums, a unique lower-case email, an `https` avatar, `completed_at` set exactly when a task is `done`, and six foreign keys with deliberate delete rules.
> - Schema changes are Alembic migrations, written by hand and reviewed, each with a downgrade. The gate runs every migration up, down and up again, on an empty and on a seeded database, before it's trusted.
> - Four separate database roles: the running API can read and write rows but cannot alter the schema; a different role owns migrations; a read-only role serves reporting. No connection string is hard-coded anywhere — everything comes from the environment, and the app refuses to start without it.
> - The ERD and the data dictionary are generated from the live schema and checked for drift, so the diagram can't quietly go stale.
> - Backup and restore is tested, not assumed: a scratch restore is compared against the source by row count and primary-key checksum.
> - The whole Task 2 test suite runs again against a disposable PostgreSQL container per worker, plus new concurrency, outage and restart tests.
>
> What I'm being straight about: the rate limiter is still per process, so one API instance runs. Task 4 brings this database and the Task 2 API together with the Task 1 frontend into one deployed platform.
>
> Stack: Python 3.12, FastAPI, PostgreSQL 16, SQLAlchemy 2 (async), Alembic, argon2, JWT, mypy strict, pytest, Schemathesis, Locust, Docker.
>
> Repo and demo in the comments. #FullStackDevelopment #PostgreSQL #FastAPI #Python #BackendDevelopment #InnovationHacks #Internship

## Before you post

- [ ] Demo video recorded (see `DEMO_SCRIPT.md`) and attached
- [ ] Re-run `make gate` (including `make db-gate`) and confirm every figure above still holds
- [ ] Repo pushed; add the repo and live links as the first comment
- [ ] Innovation Hacks tagged through the mention dropdown

## First comment

Repo: _add the GitHub link_
Live docs: _add the Render URL after deploying (see README § Deploying)_
Demo: _add after recording_
