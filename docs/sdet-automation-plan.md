# SDET Automation Plan (practice + resume)

Structured as the test pyramid plus the infra/CI-CD/load layers that turn "QA" into "SDET".

## The pyramid

### Bottom — API tests (most cases) · pytest + httpx/requests
- Full CRUD per endpoint; auth (valid/invalid/expired token); RBAC (user cannot hit admin routes); validation/negative cases; full order-lifecycle state machine.
- Schema/contract validation against the OpenAPI spec.
- Data-driven / parametrized tests; fixtures for auth tokens + seeded data.
- Target: 60-80+ tests.

### Middle — Unit / integration tests
- Unit-test backend logic (price totals, stock decrement, status-transition rules — e.g. cannot go DELIVERED -> PACKING).
- Coverage via pytest-cov (report a %).

> **IMPORTANT — load testing runs locally only.** Never run heavy Locust load against the
> free public (Render) deployment: you will hit rate limits / throttling / provider-terms
> issues, and the numbers will reflect the provider's throttling, not your app. Run all load
> tests against the local Docker Compose stack where you control resources and get honest
> p95 / RPS / error-rate figures. Use the public deploy only for functional / E2E / smoke runs.

### Top — UI / E2E (fewest) · Playwright (Python) + pytest-playwright
- Page Object Model.
- Critical journeys only: login -> add to cart -> checkout -> see order; admin advances status.
- Cross-browser, parallel execution, trace/screenshot on failure.
- Async practice: assert against fetch-driven cart-badge updates (wait_for_response).

## Cross-cutting layers (the SDET differentiators)
| Area | Tool | Demonstrates |
|---|---|---|
| Containerization | Docker + docker-compose | App + DB + tests containerized |
| CI/CD gate | GitHub Actions | lint -> unit -> API -> build -> run app -> E2E -> deploy only if green |
| Load/performance | Locust (Python-native) | Ramp users on checkout/catalog; p95 latency, RPS, error rate. RUN LOCALLY ONLY |
| Contract testing | Pact (stretch) | Consumer/provider contracts |
| Reporting | Allure | Rich HTML reports as CI artifact |
| Quality gates | ruff/flake8 + coverage thresholds | Fail build under X% coverage |
| Test data mgmt | seed/reset endpoints + factories | Deterministic, isolated runs |
| IaC (stretch) | Terraform / Ansible | "Infrastructure automation" bullet |

## Deployment gate pipeline
```
push/PR -> lint & static analysis
        -> unit tests (+ coverage gate)
        -> build app Docker image
        -> docker compose up (app + db)
        -> run API test suite
        -> run Playwright E2E suite
        -> [all pass?] -> deploy to Render   ── else fail, no deploy
        -> publish Allure report as artifact
```
(Load tests are NOT part of the CI gate — they run locally, on demand, against Docker Compose.)

## Resume bullets this unlocks
- Built a layered automation framework (unit/API/UI) following the test pyramid, 80+ automated tests, integrated into CI/CD.
- Designed a CI/CD quality gate in GitHub Actions that blocks deployment on any test failure; containerized app + test infra with Docker Compose.
- Implemented OpenAPI contract validation and RBAC/security test coverage for a REST API.
- Performance-tested checkout flows with Locust, reporting p95 latency and throughput under load.
- Page Object Model UI automation in Playwright with parallel, cross-browser execution and trace-based failure diagnostics.

## Repo layout
```
/app            # FastAPI e-commerce (SUT)
/tests
  /unit
  /api
  /e2e          # Playwright POM
/load           # Locust
/.github/workflows
docker-compose.yml
```
