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
from app.models import Product, Role, User
from app.security import hash_password

settings = get_settings()

# Deterministic catalog so the UI/API always has stable data for tests.
# (sku, name, description, price_cents, stock, emoji)
_PRODUCTS: list[tuple[str, str, str, int, int, str]] = [
    ("SKU-TSHIRT", "Cotton T-Shirt", "Soft crew-neck cotton tee.", 1999, 50, "👕"),
    ("SKU-MUG", "Ceramic Mug", "11oz ceramic mug, dishwasher safe.", 1299, 30, "☕"),
    ("SKU-NOTEBOOK", "Dotted Notebook", "A5 dotted notebook, 120 pages.", 899, 100, "📓"),
    ("SKU-HEADPHONES", "Wireless Headphones", "Over-ear Bluetooth headphones.", 8999, 15, "🎧"),
    ("SKU-BOTTLE", "Steel Water Bottle", "750ml insulated bottle.", 2499, 40, "🍶"),
    ("SKU-BACKPACK", "Everyday Backpack", "20L water-resistant backpack.", 5499, 8, "🎒"),
    ("SKU-PEN", "Gel Pen (3-pack)", "0.5mm smooth-writing gel pens.", 499, 0, "🖊️"),
    ("SKU-CAP", "Baseball Cap", "Adjustable cotton cap.", 1599, 25, "🧢"),
]


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


def seed_products(db: Session) -> None:
    """Insert the default catalog for any SKU not already present."""
    existing_skus = set(db.scalars(select(Product.sku)).all())
    for sku, name, description, price_cents, stock, emoji in _PRODUCTS:
        if sku in existing_skus:
            continue
        db.add(
            Product(
                sku=sku,
                name=name,
                description=description,
                price_cents=price_cents,
                stock=stock,
                image_emoji=emoji,
            )
        )
    db.commit()


def run_seed() -> None:
    """Open a session and run all idempotent seeders."""
    db = SessionLocal()
    try:
        seed_admin(db)
        seed_products(db)
    finally:
        db.close()
