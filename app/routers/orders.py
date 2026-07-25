"""Checkout and order-history API for the authenticated user."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import services
from app.database import get_db
from app.deps import get_current_user
from app.models import Order, User
from app.schemas import CheckoutRequest, OrderPublic, OrderSummary

router = APIRouter(prefix="/api", tags=["orders"])


@router.post("/checkout", response_model=OrderPublic, status_code=status.HTTP_201_CREATED)
def checkout(
    payload: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Order:
    return services.checkout(db, current_user, payload.card_number)


@router.get("/orders", response_model=list[OrderSummary])
def list_orders(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Order]:
    return list(
        db.scalars(
            select(Order)
            .where(Order.user_id == current_user.id)
            .order_by(Order.id.desc())
        ).all()
    )


@router.get("/orders/{order_id}", response_model=OrderPublic)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Order:
    order = db.get(Order, order_id)
    # 404 (not 403) for someone else's order so ids aren't enumerable.
    if order is None or order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
