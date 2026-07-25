"""Pydantic request/response schemas (the API contract).

Kept separate from ORM models so the wire format is explicit and stable for
contract testing.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import Role


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
