# Test To-Do (YOURS — you own everything here)

The assistant does NOT write these unless you explicitly ask. This is your
test-automation practice checklist. Update it freely as you go. Organized by the test pyramid + infra.

## Setup / tooling
- [ ] Create `tests/` structure: `tests/unit/`, `tests/api/`, `tests/e2e/`, `load/`
- [ ] Test dependencies: `pytest`, `httpx`, `pytest-cov`, `pytest-playwright`, `locust`, `allure-pytest`
- [ ] `tests/conftest.py` — shared fixtures (base URL, admin/user tokens, seeded data, reset hook)
- [ ] `pytest.ini` / `pyproject.toml` — markers (`unit`, `api`, `e2e`, `smoke`), addopts
- [ ] Point tests at the app via `/api/test/reset` + `/api/test/seed` for deterministic runs

## Unit tests (middle layer) — `tests/unit/`
- [ ] Order state machine: valid transitions pass, invalid ones rejected (e.g. DELIVERED→PACKING)
- [ ] Cart total / line-total math (incl. quantity edge cases)
- [ ] Payment check (fail-card suffix logic)
- [ ] Stock decrement logic
- [ ] Coverage report with `pytest-cov`; set a coverage threshold

## API tests (largest layer) — `tests/api/`
Auth
- [ ] Register: success, duplicate email (409), bad payload (422)
- [ ] Login: success, wrong password (401), unknown user (401)
- [ ] `/me`: valid token, missing token (401), expired/invalid token (401)
RBAC / security
- [ ] Normal user blocked from admin routes (403)
- [ ] Unauthenticated blocked from protected routes (401)
Products
- [ ] List products; get by id; 404 for missing id
Cart
- [ ] Add item, update qty, remove item, get cart total
- [ ] Add out-of-stock / invalid product handling
Checkout / orders
- [ ] Successful checkout creates order, decrements stock, empties cart
- [ ] Fail-card path returns payment error, no order created
- [ ] Empty-cart checkout rejected
- [ ] List my orders; get order detail with status history; can't see another user's order
Admin
- [ ] List all orders
- [ ] Advance status through full lifecycle; invalid transition rejected
- [ ] Create/update products
Contract
- [ ] Validate responses against the OpenAPI schema (`/openapi.json`)
Data-driven
- [ ] Parametrize a representative endpoint (e.g. validation cases)

## UI / E2E tests (fewest) — `tests/e2e/` (Playwright, Page Object Model)
- [ ] Page objects: Login, Catalog, ProductDetail, Cart, Checkout, Orders, Admin
- [ ] Journey: register/login → add to cart → checkout → see order
- [ ] Journey: admin login → advance an order's status → user sees updated timeline
- [ ] Async check: cart badge updates via fetch (`wait_for_response`)
- [ ] Negative: login with bad creds shows error
- [ ] Config: cross-browser, parallel workers, trace + screenshot on failure

## Load testing (LOCAL ONLY) — `load/`
- [ ] Locust file: browse catalog + add to cart + checkout user flow
- [ ] Run against local Docker Compose stack only (never Render)
- [ ] Capture p95 latency, RPS, error rate; note a baseline
- [ ] (Optional) compare Postgres behavior under increasing concurrency

## Infra / CI-CD (the automation differentiators)
- [ ] `.github/workflows/ci.yml`: lint → unit (+coverage gate) → build image → compose up → API tests → E2E tests
- [ ] Deploy-only-if-green step → Render
- [ ] Publish Allure report as a CI artifact
- [ ] Smoke test suite that runs against the deployed Render URL
- [ ] (Stretch) Pact contract tests
- [ ] (Stretch) Terraform/Ansible for infra automation bullet

## Resume checkpoints (mark when you can honestly claim it)
- [ ] 80+ automated tests across the pyramid, wired into CI
- [ ] CI/CD quality gate blocks deploy on any failure
- [ ] OpenAPI contract validation + RBAC/security coverage
- [ ] Locust load testing with reported p95 / throughput
- [ ] Playwright POM, parallel + cross-browser, trace-based diagnostics
