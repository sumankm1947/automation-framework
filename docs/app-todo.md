# App To-Do (assistant follows this)

The assistant builds the e-commerce app (System Under Test) against this list.
Organized by the 7 build milestones. Check items off as completed.

## Milestone 1 — Skeleton + Docker + Postgres + health  ✅ DONE (2026-07-23)
- [x] Project structure (`app/`, `templates/`, `static/`)
- [x] `requirements.txt`
- [x] `app/config.py` (env-driven settings: DB URL, JWT, app_env, fail-card suffix)
- [x] `app/database.py` (SQLAlchemy engine, session, Base, `get_db`)
- [x] `app/main.py` (FastAPI app factory, startup table create, Swagger at `/docs`)
- [x] `GET /health` and `GET /ready` endpoints
- [x] `Dockerfile` (app image)
- [x] `docker-compose.yml` (app + Postgres, healthchecks)
- [x] `.env.example`
- [x] `README.md` (how to run locally with one command)
- [x] Verify `docker compose up` boots app + DB and `/health` returns 200
      (verified: /health→200 ok, /ready→200 db ok, /openapi.json title "Shoplite API")

## Milestone 2 — Auth + users/roles  ✅ DONE (2026-07-26)
- [x] `app/models.py` — User (email, password_hash, role) + `Role` enum
- [x] `app/security.py` — bcrypt hashing, JWT create/decode
- [x] `app/deps.py` — `get_current_user` (401), `require_admin` (403)
- [x] `app/schemas.py` — register/login/user/token Pydantic contracts
- [x] `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- [x] Seed a default admin account (`app/seed.py`, idempotent, on startup)
      (verified via SQLite smoke test: register/dup-409/short-422/login/401/me/admin-role)

## Milestone 3 — Products + catalog pages  ✅ DONE (2026-07-26)
- [x] Product model (sku, name, description, `price_cents` int, stock, image_emoji)
- [x] `GET /api/products`, `GET /api/products/{id}` (404 on missing)
- [x] Catalog page (product grid) + product detail page (Jinja2, `data-testid`s)
- [x] Basic CSS file (layout, cards, forms, buttons, nav, color-coded status labels)
- [x] Seed 8 deterministic products (incl. one out-of-stock SKU-PEN for negatives)
- [x] Static mount, `price` Jinja filter (cents→$), cart-badge JS scaffold
      (verified via smoke test: list/single/404, page render, price format, static CSS)

## Milestone 4 — Cart + checkout + orders  ✅ DONE (2026-07-26)
- [x] Cart / CartItem models (one cart per user; unique cart+product)
- [x] `GET /api/cart`, `POST /api/cart/items`, `PATCH /api/cart/items/{id}`, `DELETE /api/cart/items/{id}`
- [x] Order / OrderItem (price snapshot) / OrderStatusHistory models
- [x] `POST /api/checkout` — mock payment (402 on fail-card), stock re-check (409),
      empty-cart guard (400), stock decrement, cart cleared, PLACED history event
- [x] `GET /api/orders`, `GET /api/orders/{id}` (items + status timeline; 404 for others' orders)
- [x] Cart page (JS-rendered, qty edit/remove), checkout form, orders + order-detail pages
- [x] `app/services.py` (cart math, payment check, checkout txn); fetch-driven cart badge live
      (verified via smoke test: 28 checks — add/increment/OOS/exceed/remove/patch, 401/402/400/409,
      stock decrement, ownership 404, all page shells render)

## Milestone 5 — Admin order lifecycle  ✅ DONE (2026-07-26)
- [x] `app/services.py` — order state machine (`ALLOWED_TRANSITIONS`, `advance_order_status`)
- [x] `GET /api/admin/orders` (all orders + customer email), `GET /api/admin/orders/{id}`
- [x] `PATCH /api/admin/orders/{id}/status` (validate transition → 409; writes history)
- [x] Admin product mgmt: `POST /api/admin/products` (409 dup sku), `PATCH /api/admin/products/{id}` (partial)
- [x] Admin pages (`/admin` orders + status control, `/admin/products`); admin nav link role-gated
      (verified via smoke test: 26 checks — RBAC 401/403, full PLACED→DELIVERED chain,
      invalid/terminal 409, 422 bad status, product create/dup/partial-update)

## Milestone 6 — Test-support + docs + testability  ✅ DONE (2026-07-26)
- [x] `POST /api/test/reset`, `POST /api/test/seed` (mounted ONLY when `APP_ENV=test`)
- [x] Seed data automation can rely on: admin, standard user (`user@shoplite.com`/`user12345`), 8 products
- [x] `data-testid` pass across all templates (+ runtime rows: cart-row, order-row, timeline-event)
- [x] OpenAPI at `/openapi.json` complete — every API path present; HTML pages excluded
      (verified via smoke test: seed/reset counts, idempotency, wipe, OpenAPI paths;
      separate check confirms test endpoints 404 + absent from schema outside test env)

## Milestone 7 — Negative-path polish  ✅ DONE (2026-07-26)
- [x] Out-of-stock handling: 409 on add/exceed and re-checked at checkout (409)
- [x] Bad/failed payment path returns clean 402 with `detail`
- [x] 401 vs 403 correct across routes (auth→401, non-admin→403); malformed/bad-sub token→401 (no 500)
- [x] Input validation returns 422 with a `detail` list (short pw, bad email, qty bounds, bad enum, missing fields)
- [x] Consistent error shape: every handled error returns JSON `{"detail": ...}`;
      added a catch-all 500 handler that logs and never leaks stack traces
      (verified via negative-path smoke test: 28 checks across 400/401/402/403/404/409/422)

## Deployment (after app is stable)
- [ ] `render.yaml` / Render service config (app + Postgres)
- [ ] Document deploy steps in README
- [ ] Wire GitHub Actions to deploy to Render on green (CI itself is user's test todo)
