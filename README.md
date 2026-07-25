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

## Deploy to Render

The repo ships a [`render.yaml`](render.yaml) Blueprint that provisions the web
service **and** a managed Postgres in one step.

1. Push this repo to GitHub (already at `github.com/sumankm1947/automation-framework`).
2. In the [Render dashboard](https://dashboard.render.com/), click **New +** →
   **Blueprint**, and select this repository. Render reads `render.yaml`.
3. When prompted, set **`ADMIN_PASSWORD`** (it uses `sync: false`, so it is never
   stored in git). `JWT_SECRET` is generated automatically; `DATABASE_URL` is wired
   from the managed database.
4. Click **Apply**. Render builds the Docker image, starts Postgres, and deploys.
   The app auto-creates its tables and seeds the admin + catalog on first boot.

Notes:
- `APP_ENV=production` on Render, so the destructive `/api/test/*` endpoints are
  **not** mounted there.
- The Dockerfile binds to Render's injected `$PORT` (falling back to `8000` locally).
- Free-tier caveats: the web service sleeps after inactivity and cold-starts slowly;
  the free Postgres instance expires after ~90 days. Fine for a portfolio demo.
- **Load tests (Locust) must NOT be run against the free Render deploy** — throttling
  makes the numbers meaningless. Run load tests locally only.

CI/CD ("deploy only if green") is added later, once the test suite exists — a
GitHub Actions workflow will run the tests and gate the Render deploy on success.

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
- **Milestone 7 complete:** negative-path polish. Consistent JSON error shape
  (`{"detail": ...}`), correct `401` vs `403`, `402` on declined payment, `409` for
  out-of-stock / illegal state transitions / duplicates, `422` for validation, and a
  catch-all `500` handler that never leaks stack traces. **The app is feature-complete.**

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
