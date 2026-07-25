"""FastAPI application factory.

Milestone 1 wires up the app, health/readiness probes, and creates tables
on startup. Later milestones register auth, product, cart, order, and admin
routers here.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import get_settings
from app.database import Base, engine
from app.routers import admin, auth, cart, orders, pages, products

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.app_name} API",
        description="Deliberately simple e-commerce app built as a test-automation target.",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    @app.on_event("startup")
    def on_startup() -> None:
        # For the portfolio app we create tables directly on startup; Alembic
        # migrations are layered in a later milestone.
        Base.metadata.create_all(bind=engine)
        # Ensure a default admin exists (idempotent).
        from app.seed import run_seed

        run_seed()

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        """Liveness probe — the process is up. No dependency checks."""
        return {"status": "ok"}

    @app.get("/ready", tags=["system"])
    def ready() -> dict[str, str]:
        """Readiness probe — the app can reach its database."""
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            return {"status": "not-ready", "database": "unreachable"}
        return {"status": "ready", "database": "ok"}

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.include_router(auth.router)
    app.include_router(products.router)
    app.include_router(cart.router)
    app.include_router(orders.router)
    app.include_router(admin.router)
    app.include_router(pages.router)

    return app


app = create_app()
