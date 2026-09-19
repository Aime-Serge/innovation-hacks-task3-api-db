# LinkedIn post draft — Task 3

Post this once the demo video is recorded and uploaded.

**Before posting**: confirm Innovation Hacks' real LinkedIn page yourself
(search for it directly in LinkedIn) and tag it using LinkedIn's own
`@`-mention autocomplete as you type — typing "@Innovation Hacks" as
plain text does not create a real tag/link, you have to select their
page from the dropdown.

**Only post claims you can explain.** Every statement below is true of
this repo, but you should be able to talk through each one (how a foreign
key with ON DELETE CASCADE works, why two simultaneous signups can race)
if someone asks. Edit the wording so it sounds like you.

## Post copy

**Hook:**
Two people sign up with the same email at the same instant. What happens?

**Body:**
Task 3 of my Full Stack Development Internship with @Innovation Hacks:
the same users/projects/tasks API, now persisted in PostgreSQL with
SQLAlchemy 2.0 and Alembic migrations.

My focus was letting the database enforce the rules, not just the API. A
unique email index, foreign keys with cascade delete, and a native status
enum are all enforced by Postgres itself, and my tests bypass the API to
hit the database directly and prove it.

Two things I caught along the way:
• The brief asks for full CRUD on every entity, and projects could only be
  created and read. Added update and delete.
• The "does it exist? then write it" pattern can race. Two simultaneous
  signups could both pass the check, and the database's rejection could
  surface as a 500 instead of an error a client can act on. It's now a
  clean 409 (verified with tests that simulate the race).

The live API's landing page has a "Run live checks" button that runs
eleven real requests against the deployed API and database, and shows
pass/fail for each.

Stack: FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic, pytest (69 tests run
against real Postgres), deployed on Render with a Neon database.

**Tag:** @Innovation Hacks (via the real mention dropdown — see above)

**Hashtags:** #FullStackDevelopment #PostgreSQL #Python #DatabaseDesign
#BuildInnovateImpact

**Call to action:**
Repo, live API, and demo video are in the first comment. Curious how
others handle check-then-write races.

## First comment (outbound links go here, not in the post body)

Live API (click "Run live checks"): https://ih-task3-api.onrender.com
Repo: https://github.com/Aime-Serge/innovation-hacks-task3-api-db-integration
Demo: [add after recording]

Note: the API runs on a free tier, so the first request after a quiet
period can take up to a minute to wake up.

## Before you post

- [ ] Demo video recorded and uploaded (see `DEMO_SCRIPT.md`)
- [ ] Open the live link yourself once and click "Run live checks"
- [ ] Tag applied via LinkedIn's mention dropdown, not typed as plain text
- [ ] Video or a screenshot (`docs/screenshots/`) attached to the post itself
- [ ] Repo, live, and demo links added as the first comment
