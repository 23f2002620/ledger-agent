import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

# Asia/Kolkata is UTC+5:30
KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))

def process_orders(raw_orders: List[Dict[str, Any]], rates: Dict[str, float]) -> List[Dict[str, Any]]:
    """Process raw orders: deduplicate, convert currency, parse timestamps.

    Args:
        raw_orders: List of order dicts from the API.
        rates: Dict mapping currency code to USD per unit of that currency.

    Returns:
        List of processed order dicts with added fields:
            amount_usd: float
            created_at: datetime in KOLKATA_TZ
            updated_at: datetime in KOLKATA_TZ
    """
    # Step 1: Deduplicate by id, keeping the one with latest updated_at
    orders_by_id: Dict[str, Dict[str, Any]] = {}
    for order in raw_orders:
        order_id = order['id']
        # Parse the updated_at string to datetime for comparison
        # The API returns ISO format with timezone offset, e.g., "2024-08-12T10:30:00+05:30"
        # We'll parse it to datetime object (aware) and then convert to KOLKATA_TZ for consistency?
        # Actually, we can keep the datetime as is and compare using the same timezone.
        # We'll parse to datetime with timezone info.
        updated_str = order['updated_at']
        # If the string ends with Z, replace with +00:00
        if updated_str.endswith('Z'):
            updated_str = updated_str[:-1] + '+00:00'
        updated_dt = datetime.fromisoformat(updated_str)

        if order_id not in orders_by_id:
            orders_by_id[order_id] = order
        else:
            # Compare updated_at
            existing_updated_str = orders_by_id[order_id]['updated_at']
            if existing_updated_str.endswith('Z'):
                existing_updated_str = existing_updated_str[:-1] + '+00:00'
            existing_updated_dt = datetime.fromisoformat(existing_updated_str)
            if updated_dt > existing_updated_dt:
                orders_by_id[order_id] = order

    # Step 2: Convert each order
    processed_orders = []
    for order in orders_by_id.values():
        # Create a copy to avoid modifying the original dict (though we are done with raw)
        processed = order.copy()

        # Convert amount to USD
        currency = order['currency']
        amount = float(order['amount'])
        rate = rates.get(currency, 1.0)  # default to 1.0 if currency not found (should not happen)
        processed['amount_usd'] = amount * rate

        # Parse timestamps to datetime objects in KOLKATA_TZ
        for time_field in ['created_at', 'updated_at']:
            time_str = order[time_field]
            if time_str.endswith('Z'):
                time_str = time_str[:-1] + '+00:00'
            dt = datetime.fromisoformat(time_str)
            # Convert to KOLKATA_TZ
            dt_kolkata = dt.astimezone(KOLKATA_TZ)
            processed[time_field] = dt_kolkata

        processed_orders.append(processed)

    return processed_orders