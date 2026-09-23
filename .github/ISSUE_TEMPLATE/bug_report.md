---
name: Bug report
about: Something in the API or the PostgreSQL data layer doesn't behave as documented
title: "[bug] "
labels: bug
---

## Requirement ID(s)

Which functional/non-functional requirement or business rule does this
violate, if any? See `docs/standards/task3-standards-pack.md` (e.g. `FR-305`
full CRUD, `FR-309` status/completion consistency, `NFR-306` no orphaned
rows) or the Task 2 pack for earlier IDs. Use `<set-me>` if none applies.

## Description

A clear description of what's wrong.

## Steps to reproduce

1.
2.
3.

## Expected behaviour

## Actual behaviour

## Environment

- Storage backend: `memory` / `sql` (`STORAGE_BACKEND`)
- Commit or tag: <set-me>
- `APP_ENV`: <set-me>

## Tests touched

Which existing tests cover this area, and did you add/update a test that
fails before your fix and passes after (per the standards pack: "A bug fix
adds a test that failed before the fix")? List the test file(s) and
`TC-###` id(s) if applicable.

## Screenshots / logs

Attach screenshots or log excerpts if relevant. Do not include real
credentials, tokens, or personal data — see `SECURITY.md`.
