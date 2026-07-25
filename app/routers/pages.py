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


# The pages below are client-rendered shells: the browser fetches data from the
# JSON API using the stored JWT (see static/js/app.js). They render regardless
# of auth; the client redirects to /login when no valid token is present.
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {"title": "Login"})


@router.get("/cart", response_class=HTMLResponse)
def cart_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "cart.html", {"title": "Your Cart"})


@router.get("/orders", response_class=HTMLResponse)
def orders_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "orders.html", {"title": "Your Orders"})


@router.get("/orders/{order_id}", response_class=HTMLResponse)
def order_detail_page(request: Request, order_id: int) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "order_detail.html", {"title": f"Order #{order_id}", "order_id": order_id}
    )
