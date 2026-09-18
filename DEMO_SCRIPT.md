# Demo Video Script

Target length: **3:00–3:30** (within the guide's 2–5 minute range —
backend-only, but there's more to show than Task 2: real persistence,
migrations, and cascading deletes).

Record against a locally running stack: Postgres via `docker compose up -d`,
migrations applied (`alembic upgrade head`), then `uvicorn app.main:app --reload`.
Use the Swagger UI at `http://localhost:8000/docs` — every request in
this script should actually be sent against the real database, not a
slide.

| Time | Beat | Say | Show |
| --- | --- | --- | --- |
| 0:00–0:20 | Cold open | "This is Task 2's API with the in-memory store swapped for real PostgreSQL — same routes, same request/response contracts, just backed by a real database now. FastAPI, SQLAlchemy 2.0, Alembic migrations." | Terminal: `docker compose up -d`, then `alembic upgrade head` showing the migration apply cleanly. Then Swagger UI overview at `/docs`. |
| 0:20–0:50 | Create the full chain | "User, then a project owned by that user, then a task on that project — the exact same three-entity chain as Task 2." | `POST /users` (Try it out, Execute, show the real 201). `POST /projects` with that user's id. `POST /tasks` with that project's id. |
| 0:50–1:20 | Prove it's a real database, not memory | "This isn't just holding state in a Python dict anymore — it's actually in Postgres." | Terminal split: `psql` (or `docker exec ... psql`) a quick `SELECT * FROM users;` showing the row that was just created via the API — the same row, same UUID. |
| 1:20–1:50 | Relationships enforced at two layers | "A project needs a real owner, same as Task 2 — but now there's also a foreign key at the schema level, so even a raw SQL insert bypassing the API would get rejected." | `POST /projects` with a random UUID as `owner_id` (404, API-layer check). Mention (or show briefly in `app/db/models.py`) that `owner_id` is also a real FK with `ON DELETE CASCADE`. |
| 1:50–2:30 | Cascade delete, the headline feature | "Delete a user, and everything they own goes with them — their projects, and those projects' tasks — enforced by the database itself, not application code looping through and deleting things one by one." | `DELETE /users/{id}` on the user from earlier (204). Then `GET` the project and the task by their ids — both 404 now, even though neither was deleted directly. |
| 2:30–2:50 | Full CRUD on every entity | "Projects can now be renamed and deleted too, not just created and read — same cascade rule applies: delete a project, its tasks go with it." | `POST /projects` + `POST /tasks` again, then `PATCH /projects/{id}` (rename), then `DELETE /projects/{id}`, then show the task is gone. |
| 2:50–3:15 | Close | "60 tests, all passing against a real Postgres instance — including tests that bypass the API entirely and hit the database directly, proving the schema itself enforces these rules. Full source, ER diagram, and API docs in the repo linked below." | Quick cut to a passing `pytest -v` run, then the README's ER diagram, then back to the repo's GitHub page. |

## Notes for whoever records this

- The cascade-delete beat (1:50–2:30) is the single most important
  thing to get right on camera — it's the feature that most clearly
  distinguishes this task from Task 2, so don't rush it.
- No auth on this task either (still deliberate, still Task 4's job) —
  no need to apologize for it on screen.
- If a live `psql` terminal split feels like too much setup, it's fine
  to skip beat 0:50–1:20 and instead just say "this is now backed by
  real Postgres" once at the top — the cascade-delete beat later
  already proves persistence indirectly.
- Have the random-UUID and the real ids typed/copied into separate
  Swagger tabs before recording, so the video doesn't sit on typing or
  copy-pasting UUIDs mid-take.
