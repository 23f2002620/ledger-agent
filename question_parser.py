import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
import calendar

# Asia/Kolkata timezone offset
KOLKATA_TZ = timezone(timedelta(seconds=19800))  # 5*3600 + 30*60 = 19800

def parse_question(question: str) -> Dict[str, Any]:
    """Parse a natural language question into a structured query.

    Args:
        question: The question string.

    Returns:
        A dictionary with keys:
            intent: str (one of 'revenue', 'refunded_amount', 'order_count', 'top_product', 'top_customer')
            filters: dict with optional keys 'region', 'product', 'customer', 'status', 'time_start', 'time_end'
            group_by: Optional[str] ('product', 'customer', or None)
            limit: Optional[int] (for top-N queries)
    """
    q_lower = question.lower()

    # Initialize result
    result = {
        'intent': None,
        'filters': {},
        'group_by': None,
        'limit': None,
        'distinct': False,  # Whether to count distinct customers
        'average': False    # Whether to compute average instead of sum
    }

    # 1. Detect count questions (priority when question is about counting)
    if q_lower.startswith('how many') or q_lower.startswith('number of') or q_lower.startswith('what is the number of'):
        result['intent'] = 'order_count'

    # 2. Detect top customer / product patterns (which customer had the highest revenue, etc.)
    # Pattern: which customer had the highest revenue
    if ('which customer' in q_lower or 'which customer' in q_lower) and ('highest' in q_lower or 'most' in q_lower) and ('revenue' in q_lower or 'total' in q_lower or 'amount' in q_lower):
        result['intent'] = 'revenue'
        result['group_by'] = 'customer'
        result['limit'] = 1
    # Pattern: which product had the highest revenue
    elif ('which product' in q_lower or 'which product' in q_lower) and ('highest' in q_lower or 'most' in q_lower) and ('revenue' in q_lower or 'total' in q_lower or 'amount' in q_lower):
        result['intent'] = 'revenue'
        result['group_by'] = 'product'
        result['limit'] = 1

    # 3. Detect top-selling / top selling product by revenue patterns
    # Patterns like: "top-selling product by revenue", "top selling product by revenue", "top product by revenue"
    if ('top-selling' in q_lower or 'top selling' in q_lower or 'top product' in q_lower) and ('by revenue' in q_lower or 'by total' in q_lower or 'by amount' in q_lower):
        result['intent'] = 'revenue'
        result['group_by'] = 'product'
        result['limit'] = 1
    # Also handle "top-selling [product] by revenue" without the word "product" explicitly?
    # We'll rely on the product extraction later to set the group_by if needed, but we already set group_by to product above.
    # If the above didn't match, we can also look for "top-selling" and "revenue" and assume we want top product by revenue.
    elif ('top-selling' in q_lower or 'top selling' in q_lower) and ('revenue' in q_lower or 'total' in q_lower or 'amount' in q_lower):
        result['intent'] = 'revenue'
        result['group_by'] = 'product'
        result['limit'] = 1

    # 4. Detect intent based on keywords (if not already set)
    if result['intent'] is None:
        if any(word in q_lower for word in ['revenue', 'sales', 'income', 'total amount']):
            result['intent'] = 'revenue'
        elif any(word in q_lower for word in ['refunded', 'refund', 'returned']):
            result['intent'] = 'refunded_amount'
        elif any(word in q_lower for word in ['count', 'number of', 'how many']):
            result['intent'] = 'order_count'
        elif 'top customer' in q_lower or 'highest spending customer' in q_lower or 'most valuable customer' in q_lower:
            result['intent'] = 'top_customer'
        elif 'top product' in q_lower or 'best selling' in q_lower or 'most popular product' in q_lower or 'highest revenue product' in q_lower:
            result['intent'] = 'top_product'
        else:
            # Default to revenue if unclear
            result['intent'] = 'revenue'

    # 4.5. Detect distinct/different modifiers (for counting distinct customers)
    if result['intent'] == 'order_count':
        # Check for words that indicate we want distinct/customers counted uniquely
        distinct_indicators = ['different', 'distinct', 'unique']
        if any(indicator in q_lower for indicator in distinct_indicators):
            # Additionally, check if the question is about customers
            if 'customer' in q_lower:
                result['distinct'] = True

    # 4.6. Detect average modifier
    average_indicators = ['average', 'avg', 'mean']
    if any(indicator in q_lower for indicator in average_indicators):
        # For average, we typically want to compute average of amounts
        # This applies to revenue-like queries
        if result['intent'] in ['revenue', 'refunded_amount']:
            result['average'] = True

    # 5. Extract region
    import re
    regions = ['north', 'south', 'east', 'west', 'central']
    for region in regions:
        # Use word boundary regex to avoid matching substrings (e.g., "east" in "toaster")
        if re.search(r'\b' + re.escape(region) + r'\b', q_lower):
            result['filters']['region'] = region.capitalize()  # Store as proper case
            break

    # 6. Extract product: look for known product names
    known_products = ['Blender', 'Mixer', 'Kettle', 'Air Fryer', 'Juicer', 'Grinder', 'Toaster']
    for product in known_products:
        if product.lower() in q_lower:
            result['filters']['product'] = product
            break

    # 7. Extract customer
    # Look for pattern C followed by digits
    customer_match = re.search(r'\b(C\d+)\b', question, re.IGNORECASE)
    if customer_match:
        result['filters']['customer'] = customer_match.group(1).upper()
    else:
        # Look for "customer" keyword
        if 'customer' in q_lower:
            # Try to extract the customer ID after the keyword
            # Simplified: look for a word that looks like a customer ID after "customer"
            match = re.search(r'customer\s+(C\d+)', q_lower, re.IGNORECASE)
            if match:
                result['filters']['customer'] = match.group(1).upper()

    # 8. Extract status
    statuses = ['paid', 'refunded', 'void']
    for status in statuses:
        if status in q_lower:
            result['filters']['status'] = status
            break

    # 9. Extract time range
    time_start, time_end = _extract_time_range(q_lower)
    if time_start:
        result['filters']['time_start'] = time_start
    if time_end:
        result['filters']['time_end'] = time_end

    # 10. Extract grouping (only if not already set by top patterns)
    if result['group_by'] is None:
        if 'per product' in q_lower or 'by product' in q_lower:
            result['group_by'] = 'product'
        elif 'per customer' in q_lower or 'by customer' in q_lower:
            result['group_by'] = 'customer'

    # 11. Extract limit for top-N queries (only if not already set by top patterns)
    if result['limit'] is None:
        # Look for patterns like "top 5", "top 10", "highest 3"
        limit_match = re.search(r'(?:top|highest)\s+(\d+)', q_lower)
        if limit_match:
            result['limit'] = int(limit_match.group(1))
        # Also look for "the top" or "the highest"
        elif 'top' in q_lower or 'highest' in q_lower:
            # Default to 1 if just "top" or "highest"
            result['limit'] = 1

    return result

