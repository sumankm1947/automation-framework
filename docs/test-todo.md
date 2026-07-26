# Test To-Do — YOUR execution plan (you own everything here)

This is your test-automation practice checklist for the Shoplite SUT. The assistant
does **not** write these tests unless you explicitly ask. Update freely as you go.

Work the phases roughly top-to-bottom. Each item is scoped to be one or a few tests.
Concrete endpoints, status codes, seeded data, and `data-testid`s are in the
**[SUT Quick Reference](#sut-quick-reference)** at the bottom — pull from there so you're
not hunting through the app.

Target: **80+ tests across the pyramid, wired into CI.**

---

## Phase 0 — Project setup & tooling  `tests/`
- [ ] Create the layout: `tests/unit/`, `tests/api/`, `tests/e2e/`, `load/`, `tests/conftest.py`
- [ ] Add dev deps (separate `requirements-dev.txt`): `pytest`, `httpx`, `pytest-cov`,
      `pytest-playwright`, `playwright`, `locust`, `allure-pytest`, `jsonschema` (contract), `ruff`
- [ ] `pyproject.toml`/`pytest.ini`: register markers `unit`, `api`, `e2e`, `smoke`, `contract`;
      set `addopts` (e.g. `-ra --strict-markers`)
- [ ] `conftest.py` fixtures:
  - [ ] `base_url` (env-driven, default `http://localhost:8000`)
  - [ ] `api` — an `httpx.Client` bound to `base_url`
  - [ ] `reset_db` — calls `POST /api/test/reset` before a test/module (needs `APP_ENV=test`)
  - [ ] `admin_token` / `admin_headers` — login `admin@shoplite.com` / `admin12345`
  - [ ] `user_token` / `user_headers` — login `user@shoplite.com` / `user12345`
  - [ ] `fresh_user` — factory: register a random-email user, return its headers
- [ ] Decide the run target per layer: **unit/API/E2E → local Docker Compose in `APP_ENV=test`**;
      smoke → the Render URL. Document the commands in a `tests/README.md`.

## Phase 1 — Unit tests (pure logic)  `tests/unit/`
Import directly from `app/services.py` and `app/security.py`. No server needed for the pure bits;
the cart/checkout helpers need a DB session — use an in-memory SQLite session for those.
- [ ] `is_card_declined` — declines cards ending in the fail suffix (`0000`), accepts others
- [ ] Cart totals — `line_total = price_cents * qty`; grand total = sum of lines; `item_count` = sum of quantities
- [ ] State machine — `can_transition` allows each legal edge and rejects illegal ones
      (spot-check `DELIVERED→PACKING` = False, `PLACED→PACKING` = True, terminals go nowhere)
- [ ] `advance_order_status` — appends a history row and updates status on a legal move; raises on illegal
- [ ] Stock decrement — after `checkout`, product stock drops by ordered qty; cart is emptied
- [ ] Password hashing — `hash_password` + `verify_password` round-trip; wrong password fails
- [ ] Coverage: run `pytest --cov=app`, set a threshold (e.g. `--cov-fail-under=80`)

## Phase 2 — API tests (largest layer)  `tests/api/`
Hit the JSON API over HTTP. Use `reset_db` for isolation. Assert **both** status code and body.

**Auth**
- [ ] Register success → `201`, body has `role: "user"`, **no** `password_hash`
- [ ] Register duplicate email → `409`
- [ ] Register bad payload → `422` (short password `<8`, invalid email) — `detail` is a list
- [ ] Login success → `200` with `access_token`; wrong password → `401`; unknown user → `401`
- [ ] `/me` with valid token → `200`; missing token → `401`; malformed/garbage token → `401`

**RBAC / security**
- [ ] Standard user → any `/api/admin/*` route → `403`
- [ ] Unauthenticated → protected route (`/api/cart`, `/api/orders`, `/api/checkout`) → `401`
- [ ] Token with a non-integer subject → `401` (not 500) — craft via `app.security.create_access_token`

**Products**
- [ ] List → `200`, 8 products, prices in integer cents
- [ ] Get by id → `200`; missing id → `404`

**Cart**
- [ ] Add item → `201`, correct `item_count` / `total_cents`
- [ ] Adding same product again increments quantity (not a second line)
- [ ] Add out-of-stock (`SKU-PEN`) → `409`; add qty > stock → `409`; qty `0` → `422`; missing `product_id` → `422`
- [ ] Update qty → `200`; update beyond stock → `409`; update non-existent / foreign item → `404`
- [ ] Remove item → `200` and item gone

**Checkout / orders**
- [ ] Success → `201`, order `status=PLACED`, snapshot line items, `history` has one PLACED event,
      stock decremented, cart emptied
- [ ] Fail-card (`…0000`) → `402`, no order created, cart untouched
- [ ] Empty-cart checkout → `400`
- [ ] List my orders → `200`; get order detail → items + status timeline
- [ ] Cannot read another user's order → `404` (ids not enumerable)

**Admin**
- [ ] List all orders → `200`, includes `user_email`
- [ ] Advance status full lifecycle `PLACED→PACKING→IN_TRANSIT→DELIVERED` (history grows each step)
- [ ] Illegal transition (e.g. `PLACED→DELIVERED`) → `409`; terminal `DELIVERED→*` → `409`; bad enum → `422`; missing order → `404`
- [ ] Create product → `201`; duplicate SKU → `409`; new product appears in public catalog
- [ ] Partial update product → `200`, only sent fields change; missing product → `404`

**Contract & data-driven**
- [ ] Fetch `/openapi.json`; validate representative responses against their schema (`jsonschema`)
- [ ] Parametrize a validation endpoint (register / cart-add) across several bad payloads → all `422`

## Phase 3 — UI / E2E (fewest, highest value)  `tests/e2e/`  · Playwright + POM
Run against the app in `APP_ENV=test`; `reset` between specs. Select by `data-testid`.
- [ ] Page Objects: `LoginPage`, `CatalogPage`, `ProductDetailPage`, `CartPage`, `OrdersPage`, `OrderDetailPage`, `AdminOrdersPage`, `AdminProductsPage`
- [ ] Auth helper: log in via UI **or** seed `localStorage['shoplite_token']` directly for speed
- [ ] Journey — shopper: register/login → add to cart → checkout (good card) → land on order detail showing `PLACED`
- [ ] Journey — admin: login → `/admin` → advance an order's status → shopper's order-detail timeline reflects it
- [ ] Async: `add-to-cart` updates the `cart-badge` via fetch — assert with `wait_for_response` on `/api/cart/items`
- [ ] Negative: bad login credentials surface `login-error`; out-of-stock product's `add-to-cart` is disabled
- [ ] Config: cross-browser (chromium/firefox/webkit), parallel workers, trace + screenshot on failure

## Phase 4 — Load testing (LOCAL ONLY)  `load/`
> Never run against the Render deploy — throttling makes the numbers meaningless.
- [ ] Locust user flow: browse catalog → view product → login → add to cart → checkout
- [ ] Run against local Docker Compose only; ramp users; capture **p95 latency, RPS, error rate**
- [ ] Record a baseline in `load/README.md`; (optional) observe Postgres under rising concurrency

## Phase 5 — CI/CD quality gate  `.github/workflows/`
- [ ] `ci.yml`: lint (`ruff`) → unit (+ coverage gate) → build image → `docker compose up` (`APP_ENV=test`)
      → API suite → Playwright E2E → publish **Allure** report as an artifact
- [ ] **Deploy-only-if-green**: on `main` and all-green, trigger the Render deploy hook (this is the app's
      existing `render.yaml` service). Load tests are **not** part of the gate.
- [ ] Smoke suite (`-m smoke`) that runs against the **deployed Render URL** post-deploy
      (health/ready, catalog loads, login works) — keep it read-only + tiny
- [ ] (Stretch) Pact consumer/provider contract tests; (Stretch) Terraform/Ansible infra bullet

## Resume checkpoints — mark only when honestly true
- [ ] 80+ automated tests across unit/API/E2E, wired into CI
- [ ] CI/CD quality gate blocks deploy on any failure
- [ ] OpenAPI contract validation + RBAC/security coverage
- [ ] Locust load testing with reported p95 / throughput (local)
- [ ] Playwright POM, parallel + cross-browser, trace-based diagnostics

---

## SUT Quick Reference

**Run the SUT for testing** (enables the reset/seed hooks):
`$env:APP_ENV="test"; docker compose up --build`  → app at `http://localhost:8000`

**Seeded accounts**
| Role | Email | Password | Notes |
|---|---|---|---|
| admin | `admin@shoplite.com` | `admin12345` | seeded on every startup |
| user | `user@shoplite.com` | `user12345` | only after `POST /api/test/seed` or `/reset` (test env) |

**Test hooks** (only when `APP_ENV=test`) — `POST /api/test/reset` (wipe + re-seed baseline),
`POST /api/test/seed` (idempotent ensure baseline).

**Seeded catalog** (price in cents / stock): `SKU-TSHIRT` 1999/50 · `SKU-MUG` 1299/30 ·
`SKU-NOTEBOOK` 899/100 · `SKU-HEADPHONES` 8999/15 · `SKU-BOTTLE` 2499/40 · `SKU-BACKPACK` 5499/8 ·
`SKU-PEN` 499/**0 (out of stock)** · `SKU-CAP` 1599/25.

**Mock payment:** card number ending in `0000` → checkout `402`. Any other → success.

**Endpoints & expected status codes**
- Auth: `POST /api/auth/register` 201/409/422 · `POST /api/auth/login` 200/401 · `GET /api/auth/me` 200/401
- Products: `GET /api/products` 200 · `GET /api/products/{id}` 200/404
- Cart (auth): `GET /api/cart` 200/401 · `POST /api/cart/items` 201/409/422/404 ·
  `PATCH /api/cart/items/{id}` 200/409/404/422 · `DELETE /api/cart/items/{id}` 200/404
- Orders (auth): `POST /api/checkout` 201/400/402/409/401 · `GET /api/orders` 200 · `GET /api/orders/{id}` 200/404
- Admin (401 anon / 403 non-admin): `GET /api/admin/orders` · `GET /api/admin/orders/{id}` ·
  `PATCH /api/admin/orders/{id}/status` 200/409/404/422 · `POST /api/admin/products` 201/409/422 ·
  `PATCH /api/admin/products/{id}` 200/404
- System: `GET /health` · `GET /ready` · `GET /docs` · `GET /openapi.json`

**Order state machine:** `PLACED → {PACKING, CANCELLED}`, `PACKING → {IN_TRANSIT, CANCELLED}`,
`IN_TRANSIT → {DELIVERED}`, `DELIVERED`/`CANCELLED` terminal.

**Unit-test targets (import directly):** `app.services.is_card_declined`, `.cart_to_public`,
`.can_transition`, `.advance_order_status`, `.checkout`; `app.security.hash_password`/`verify_password`.

**Error shape:** all handled errors return `{"detail": ...}` (a string for `HTTPException`, a list for `422`).

**Key `data-testid`s for E2E** (runtime-injected rows noted):
- Nav: `nav-catalog`, `nav-cart`, `cart-badge`, `nav-orders`, `nav-admin`, `nav-login`, `nav-logout`
- Catalog: `product-grid`, `product-card` (`data-sku`), `product-name`, `product-price`, `product-stock`, `add-to-cart` (`data-product-id`)
- Product detail: `product-detail`, `detail-name`, `detail-price`, `detail-stock`, `add-to-cart`
- Login: `login-form`, `login-email`, `login-password`, `login-submit`, `login-error`,
  `register-form`, `register-email`, `register-password`, `register-submit`, `register-error`, `register-ok`
- Cart: `cart-empty`, `cart-table`, `cart-total`, `checkout-form`, `checkout-card`, `checkout-submit`, `checkout-error`;
  rows → `cart-row` (`data-item-id`), `cart-qty`, `cart-line-total`, `cart-remove`
- Orders: `orders-empty`, `orders-table`; rows → `order-row`, `order-link`, `order-row-status`
- Order detail: `order-detail` (`data-order-id`), `order-status`, `order-total`, `order-timeline`;
  rows → `order-item-row`, `timeline-event`
- Admin orders: `admin-orders-table`; rows → `admin-order-row` (`data-order-id`), `admin-order-customer`,
  `admin-order-status`, `admin-status-select`, `admin-status-save`
- Admin products: `product-create-form`, `product-sku`, `product-name`, `product-price`, `product-stock`,
  `product-create-submit`, `product-create-ok`; rows → `admin-product-row`, `admin-product-price`,
  `admin-product-stock`, `admin-product-save`

**Auth for the UI:** the browser stores the JWT in `localStorage['shoplite_token']` after login and
sends it as `Authorization: Bearer <token>`. You can set it directly to skip the login UI in E2E setup.
