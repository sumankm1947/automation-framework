# Shoplite — E-commerce Test Target

A deliberately simple but architecturally real e-commerce app, built as the
**System Under Test** for a QA / test-automation portfolio. The test framework
(pytest / Playwright / Locust / CI) lives alongside it and is written separately.

Stack: **FastAPI · PostgreSQL · SQLAlchemy + Alembic · JWT · Jinja2 · Docker Compose**

## Run locally (one command)

Requires Docker + Docker Compose.

```bash
docker compose up --build
```

This boots Postgres and the app. Once healthy:

- App / API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json
- Health (liveness): http://localhost:8000/health
- Readiness (DB reachable): http://localhost:8000/ready

Stop and remove containers:

```bash
docker compose down          # keep the database volume
docker compose down -v       # also wipe Postgres data
```

## Configuration

All config is environment-driven. Copy `.env.example` to `.env` to override
defaults locally; Compose supplies sensible defaults without it.

| Var | Purpose |
|---|---|
| `APP_ENV` | `local` \| `test` \| `production`. Guarded `/api/test/*` endpoints enable only under `test`. |
| `DATABASE_URL` | SQLAlchemy Postgres URL. |
| `JWT_SECRET` / `JWT_ALGORITHM` / `JWT_EXPIRE_MINUTES` | Auth (from Milestone 2). |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Default admin seeded on startup if absent. |
| `FAIL_CARD_SUFFIX` | Card suffix that forces a mock-payment failure for negative tests. |

## Build progress

Built in 7 milestones (see `docs/app-todo.md`).

- **Milestone 1 complete:** skeleton, Docker + Postgres, `/health` + `/ready` probes.
- **Milestone 2 complete:** JWT auth with `user`/`admin` roles —
  `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`. A default
  admin (`ADMIN_EMAIL` / `ADMIN_PASSWORD`, default `admin@shoplite.com` / `admin12345`)
  is seeded on startup. Send the token as `Authorization: Bearer <token>`.
- **Milestone 3 complete:** product catalog — `GET /api/products`,
  `GET /api/products/{id}`, plus server-rendered catalog (`/`) and product-detail
  (`/products/{id}`) pages with stable `data-testid`s. Prices are stored as integer
  cents. Eight products (one out-of-stock) are seeded on startup.
- **Milestone 4 complete:** cart, checkout, and orders. Cart API
  (`GET /api/cart`, `POST/PATCH/DELETE /api/cart/items[...]`), `POST /api/checkout`
  (mock payment — a card ending in `FAIL_CARD_SUFFIX` is declined with 402), and
  `GET /api/orders[/{id}]` with a status timeline. Cart/checkout/orders pages fetch
  the API client-side using the JWT saved at login; the cart badge is fetch-driven.
- **Milestone 5 complete:** admin order lifecycle + product management. Admin-only API
  (`GET /api/admin/orders`, `PATCH /api/admin/orders/{id}/status`, `POST`/`PATCH
  /api/admin/products`) enforcing the state machine
  `PLACED → PACKING → IN_TRANSIT → DELIVERED` (+ `CANCELLED`); illegal transitions
  return 409. Admin pages at `/admin` and `/admin/products`.
- **Milestone 6 complete:** test-support + testability. Guarded `POST /api/test/reset`
  and `POST /api/test/seed` (mounted **only** when `APP_ENV=test`) give automation a
  clean, known state. Stable `data-testid`s across every template. The `/openapi.json`
  contract is complete (all API paths; HTML pages excluded).

## Seeded accounts & test hooks

| Account | Email | Password | Role |
|---|---|---|---|
| Admin (always seeded) | `admin@shoplite.com` | `admin12345` | admin |
| Standard user (test seed) | `user@shoplite.com` | `user12345` | user |

Run the app with `APP_ENV=test` to enable the test-support endpoints:

- `POST /api/test/reset` — wipe all data, then re-seed admin + standard user + catalog.
- `POST /api/test/seed` — idempotently ensure the baseline data exists.

Mock payment: any card number ending in `FAIL_CARD_SUFFIX` (default `0000`) is declined
with `402` — use it for negative checkout tests.
