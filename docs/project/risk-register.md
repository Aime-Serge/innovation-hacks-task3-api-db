# Risk register

Top risks specific to this DB-backed API, each checked against real files
in this repository during this pass rather than assumed. Not exhaustive —
limited to what could be verified in the time available.

| # | Risk | Evidence | Impact if realised |
| --- | --- | --- | --- |
| 1 | **Single-worker capacity ceiling.** The service intentionally runs one uvicorn worker (`Dockerfile` CMD, `render.yaml` `WEB_CONCURRENCY=1`) because the login/registration rate limiter is in-process (`app/core/ratelimit.py`, ADR-216). Measured capacity is about 40 requests/second; at 5 concurrent users, list endpoints already exceed the pack's 200 ms p95 target, and at 10 users most endpoints do (`docs/adr/ADR-330-load-profile-and-capacity.md`, read directly — these are real measured numbers, not estimates). | `docs/adr/ADR-216-in-process-rate-limiter.md`, `docs/adr/ADR-330-load-profile-and-capacity.md`, `render.yaml` | Scaling to more than a small team's traffic requires a shared rate-limit store and likely a connection pooler first (both explicitly called out as out-of-scope roadmap items in ADR-330). |
| 2 | **Backups are manual, not scheduled.** `make db-backup` (`database/scripts/backup.sh`) and `make db-restore-test` exist and work as documented, but no cron job, GitHub Actions schedule, or other automated trigger was found — verified by `grep -rniE "cron|schedule" .github/workflows/ci.yml Makefile database/ scripts/`, which returned no matches. | `database/scripts/backup.sh`, `Makefile`, grep above | If nobody runs `make db-backup` on a cadence, the documented RPO of 24 hours (`docs/ops/runbook.md`, from the standards pack, NOT independently re-tested) is aspirational rather than enforced. |
| 3 | **Free-tier hosting sleeps.** `render.yaml` sets `plan: free`, and the README states the (Task 2) free-tier service "sleeps, so the first request can take about a minute." The same plan is configured for this repository's own deployment. | `render.yaml`, `README.md` | Availability/latency on first request after idle is a real, acknowledged limitation of the current deployment target, not a defect in the code. |
| 4 | **No point-in-time recovery.** `docs/ops/runbook.md` (this pass's own earlier work, re-confirmed by reading `database/scripts/` again) notes PITR is only available via a managed provider and "no such provider is configured in this repository." Recovery is limited to the newest `pg_dump`, verified restorable by `make db-restore-test` (row counts + PK checksum comparison), not to an arbitrary point in time. | `database/scripts/backup.sh`, `database/scripts/restore-test.sh`, `docs/ops/runbook.md` | Data loss window after the last dump could exceed the documented 24-hour RPO if the schedule in risk #1 above is not kept manually. |
| 5 | **No dedicated single-step rollback command.** Alembic's standard `alembic downgrade -1` works (every revision has a `downgrade`, per `migrations/README`), but there is no `make` target for it — only `make db-roundtrip`, which exercises up/down/up as a *test*, not as an operator runbook step (confirmed by reading `Makefile`'s `db-roundtrip` target and `migrations/README`). | `Makefile`, `migrations/README` | An operator rolling back a bad migration in production must know the exact Alembic invocation rather than running a documented `make` target; higher chance of operator error under time pressure. |

## What was checked and found to be *not* a risk (stated for completeness)

- **Indexing.** `database/docs/data-dictionary.md` (generated from the live
  schema) shows indexes on every foreign key used in a hot path
  (`ix_projects_owner_id`, `ix_tasks_project_id_status`,
  `ix_tasks_assignee_id_status`, `ix_activity_actor_id`,
  `ix_activity_project_id`, `ix_activity_task_id`), plus trigram indexes for
  text search and partial/composite indexes tuned for specific query
  patterns (`ix_tasks_due_date_open`, `ix_tasks_priority_rank_id`). No
  missing-index gap was found by reading the dictionary; not listed as a
  top-5 risk.
- **Secrets in git history.** Gitleaks was run for real, across full
  history and all branches, by the orchestrating session for this pass:
  **zero leaks found.** Not re-run here; stated as verified fact per the
  session's instructions, not re-verified independently by this agent.