def _extract_time_range(text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Extract time range from the question text.

    Returns a tuple (start_time, end_time) as datetime objects in KOLKATA_TZ.
    If no time expression is found, returns (None, None).
    """
    # We'll handle a few common patterns
    # 1. Month Year: e.g., "march 2026"
    month_year_match = re.search(r'(\w+)\s+(\d{4})', text)
    if month_year_match:
        month_str = month_year_match.group(1).lower()
        year = int(month_year_match.group(2))
        try:
            month = list(calendar.month_name).index(month_str.capitalize())
        except ValueError:
            # Try abbreviated month
            try:
                month = list(calendar.month_abbr).index(month_str.capitalize())
            except ValueError:
                month = None
        if month:
            # First day of the month at 00:00:00 in KOLKATA_TZ
            start = datetime(year, month, 1, tzinfo=KOLKATA_TZ)
            # Last day of the month at 23:59:59.999999
            if month == 12:
                end = datetime(year+1, 1, 1, tzinfo=KOLKATA_TZ) - timedelta(microseconds=1)
            else:
                end = datetime(year, month+1, 1, tzinfo=KOLKATA_TZ) - timedelta(microseconds=1)
            return start, end

    # 2. Year only: e.g., "in 2026"
    year_match = re.search(r'in\s+(\d{4})', text)
    if year_match:
        year = int(year_match.group(1))
        start = datetime(year, 1, 1, tzinfo=KOLKATA_TZ)
        end = datetime(year+1, 1, 1, tzinfo=KOLKATA_TZ) - timedelta(microseconds=1)
        return start, end

    # 3. Relative: last month, past week, today, yesterday
    now = datetime.now(KOLKATA_TZ)
    if 'last month' in text:
        # First day of previous month
        if now.month == 1:
            start = datetime(now.year-1, 12, 1, tzinfo=KOLKATA_TZ)
            end = datetime(now.year, 1, 1, tzinfo=KOLKATA_TZ) - timedelta(microseconds=1)
        else:
            start = datetime(now.year, now.month-1, 1, tzinfo=KOLKATA_TZ)
            end = datetime(now.year, now.month, 1, tzinfo=KOLKATA_TZ) - timedelta(microseconds=1)
        return start, end
    if 'past week' in text or 'last week' in text:
        start = now - timedelta(days=7)
        end = now
        return start, end
    if 'today' in text:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end
    if 'yesterday' in text:
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end

    # If no time expression found, return None, None
    return None, None