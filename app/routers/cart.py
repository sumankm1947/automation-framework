"""Cart API. All routes require an authenticated user and act on their cart."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import services
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import CartItemCreate, CartItemUpdate, CartPublic

router = APIRouter(prefix="/api/cart", tags=["cart"])


@router.get("", response_model=CartPublic)
def get_cart(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> CartPublic:
    cart = services.get_or_create_cart(db, current_user)
    return services.cart_to_public(cart)


@router.post("/items", response_model=CartPublic, status_code=201)
def add_cart_item(
    payload: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CartPublic:
    cart = services.get_or_create_cart(db, current_user)
    cart = services.add_item(db, cart, payload.product_id, payload.quantity)
    return services.cart_to_public(cart)


@router.patch("/items/{item_id}", response_model=CartPublic)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CartPublic:
    cart = services.get_or_create_cart(db, current_user)
    cart = services.update_item(db, cart, item_id, payload.quantity)
    return services.cart_to_public(cart)


@router.delete("/items/{item_id}", response_model=CartPublic)
def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CartPublic:
    cart = services.get_or_create_cart(db, current_user)
    cart = services.remove_item(db, cart, item_id)
    return services.cart_to_public(cart)
