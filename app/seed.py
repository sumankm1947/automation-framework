"""Idempotent seeding helpers run on startup.

Milestone 2 seeds a default admin so the API always has an admin account for
manual exploration and automated tests. Later milestones extend seeding with
catalog/product data.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import Role, User
from app.security import hash_password

settings = get_settings()


def seed_admin(db: Session) -> None:
    """Create the default admin account if it does not already exist."""
    existing = db.scalar(select(User).where(User.email == settings.admin_email))
    if existing is not None:
        return
    db.add(
        User(
            email=settings.admin_email,
            password_hash=hash_password(settings.admin_password),
            role=Role.admin,
        )
    )
    db.commit()


def run_seed() -> None:
    """Open a session and run all idempotent seeders."""
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()
