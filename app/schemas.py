"""Pydantic request/response schemas (the API contract).

Kept separate from ORM models so the wire format is explicit and stable for
contract testing.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field

from app.models import OrderStatus, Role


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """User as exposed by the API — never includes the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: Role
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductPublic(BaseModel):
    """Product as exposed by the catalog API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    description: str
    price_cents: int
    stock: int
    image_emoji: str

    @property
    def in_stock(self) -> bool:  # convenience for templates
        return self.stock > 0


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    description: str = ""
    price_cents: int = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    image_emoji: str = Field(default="📦", max_length=8)


class ProductUpdate(BaseModel):
    """Partial update — only provided fields change."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price_cents: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    image_emoji: str | None = Field(default=None, max_length=8)


# --- Cart ---
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=100)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=100)


class CartItemPublic(BaseModel):
    id: int
    product_id: int
    name: str
    image_emoji: str
    unit_price_cents: int
    quantity: int
    line_total_cents: int


class CartPublic(BaseModel):
    items: list[CartItemPublic]
    item_count: int
    total_cents: int


# --- Checkout + Orders ---
class CheckoutRequest(BaseModel):
    # Mock payment: any card number ending in FAIL_CARD_SUFFIX is declined.
    card_number: str = Field(min_length=4, max_length=32)


class OrderItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int | None
    product_name: str
    unit_price_cents: int
    quantity: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def line_total_cents(self) -> int:
        return self.unit_price_cents * self.quantity


class OrderStatusEventPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: OrderStatus
    created_at: datetime


class OrderSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: OrderStatus
    total_cents: int
    created_at: datetime


class OrderPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: OrderStatus
    total_cents: int
    created_at: datetime
    items: list[OrderItemPublic]
    history: list[OrderStatusEventPublic]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class AdminOrderSummary(BaseModel):
    """Order row for the admin list, including who placed it."""

    id: int
    user_id: int
    user_email: str
    status: OrderStatus
    total_cents: int
    created_at: datetime
