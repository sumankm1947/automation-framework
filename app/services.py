"""Business logic shared by routes: cart math, mock payment, checkout.

Milestone 4 covers cart totals, the mock-payment check, and the checkout
transaction. Milestone 5 adds the order-status state machine here.
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    OrderStatus,
    OrderStatusHistory,
    Product,
    User,
)
from app.schemas import CartItemPublic, CartPublic

settings = get_settings()


# --- Cart ---------------------------------------------------------------
def get_or_create_cart(db: Session, user: User) -> Cart:
    """Return the user's cart, creating an empty one on first use."""
    cart = db.scalar(select(Cart).where(Cart.user_id == user.id))
    if cart is None:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def cart_to_public(cart: Cart) -> CartPublic:
    """Build the API/response view of a cart with per-line and grand totals."""
    items: list[CartItemPublic] = []
    total = 0
    count = 0
    for item in cart.items:
        product = item.product
        line_total = product.price_cents * item.quantity
        total += line_total
        count += item.quantity
        items.append(
            CartItemPublic(
                id=item.id,
                product_id=product.id,
                name=product.name,
                image_emoji=product.image_emoji,
                unit_price_cents=product.price_cents,
                quantity=item.quantity,
                line_total_cents=line_total,
            )
        )
    return CartPublic(items=items, item_count=count, total_cents=total)


def _require_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def add_item(db: Session, cart: Cart, product_id: int, quantity: int) -> Cart:
    """Add a product to the cart or increase its quantity, capped at stock."""
    product = _require_product(db, product_id)
    existing = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == product_id
        )
    )
    desired = quantity + (existing.quantity if existing else 0)
    if product.stock < desired:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only {product.stock} in stock",
        )
    if existing:
        existing.quantity = desired
    else:
        db.add(CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity))
    db.commit()
    db.refresh(cart)
    return cart


def _require_owned_item(db: Session, cart: Cart, item_id: int) -> CartItem:
    item = db.get(CartItem, item_id)
    if item is None or item.cart_id != cart.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
        )
    return item


def update_item(db: Session, cart: Cart, item_id: int, quantity: int) -> Cart:
    """Set an item's quantity to an absolute value, capped at stock."""
    item = _require_owned_item(db, cart, item_id)
    if item.product.stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only {item.product.stock} in stock",
        )
    item.quantity = quantity
    db.commit()
    db.refresh(cart)
    return cart


def remove_item(db: Session, cart: Cart, item_id: int) -> Cart:
    """Remove an item from the cart."""
    item = _require_owned_item(db, cart, item_id)
    db.delete(item)
    db.commit()
    db.refresh(cart)
    return cart


# --- Payment + checkout -------------------------------------------------
def is_card_declined(card_number: str) -> bool:
    """Mock gateway: decline any card ending in the configured fail suffix."""
    return card_number.strip().endswith(settings.fail_card_suffix)


def checkout(db: Session, user: User, card_number: str) -> Order:
    """Turn the user's cart into an order: validate, charge, decrement, clear.

    Raises 400 (empty cart), 402 (payment declined), or 409 (insufficient
    stock). On success the cart is emptied and stock is decremented.
    """
    cart = get_or_create_cart(db, user)
    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty"
        )

    # Re-validate stock at checkout time (it may have changed since add).
    for item in cart.items:
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"'{item.product.name}' is out of stock",
            )

    if is_card_declined(card_number):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Payment declined"
        )

    total = sum(item.product.price_cents * item.quantity for item in cart.items)
    order = Order(user_id=user.id, status=OrderStatus.PLACED, total_cents=total)
    order.history.append(OrderStatusHistory(status=OrderStatus.PLACED))
    for item in cart.items:
        order.items.append(
            OrderItem(
                product_id=item.product.id,
                product_name=item.product.name,
                unit_price_cents=item.product.price_cents,
                quantity=item.quantity,
            )
        )
        item.product.stock -= item.quantity

    db.add(order)
    # Empty the cart now that its contents are captured on the order.
    for item in list(cart.items):
        db.delete(item)
    db.commit()
    db.refresh(order)
    return order
