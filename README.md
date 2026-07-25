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
