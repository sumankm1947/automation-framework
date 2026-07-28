# Running the tests

Every layer points at a **run target** — the instance of the app under test.
Which target you use is controlled entirely by the `API_BASE_URL` env var
(read in `tests/conftest.py`, default `http://localhost:8000`).

| Layer | Run target | Needs a server? |
|---|---|---|
| Unit (`tests/unit/`) | none — imports `app.*` directly | no |
| API (`tests/api/`) | local Docker Compose, `APP_ENV=test` | yes |
| E2E (`tests/e2e/`) | local Docker Compose, `APP_ENV=test` | yes |
| Smoke (`-m smoke`) | the deployed Render URL | already running |
| Load (`load/`) | local Docker Compose **only** | yes |

API and E2E need `APP_ENV=test` because they use `POST /api/test/reset`, which is
only mounted in the test environment. They are destructive — never point them at
a deployed app. Smoke tests are read-only and safe against the deploy.

## Setup

```powershell
python -m venv .testvenv
.\.testvenv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
playwright install        # E2E only
```

## Start the app (needed for API / E2E / load)

```powershell
$env:APP_ENV="test"
docker compose up --build
```

App at `http://localhost:8000` · Swagger at `/docs`.

## Commands

```powershell
# Unit — no server required
pytest -m unit

# Unit with the coverage gate
pytest -m unit --cov=app --cov-fail-under=80

# API — local compose in APP_ENV=test
pytest -m api

# E2E — local compose in APP_ENV=test
pytest -m e2e

# Everything except load
pytest -m "not load"

# Smoke — against the deploy (read-only)
$env:API_BASE_URL="https://<your-app>.onrender.com"
pytest -m smoke
$env:API_BASE_URL=$null      # unset afterwards

# Load — local only, not pytest
locust -f load/locustfile.py --host http://localhost:8000
```

> Unset `API_BASE_URL` after a smoke run. A leftover value would aim the
> destructive suites at the deployed app.

## Seeded accounts

| Role | Email | Password | Available |
|---|---|---|---|
| admin | `admin@shoplite.com` | `admin12345` | every startup |
| user | `user@shoplite.com` | `user12345` | after reset/seed (test env only) |

Use the `fresh_user` fixture for tests that need their own isolated account.

## Fixtures (`tests/conftest.py`)

| Fixture | Scope | Purpose |
|---|---|---|
| `api_base_url` | session | target URL from `API_BASE_URL` |
| `api_client` | session | `requests`-based client with logging + timeout |
| `reset_db` | module | `POST /api/test/reset` — clean DB per test file |
| `admin_token` | module | admin JWT (depends on `reset_db`) |
| `user_token` | module | standard-user JWT (depends on `reset_db`) |
| `fresh_user` | function | factory → JWT for a brand-new random user |

`reset_db` wipes and re-seeds, so **user and product ids change after every
reset**. Look products up by SKU rather than hardcoding ids.

Token fixtures depend on `reset_db` so login always happens *after* the wipe.
Keep them at the same scope as `reset_db` — a wider fixture cannot request a
narrower one.
