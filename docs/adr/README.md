# Architecture Decision Records

Index of the ADRs in this directory. Each file name carries its own ADR
number; this index only lists what already exists — see the standards packs
under `docs/standards/` for the fuller decision writeups referenced by some
of these IDs (e.g. ADR-301 to ADR-313 in `task3-standards-pack.md`, section 7,
are the data-layer decisions; the `ADR-2xx` and `ADR-3xx` files below are the
in-repo record of decisions made while building this codebase).

## Task 1 / Task 2 era decisions

- [ADR-212: repo layout](ADR-212-repo-layout.md)
- [ADR-213: Python 3.12](ADR-213-python-3-12.md)
- [ADR-214: not backward compatible](ADR-214-not-backward-compatible.md)
- [ADR-215: landing page and health](ADR-215-landing-page-and-health.md)
- [ADR-216: in-process rate limiter](ADR-216-in-process-rate-limiter.md)
- [ADR-217: activity and user reads](ADR-217-activity-and-user-reads.md)
- [ADR-218: optional due date](ADR-218-optional-due-date.md)
- [ADR-219: CSP and body limit](ADR-219-csp-and-body-limit.md)
- [ADR-220: pydantic/mypy alias warning](ADR-220-pydantic-mypy-alias-warning.md)
- [ADR-221: Render demo seeding](ADR-221-render-demo-seeding.md)
- [ADR-222: email validation](ADR-222-email-validation.md)
- [ADR-223: clock and token expiry](ADR-223-clock-and-token-expiry.md)
- [ADR-224: camelCase path parameters](ADR-224-camel-case-path-parameters.md)
- [ADR-225: welcome page](ADR-225-welcome-page.md)

## Task 3 (PostgreSQL data layer) decisions

- [ADR-314: additional repository methods](ADR-314-additional-repository-methods.md)
- [ADR-315: password hash not part of equality](ADR-315-password-hash-not-part-of-equality.md)
- [ADR-316: storage backend default](ADR-316-storage-backend-default.md)
- [ADR-317: test plumbing changes](ADR-317-test-plumbing-changes.md)
- [ADR-318: repository layout](ADR-318-repository-layout.md)
- [ADR-319: branch name](ADR-319-branch-name.md)
- [ADR-320: readonly role](ADR-320-readonly-role.md)
- [ADR-321: Task 1 pack extract](ADR-321-task1-pack-extract.md)
- [ADR-322: activity tie-break](ADR-322-activity-tie-break.md)
- [ADR-323: text ordering](ADR-323-text-ordering.md)
- [ADR-324: window count](ADR-324-window-count.md)
- [ADR-325: replaces first implementation](ADR-325-replaces-first-implementation.md)
- [ADR-326: query timeouts](ADR-326-query-timeouts.md)
- [ADR-327: text the database can store](ADR-327-text-the-database-can-store.md)
- [ADR-328: count only when the page is full](ADR-328-count-only-when-the-page-is-full.md)
- [ADR-329: fewer round trips](ADR-329-fewer-round-trips.md)
- [ADR-330: load profile and capacity](ADR-330-load-profile-and-capacity.md)

Note: `docs/standards/task3-standards-pack.md` section 7 also documents
ADR-301 to ADR-313 (database engine choice, SQLAlchemy/asyncpg, UnitOfWork
port, etc.) inline within the pack itself rather than as separate files in
this directory. This index only lists the standalone files present in
`docs/adr/` at the time of writing; if ADR-301–ADR-313 get split into their
own files later, add them here too.
