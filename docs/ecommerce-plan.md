# E-commerce App Plan (System Under Test)

The application exists to be *tested*, not admired. Simple UI, real architecture.

## Design principles
- Deliberately simple UI (ugly is fine), but a genuine backend, real database, documented REST API, and stateful workflows (order lifecycle).
- Automation-friendly by construction: stable `data-testid` attributes, auto-generated OpenAPI/Swagger spec, seedable/resettable test data, `/health` + `/ready` endpoints.
- Everything containerized: one `docker compose up`.

## Stack (locked)
| Layer | Choice |
|---|---|
| Backend/API | FastAPI |
| DB | PostgreSQL (Dockerized) |
| ORM/Migrations | SQLAlchemy + Alembic |
| Auth | JWT access token, role-based (user/admin) |
| Frontend | Jinja2 server-rendered templates + small vanilla JS (fetch-driven cart badge for async UI-testing practice) |
| Styling | One small hand-written CSS file (~100-150 lines), no framework. Not beautiful, but properly laid out |
| Reverse proxy | Nginx (optional, in compose) |
| Public deploy | Render (free tier: Docker web service + free Postgres, auto-deploy from GitHub) |

## Styling (basic CSS, not raw HTML)
"Not beautiful" does NOT mean unstyled. Include a single small hand-written CSS file that provides:
- Clean header/nav, centered content container, readable fonts + spacing
- Product cards in a simple grid; forms with proper labels/spacing; styled cart/order tables
- Basic buttons, a cart badge, color-coded status labels (e.g. green = DELIVERED)
- No Tailwind/Bootstrap, no JS framework. Think "functional internal tool," not "landing page."
- Bonus: clean, clearly-placed elements + stable `data-testid`s keep Playwright selectors simple.

## Environments
- **Local (Docker Compose):** day-to-day fast test loop; the ONLY place load testing runs (see automation plan).
- **Public (Render):** target of the CI/CD "deploy only if green" gate; a real deployed environment for smoke/E2E runs.

## Core features (MVP)
**User**
- Register / login / logout (JWT)
- Browse catalog + product detail
- Cart: add / update qty / remove
- Checkout -> order (mock payment: succeeds by default; a "fail card" triggers failure for negative tests)
- View my orders + order detail with status timeline

**Admin**
- Admin login (separate role)
- View all orders
- Advance status: PLACED -> PACKING -> IN_TRANSIT -> DELIVERED (+ CANCELLED)
- Basic product management (create/edit/stock)

**System**
- `/health`, `/ready`
- `/api/test/reset`, `/api/test/seed` (guarded, test-env only) for deterministic automation
- Swagger UI at `/docs`

## Data model
- users (id, email, password_hash, role)
- products (id, name, price, stock, description)
- carts / cart_items
- orders (id, user_id, status, total, created_at)
- order_items
- order_status_history (timeline / admin transitions)

## API surface (sample)
```
POST /api/auth/register        POST /api/auth/login
GET  /api/products             GET  /api/products/{id}
GET  /api/cart                 POST /api/cart/items    PATCH /api/cart/items/{id}   DELETE /api/cart/items/{id}
POST /api/checkout             GET  /api/orders        GET  /api/orders/{id}
# admin
GET   /api/admin/orders        PATCH /api/admin/orders/{id}/status
POST  /api/admin/products      PATCH /api/admin/products/{id}
```

## Build milestones
1. Project skeleton + Docker + Postgres + health endpoint
2. Auth + users/roles
3. Products + catalog pages
4. Cart + checkout + orders
5. Admin order lifecycle
6. Seed/reset endpoints + Swagger + data-testid pass
7. Polish: negative paths (out-of-stock, bad payment, unauthorized)
