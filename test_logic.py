# Test the logic with mock data to understand what's happening

def test_compute_answer_logic():
    # Mock processed orders data
    mock_orders = [
        # Toaster orders
        {'id': 1, 'product': 'Toaster', 'customer': 'C001', 'status': 'paid', 'amount_usd': 50.0, 'region': 'South'},
        {'id': 2, 'product': 'Toaster', 'customer': 'C001', 'status': 'paid', 'amount_usd': 60.0, 'region': 'South'},  # Same customer, another order
        {'id': 3, 'product': 'Toaster', 'customer': 'C002', 'status': 'paid', 'amount_usd': 55.0, 'region': 'North'},
        {'id': 4, 'product': 'Toaster', 'customer': 'C003', 'status': 'paid', 'amount_usd': 70.0, 'region': 'South'},
        {'id': 5, 'product': 'Toaster', 'customer': 'C001', 'status': 'refunded', 'amount_usd': 50.0, 'region': 'South'},  # Refunded, shouldn't count

        # Grinder orders
        {'id': 6, 'product': 'Grinder', 'customer': 'C001', 'status': 'paid', 'amount_usd': 100.0, 'region': 'South'},
        {'id': 7, 'product': 'Grinder', 'customer': 'C004', 'status': 'paid', 'amount_usd': 110.0, 'region': 'South'},
        {'id': 8, 'product': 'Grinder', 'customer': 'C005', 'status': 'paid', 'amount_usd': 90.0, 'region': 'East'},

        # Other orders
        {'id': 9, 'product': 'Blender', 'customer': 'C006', 'status': 'paid', 'amount_usd': 75.0, 'region': 'South'},
        {'id': 10, 'product': 'Blender', 'customer': 'C007', 'status': 'paid', 'amount_usd': 80.0, 'region': 'South'},
    ]

    # Mock filter_orders function (simplified)
    def filter_orders(orders, **kwargs):
        filtered = orders
        for key, value in kwargs.items():
            if value is not None:
                if key == 'region':
                    filtered = [o for o in filtered if o['region'].lower() == value.lower()]
                elif key == 'product':
                    filtered = [o for o in filtered if o['product'].lower() == value.lower()]
                elif key == 'customer':
                    filtered = [o for o in filtered if o['customer'].lower() == value.lower()]
                elif key == 'status':
                    filtered = [o for o in filtered if o['status'].lower() == value.lower()]
        return filtered

    # Mock compute_answer function (simplified version focusing on the problematic queries)
    def compute_answer(orders, parsed_question):
        intent = parsed_question['intent']
        filters = parsed_question['filters'].copy()
        group_by = parsed_question['group_by']
        limit = parsed_question['limit']

        # Set default status based on intent if not specified
        if intent in ['revenue', 'refunded_amount', 'top_product', 'top_customer']:
            if intent == 'revenue' and 'status' not in filters:
                filters['status'] = 'paid'
            elif intent == 'refunded_amount' and 'status' not in filters:
                filters['status'] = 'refunded'
            elif intent in ['top_product', 'top_customer'] and 'status' not in filters:
                filters['status'] = 'paid'

        # Filter the orders
        filtered_orders = filter_orders(orders, **filters)

        # Compute based on intent
        if intent in ['revenue', 'refunded_amount']:
            if group_by:
                groups = {}
                for order in filtered_orders:
                    key = order[group_by]
                    groups[key] = groups.get(key, 0) + order['amount_usd']
                if limit:
                    sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
                    if limit == 1:
                        top_key, top_value = sorted_groups[0]
                        answer = top_key
                    else:
                        answer = [key for key, _ in sorted_groups[:limit]]
                else:
                    answer = groups
            else:
                total = sum(order['amount_usd'] for order in filtered_orders)
                answer = round(total, 2)

        elif intent == 'order_count':
            if group_by:
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
            group_by = 'product'
            limit = 1
            groups = {}
            for order in filtered_orders:
                key = order[group_by]
                groups[key] = groups.get(key, 0) + order['amount_usd']
            sorted_groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
            top_key, _ = sorted_groups[0]
            answer = top_key

        elif intent == 'top_customer':
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
            answer = None

        return answer

    # Test queries
    test_cases = [
        {
            'question': "How many different customers placed at least one paid order for a Toaster?",
            'expected_intent': 'order_count',
            'expected_filters': {'product': 'Toaster', 'status': 'paid'},
            'expected_group_by': None,  # This is the issue - should we group by customer to count distinct?
            'expected_answer': 3  # C001, C002, C003 (C001 appears twice but should count once)
        },
        {
            'question': "What is the average paid order value in USD for the South region?",
            'expected_intent': 'revenue',  # Actually, this should be revenue then divide by count?
            'expected_filters': {'region': 'South', 'status': 'paid'},
            'expected_group_by': None,
            'expected_answer': None  # Need to calculate: sum of amounts / count of orders
        },
        {
            'question': "How many distinct customers have bought a Grinder (paid orders only)?",
            'expected_intent': 'order_count',
            'expected_filters': {'product': 'Grinder', 'status': 'paid'},
            'expected_group_by': None,
            'expected_answer': 3  # C001, C004, C005
        }
    ]

    print("Testing logic with mock data...")
    print("=" * 60)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['question']}")

        # Simulate parsing (simplified)
        parsed = {
            'intent': test_case['expected_intent'],
            'filters': test_case['expected_filters'],
            'group_by': test_case['expected_group_by'],
            'limit': None
        }

        print(f"  Parsed: {parsed}")

        # Compute answer
        answer = compute_answer(mock_orders, parsed)
        print(f"  Computed answer: {answer}")
        print(f"  Expected answer: {test_case['expected_answer']}")

        # Manual verification for clarity
        if i == 1:  # Toaster distinct customers
            toaster_paid = [o for o in mock_orders if o['product'].lower() == 'toaster' and o['status'] == 'paid']
            distinct_customers = len(set(o['customer'] for o in toaster_paid))
            print(f"  Manual verification - Toaster paid orders: {len(toaster_paid)}")
            print(f"  Manual verification - Distinct customers: {distinct_customers}")
            print(f"  Customer IDs: {sorted(set(o['customer'] for o in toaster_paid))}")

        elif i == 2:  # South region average
            south_paid = [o for o in mock_orders if o['region'].lower() == 'south' and o['status'] == 'paid']
            if south_paid:
                total = sum(o['amount_usd'] for o in south_paid)
                avg = total / len(south_paid)
                print(f"  Manual verification - South paid orders: {len(south_paid)}")
                print(f"  Manual verification - Total value: {total:.2f}")
                print(f"  Manual verification - Average value: {avg:.2f}")
            else:
                print("  Manual verification - No south paid orders")

        elif i == 3:  # Grinder distinct customers
            grinder_paid = [o for o in mock_orders if o['product'].lower() == 'grinder' and o['status'] == 'paid']
            distinct_customers = len(set(o['customer'] for o in grinder_paid))
            print(f"  Manual verification - Grinder paid orders: {len(grinder_paid)}")
            print(f"  Manual verification - Distinct customers: {distinct_customers}")
            print(f"  Customer IDs: {sorted(set(o['customer'] for o in grinder_paid))}")

if __name__ == "__main__":
    test_compute_answer_logic()