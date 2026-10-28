
from fastapi import APIRouter
from app.services.services import fetch_orders

router = APIRouter()


@router.get("/orders")
def get_orders():
    """Handle requests to the orders API."""
    return fetch_orders()
