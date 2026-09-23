## Summary

What does this change, and why?

## Requirement ID(s)

List the `FR-3##` / `NFR-3##` / `BR-3##` (or Task 2 equivalents) this PR
addresses, per `docs/standards/task3-standards-pack.md`. Use `<set-me>` if
none applies (e.g. pure chore/docs).

## Definition of done (see CONTRIBUTING.md)

- [ ] Requirement IDs listed above
- [ ] Migration included and reversible, if the schema changed
      (`make db-check`, `make db-roundtrip`)
- [ ] ERD and data dictionary regenerated, if the schema changed
      (`make db-docs`)
- [ ] Tests added or updated
- [ ] `docs/openapi.json` unchanged, or the diff is explained
      (`make spec-check`, `make spec-diff`)
- [ ] README updated, if setup or configuration changed
- [ ] Relevant Standards Gate items ticked
      (`docs/standards/task3-standards-pack.md`, section 11)
- [ ] `make gate` passes locally

## Tests touched

List the test file(s) / `TC-###` ids that cover this change.

## Screenshots

Attach screenshots for any UI/response-shape change. Verify the referenced
file actually exists before linking it — do not reference a screenshot that
hasn't been captured yet; write "manual step: capture <view>" instead.

## Notes for the reviewer
