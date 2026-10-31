
from app.database import get_all_orders


def fetch_orders():
    """Fetch orders using the database layer."""
    return get_all_orders()


def calculate_total():
    return sum([100, 200])