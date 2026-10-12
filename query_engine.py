from typing import List, Dict, Any, Optional
from indexer import filter_orders

def compute_answer(
    orders: List[Dict[str, Any]],
    parsed_question: Dict[str, Any]
) -> Any:
    """Compute the answer to the parsed question.

    Args:
        orders: List of processed order dictionaries.
        parsed_question: Output from parse_question.

    Returns:
        The answer as a number, string, list, or dict.
    """
    intent = parsed_question['intent']
    filters = parsed_question['filters'].copy()
    group_by = parsed_question['group_by']
    limit = parsed_question['limit']
    distinct = parsed_question.get('distinct', False)
    average = parsed_question.get('average', False)

    # Set default status based on intent if not specified
    if intent in ['revenue', 'refunded_amount', 'top_product', 'top_customer']:
        if intent == 'revenue' and 'status' not in filters:
            filters['status'] = 'paid'
        elif intent == 'refunded_amount' and 'status' not in filters:
            filters['status'] = 'refunded'
        elif intent in ['top_product', 'top_customer'] and 'status' not in filters:
            # These are revenue-like queries, so default to paid
            filters['status'] = 'paid'
    # For order_count, we leave status as is (could be None meaning all statuses)

    # Filter the orders
    filtered_orders = filter_orders(orders, **filters)

    # Compute based on intent
    if intent in ['revenue', 'refunded_amount']:
        if group_by:
            # Group by the specified field and sum amount_usd
            groups = {}
            for order in filtered_orders:
                key = order[group_by]
                groups[key] = groups.get(key, 0) + order['amount_usd']
            if limit:
                # Sort descending by sum
                sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
                if limit == 1:
                    top_key, top_value = sorted_groups[0]
                    # For top-1, return the key (product or customer) as the answer
                    answer = top_key
                else:
                    # Return list of top N keys
                    answer = [key for key, _ in sorted_groups[:limit]]
            else:
                # No limit, return the groups dict
                answer = groups
        else:
            # No grouping, compute sum or average
            total = sum(order['amount_usd'] for order in filtered_orders)
            if average:
                # Compute average: total / count
                count = len(filtered_orders)
                answer = round(total / count, 2) if count > 0 else 0
            else:
                # No grouping, just sum
                answer = round(total, 2)  # two decimal places for currency

    elif intent == 'order_count':
        if distinct:
            # Count distinct customers (regardless of group_by)
            unique_customers = set(order['customer'] for order in filtered_orders)
            answer = len(unique_customers)
        elif group_by:
            # Group by and count
            groups = {}
            for order in filtered_orders:
                key = order[group_by]
                groups[key] = groups.get(key, 0) + 1
            if limit:
                sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
                if limit == 1:
                    top_key, _ = sorted_groups[0]
                    answer = top_key
                else:
                    answer = [key for key, _ in sorted_groups[:limit]]
            else:
                answer = groups
        else:
            answer = len(filtered_orders)

    elif intent == 'top_product':
        # Treat as revenue grouped by product with limit=1
        group_by = 'product'
        limit = 1
        # Reuse the revenue block
        groups = {}
        for order in filtered_orders:
            key = order[group_by]
            groups[key] = groups.get(key, 0) + order['amount_usd']
        sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
        top_key, _ = sorted_groups[0]
        answer = top_key

    elif intent == 'top_customer':
        # Treat as revenue grouped by customer with limit=1
        group_by = 'customer'
        limit = 1
        groups = {}
        for order in filtered_orders:
            key = order[group_by]
            groups[key] = groups.get(key, 0) + order['amount_usd']
        sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
        top_key, _ = sorted_groups[0]
        answer = top_key

    else:
        # Fallback
        answer = None

    return answer