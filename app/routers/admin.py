"""Admin API: order lifecycle control and product management.

Every route requires an admin (via `require_admin`), so non-admins get 403
and unauthenticated callers get 401.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import services
from app.database import get_db
from app.deps import require_admin
from app.models import Order, Product, User
from app.schemas import (
    AdminOrderSummary,
    OrderPublic,
    OrderStatusUpdate,
    ProductCreate,
    ProductPublic,
    ProductUpdate,
)

router = APIRouter(
    prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)]
)


# --- Orders -------------------------------------------------------------
@router.get("/orders", response_model=list[AdminOrderSummary])
def list_all_orders(db: Session = Depends(get_db)) -> list[AdminOrderSummary]:
    rows = db.execute(
        select(Order, User.email).join(User, Order.user_id == User.id).order_by(Order.id.desc())
    ).all()
    return [
        AdminOrderSummary(
            id=order.id,
            user_id=order.user_id,
            user_email=email,
            status=order.status,
            total_cents=order.total_cents,
            created_at=order.created_at,
        )
        for order, email in rows
    ]


@router.get("/orders/{order_id}", response_model=OrderPublic)
def get_any_order(order_id: int, db: Session = Depends(get_db)) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.patch("/orders/{order_id}/status", response_model=OrderPublic)
def update_order_status(
    order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)
) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return services.advance_order_status(db, order, payload.status)


# --- Products -----------------------------------------------------------
@router.post("/products", response_model=ProductPublic, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    if db.scalar(select(Product).where(Product.sku == payload.sku)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/products/{product_id}", response_model=ProductPublic)
def update_product(
    product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)
) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product
