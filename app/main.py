"""FastAPI application factory.

Milestone 1 wires up the app, health/readiness probes, and creates tables
on startup. Later milestones register auth, product, cart, order, and admin
routers here.
"""
from fastapi import FastAPI
from sqlalchemy import text

from app.config import get_settings
from app.database import Base, engine

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.app_name} API",
        description="Deliberately simple e-commerce app built as an SDET test target.",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    @app.on_event("startup")
    def on_startup() -> None:
        # For the portfolio app we create tables directly on startup; Alembic
        # migrations are layered in a later milestone.
        Base.metadata.create_all(bind=engine)

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

    return app


app = create_app()
