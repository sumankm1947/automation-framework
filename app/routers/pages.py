"""Server-rendered HTML pages (Jinja2). Milestone 3: catalog + product detail."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.templating import templates

router = APIRouter(tags=["pages"], include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
def catalog_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    products = list(db.scalars(select(Product).order_by(Product.id)).all())
    return templates.TemplateResponse(
        request, "catalog.html", {"products": products, "title": "Catalog"}
    )


@router.get("/products/{product_id}", response_class=HTMLResponse)
def product_detail_page(
    request: Request, product_id: int, db: Session = Depends(get_db)
) -> HTMLResponse:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return templates.TemplateResponse(
        request, "product_detail.html", {"product": product, "title": product.name}
    )
