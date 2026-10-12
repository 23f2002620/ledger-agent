from datetime import datetime
from typing import List, Dict, Any, Optional

def filter_orders(
    orders: List[Dict[str, Any]],
    region: Optional[str] = None,
    product: Optional[str] = None,
    customer: Optional[str] = None,
    status: Optional[str] = None,
    time_start: Optional[datetime] = None,
    time_end: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Filter orders based on the given criteria.

    All string comparisons are case-insensitive.
    Time filtering uses the 'created_at' field.

    Args:
        orders: List of processed order dictionaries.
        region: Region name (e.g., 'North').
        product: Product name (e.g., 'Blender').
        customer: Customer ID (e.g., 'C1055').
        status: Order status (e.g., 'paid').
        time_start: Inclusive lower bound for created_at.
        time_end: Inclusive upper bound for created_at.

    Returns:
        List of orders matching all criteria.
    """
    filtered = orders
    if region:
        filtered = [o for o in filtered if o['region'].lower() == region.lower()]
    if product:
        filtered = [o for o in filtered if o['product'].lower() == product.lower()]
    if customer:
        filtered = [o for o in filtered if o['customer'].lower() == customer.lower()]
    if status:
        filtered = [o for o in filtered if o['status'].lower() == status.lower()]
    if time_start:
        filtered = [o for o in filtered if o['created_at'] >= time_start]
    if time_end:
        filtered = [o for o in filtered if o['created_at'] <= time_end]
    return filtered