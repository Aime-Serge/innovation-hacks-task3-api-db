# Accessibility

This repository is a backend HTTP API (FastAPI, `/api/v1/*`, plus Swagger UI
at `/docs` and a static welcome page at `/`, per `app/main.py` and
`app/api/landing.py`). It has no interactive user interface of its own
beyond the auto-generated Swagger UI page and the single static welcome
page — verified by reading `app/api/`, `app/web/` (`landing.html`,
`landing.css`), and `app/main.py` directly; there is no component library,
no forms beyond Swagger UI's own generated ones, and no client-rendered
application code in this repository.

Web Content Accessibility Guidelines (WCAG) apply to user-facing interfaces.
This service is consumed by other software (the Task 1 dashboard, curl,
Postman, automated tests) rather than rendering a UI for end users to
operate directly, so WCAG conformance is **N/A by design** for this
repository's own surface: there is no custom UI here to audit for contrast,
keyboard navigation, screen-reader labelling, or focus order.

The two exceptions — the welcome page (`app/web/landing.html`) and the
Swagger UI page — are out of scope for a manual accessibility audit in this
pass (no such audit was run; this paragraph does not claim WCAG conformance
for either page, only that they exist and are not the focus of this API's
accessibility posture).

Accessibility work for the actual end-user experience belongs to the
consuming UI, i.e. **Task 1** (the DevDash dashboard). See that project's
own accessibility documentation for WCAG conformance claims, keyboard and
screen-reader testing, and colour-contrast checks; none of that is
duplicated or asserted here.
