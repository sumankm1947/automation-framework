"""Public catalog API: list products and fetch a single product."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.schemas import ProductPublic

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductPublic])
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    """Return the full catalog, ordered by id."""
    return list(db.scalars(select(Product).order_by(Product.id)).all())


@router.get("/{product_id}", response_model=ProductPublic)
def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    """Return a single product or 404 if it does not exist."""
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product
