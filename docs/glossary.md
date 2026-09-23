# Glossary

Domain terms as they are actually defined in this codebase. Entities are
from `app/domain/models.py`; enum values are from `app/domain/enums.py`,
read directly for this pass — nothing here is invented or extrapolated
beyond those two files plus the standards pack.

## Entities (`app/domain/models.py`)

| Term | Definition |
| --- | --- |
| **User** | An account: `id`, `name`, `email` (unique), `password_hash` (never part of equality/repr, ADR-315), `role`, `avatar_url`, `theme`, `created_at`/`updated_at`, plus optional `given_name`, `family_name` and a `profile` JSON block captured at registration. |
| **Project** | A container for tasks, owned by one user: `id`, `name`, `description`, `status`, optional `due_date`, `owner_id`, timestamps. |
| **Task** | A unit of work inside a project: `id`, `project_id`, `title`, `description`, `status`, `priority`, optional `due_date`, optional `assignee_id`, optional `completed_at`, timestamps. |
| **Activity** | An audit-trail entry for a user's action on a project (and optionally a task): `id`, `actor_id`, `project_id`, optional `task_id`, `type`, `at`. |
| **Progress** | A computed (not stored) summary for a project: `total_tasks`, `done_tasks`, `percent`. |

## Enums (`app/domain/enums.py`)

| Enum | Values | Notes |
| --- | --- | --- |
| **Role** | `developer`, `lead` | New registrations default to `developer`; `lead` may be set explicitly at registration (ADR on role registration). |
| **Theme** | `light`, `dark`, `system` | User display preference; no UI in this repository (API only). |
| **ProjectStatus** | `planned`, `active`, `on_hold`, `completed` | |
| **TaskStatus** | `todo`, `in_progress`, `in_review`, `done` | Transitions between these are constrained by business rules (see `app/domain/rules.py`); the database enforces the value set via `ck_tasks_status`, and `ck_tasks_completed_consistency` requires `completed_at` to be set if and only if `status = 'done'`. |
| **Priority** | `low`, `medium`, `high`, `urgent` | Stored as text; a generated `priority_rank` smallint column (`urgent`=4 ... `low`=1) backs ordering, per `database/docs/data-dictionary.md`. |
| **ActivityType** | `created`, `status_changed`, `completed` | The kind of event recorded in the `activity` table/audit trail. |

## Other terms used in this repository

| Term | Definition |
| --- | --- |
| **Storage backend** | `STORAGE_BACKEND` setting: `memory` (in-process, resets on restart; default outside production) or `sql` (PostgreSQL; required in production). See `app/core/config.py`. |
| **Application role (`ih_app`)** | The PostgreSQL role the running API connects as: row-level `SELECT/INSERT/UPDATE/DELETE` only, no schema changes (`database/init/roles.sh`). |
| **Migration role (`ih_migrator`)** | The PostgreSQL role that owns the database and is the only one permitted to run `alembic upgrade`; kept out of the running API's environment. |
| **Readonly role (`ih_readonly`)** | A PostgreSQL role with schema `USAGE` only; per-column table grants are applied separately in a migration (see `docs/ops/runbook.md`). |
| **Gate** | The repository's combined `make gate` / `make db-gate` targets (lint, types, tests, contract checks, DB checks) that must pass before a change is considered done (`Makefile`). |
| **ADR** | Architecture Decision Record, one file per decision under `docs/adr/`, indexed in `docs/adr/README.md`. |
| **Standards pack** | The task-specific requirements document this repository is built against (`docs/standards/task3-standards-pack.md`), source of the FR-/NFR- requirement IDs referenced in code comments. |
