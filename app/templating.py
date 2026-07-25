"""Shared Jinja2 templates environment and helpers."""
from __future__ import annotations

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


def format_price(cents: int) -> str:
    """Render integer cents as a dollar string, e.g. 1999 -> '$19.99'."""
    return f"${cents / 100:,.2f}"


templates.env.filters["price"] = format_price
