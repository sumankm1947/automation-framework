"""Test-support endpoints for automation: reset and seed the database.

These routes are DESTRUCTIVE and are only mounted when APP_ENV=test (see
app/main.py). They give the test suite a fast, deterministic way to get a clean,
known state between runs — never exposed in local/production.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    OrderStatusHistory,
    Product,
    User,
)
from app.seed import seed_admin, seed_products, seed_standard_user

router = APIRouter(prefix="/api/test", tags=["test-support"])

# Child-to-parent order so foreign keys are never violated during a wipe.
_WIPE_ORDER = [OrderStatusHistory, OrderItem, Order, CartItem, Cart, User, Product]


def _counts(db: Session) -> dict[str, int]:
    return {
        "users": db.scalar(select(func.count()).select_from(User)) or 0,
        "products": db.scalar(select(func.count()).select_from(Product)) or 0,
        "orders": db.scalar(select(func.count()).select_from(Order)) or 0,
    }


def _seed_baseline(db: Session) -> None:
    seed_admin(db)
    seed_standard_user(db)
    seed_products(db)


@router.post("/reset")
def reset(db: Session = Depends(get_db)) -> dict[str, object]:
    """Delete all data, then re-seed the baseline admin, test user, and catalog."""
    for model in _WIPE_ORDER:
        db.execute(delete(model))
    db.commit()
    _seed_baseline(db)
    return {"status": "reset", "counts": _counts(db)}


@router.post("/seed")
def seed(db: Session = Depends(get_db)) -> dict[str, object]:
    """Ensure the baseline admin, test user, and catalog exist (idempotent)."""
    _seed_baseline(db)
    return {"status": "seeded", "counts": _counts(db)}
