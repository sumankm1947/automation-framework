# App To-Do (assistant follows this)

The assistant builds the e-commerce app (System Under Test) against this list.
Organized by the 7 build milestones. Check items off as completed.

## Milestone 1 — Skeleton + Docker + Postgres + health
- [ ] Project structure (`app/`, `templates/`, `static/`)
- [ ] `requirements.txt`
- [ ] `app/config.py` (env-driven settings: DB URL, JWT, app_env, fail-card suffix)
- [ ] `app/database.py` (SQLAlchemy engine, session, Base, `get_db`)
- [ ] `app/main.py` (FastAPI app factory, startup table create, Swagger at `/docs`)
- [ ] `GET /health` and `GET /ready` endpoints
- [ ] `Dockerfile` (app image)
- [ ] `docker-compose.yml` (app + Postgres, healthchecks)
- [ ] `.env.example`
- [ ] `README.md` (how to run locally with one command)
- [ ] Verify `docker compose up` boots app + DB and `/health` returns 200

## Milestone 2 — Auth + users/roles
- [ ] `app/models.py` — User (email, password_hash, role)
- [ ] `app/security.py` — bcrypt hashing, JWT create/decode
- [ ] `app/deps.py` — `get_current_user`, `require_admin`
- [ ] `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- [ ] Seed a default admin account

## Milestone 3 — Products + catalog pages
- [ ] Product model
- [ ] `GET /api/products`, `GET /api/products/{id}`
- [ ] Catalog page (product grid) + product detail page (Jinja2)
- [ ] Basic CSS file (layout, cards, forms, buttons, nav)

## Milestone 4 — Cart + checkout + orders
- [ ] Cart / CartItem models
- [ ] `GET /api/cart`, `POST /api/cart/items`, `PATCH /api/cart/items/{id}`, `DELETE /api/cart/items/{id}`
- [ ] Order / OrderItem / OrderStatusHistory models
- [ ] `POST /api/checkout` (mock payment; fail-card path; stock decrement; empty-cart guard)
- [ ] `GET /api/orders`, `GET /api/orders/{id}` (with status timeline)
- [ ] Cart page (with fetch-driven cart badge), checkout page, orders + order-detail pages

## Milestone 5 — Admin order lifecycle
- [ ] `app/services.py` — order state machine (allowed transitions), totals, payment check
- [ ] `GET /api/admin/orders`
- [ ] `PATCH /api/admin/orders/{id}/status` (validate transition; write history)
- [ ] Admin product mgmt: `POST /api/admin/products`, `PATCH /api/admin/products/{id}`
- [ ] Admin pages (orders list + status control, product mgmt)

## Milestone 6 — Test-support + docs + testability
- [ ] `POST /api/test/reset`, `POST /api/test/seed` (guarded: only when `app_env=test`)
- [ ] Seed data (products, a user, an admin) that automation can rely on
- [ ] `data-testid` pass across all templates for stable selectors
- [ ] Confirm OpenAPI spec at `/openapi.json` is complete (for contract tests)

## Milestone 7 — Negative-path polish
- [ ] Out-of-stock handling on checkout
- [ ] Bad/failed payment path returns clean error
- [ ] Unauthorized/forbidden responses correct (401 vs 403) across routes
- [ ] Input validation errors return 422 with useful detail
- [ ] Consistent error response shape

## Deployment (after app is stable)
- [ ] `render.yaml` / Render service config (app + Postgres)
- [ ] Document deploy steps in README
- [ ] Wire GitHub Actions to deploy to Render on green (CI itself is user's test todo)
