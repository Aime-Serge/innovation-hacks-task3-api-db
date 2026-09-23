# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not currently follow Semantic Versioning as a released
package; entries are grouped by the internship task tags in this repository's
git history.

## [Unreleased]

- Documentation and governance closeout pass (LICENSE, SECURITY.md,
  CONTRIBUTING.md, CHANGELOG.md, issue/PR templates, dependabot config, ADR
  index) — see branch `chore/closeout`. TODO(human): summarize any further
  unreleased product changes here.

## [task-3-submission] - 2026-09-22

Task 3: PostgreSQL persistence layer, replacing Task 2's in-memory storage
behind the same API contract. Tag date from `git log -1 --format=%ad
task-3-submission`.

- PostgreSQL 16 schema for `users`, `projects`, `tasks`, and `activity`,
  created only through Alembic migrations (FR-301 to FR-303, FR-319).
- SQL repository implementations behind the Task 2 repository protocols,
  plus a `UnitOfWork` port for atomic multi-step operations (ADR-302,
  ADR-303).
- Database-level validation: named constraints for lengths, enums, unique
  lower-case email, `https` avatar URLs, and status/`completed_at`
  consistency (FR-307 to FR-309).
- Six foreign keys with deliberate delete rules (restrict / set null /
  cascade), each indexed (FR-306, BR-301).
- Least-privilege database roles (`ih_migrator`, `ih_app`, `ih_readonly`)
  and TLS-required production configuration (FR-317, FR-318).
- Seed profiles `default`, `empty`, `large`, and a new `xl` profile for
  performance testing (FR-321).
- Generated ERD and data dictionary (`database/docs/erd.mmd`,
  `database/docs/data-dictionary.md`) (FR-326).
- Backup and verified restore via `make db-backup` / `make db-restore-test`
  (FR-324).
- Full-registration compatibility fields (`givenName`, `familyName`,
  profile data) added via migration `0005`, per the README's "Full
  registration compatibility" section.

## [task-2-baseline] - 2026-09-20

Task 2: the FastAPI REST API (users, projects, tasks) with in-memory
storage, JWT authentication, and the quality gate this repository still
builds on. Tag date from `git log -1 --format=%ad task-2-baseline`.

- Twenty-three documented operations under `/api/v1`, one error envelope,
  bearer-token authentication.
- Business rules BR-01 to BR-06 and BR-201 to BR-211 enforced server-side.
- Test gate (`make gate`): lint, strict mypy, import-linter layering,
  pytest with coverage, OpenAPI spec checks, Schemathesis contract tests,
  bandit/pip-audit, Postman/Newman, Locust load test.

[Unreleased]: <set-me>
[task-3-submission]: <set-me>
[task-2-baseline]: <set-me>
