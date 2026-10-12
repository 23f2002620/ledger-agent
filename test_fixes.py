import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Mock the data fetching functions to avoid API calls
def mock_fetch_rates():
    return {'USD': 1.0, 'INR': 0.012, 'EUR': 1.08}  # Simplified rates

def mock_fetch_all_orders():
    # Return a small set of mock orders for testing
    return [
        {
            'id': '1',
            'amount': '100.0',
            'currency': 'USD',
            'product': 'Toaster',
            'customer': 'C001',
            'status': 'paid',
            'region': 'South',
            'created_at': '2026-01-15T10:30:00+05:30',
            'updated_at': '2026-01-15T10:30:00+05:30'
        },
        {
            'id': '2',
            'amount': '150.0',
            'currency': 'USD',
            'product': 'Toaster',
            'customer': 'C001',  # Same customer as above
            'status': 'paid',
            'region': 'South',
            'created_at': '2026-01-16T11:30:00+05:30',
            'updated_at': '2026-01-16T11:30:00+05:30'
        },
        {
            'id': '3',
            'amount': '200.0',
            'currency': 'USD',
            'product': 'Toaster',
            'customer': 'C002',
            'status': 'paid',
            'region': 'North',
            'created_at': '2026-01-17T12:30:00+05:30',
            'updated_at': '2026-01-17T12:30:00+05:30'
        },
        {
            'id': '4',
            'amount': '75.0',
            'currency': 'USD',
            'product': 'Grinder',
            'customer': 'C003',
            'status': 'paid',
            'region': 'South',
            'created_at': '2026-01-18T09:30:00+05:30',
            'updated_at': '2026-01-18T09:30:00+05:30'
        },
        {
            'id': '5',
            'amount': '100.0',
            'currency': 'USD',
            'product': 'Grinder',
            'customer': 'C003',  # Same customer as above
            'status': 'paid',
            'region': 'South',
            'created_at': '2026-01-19T10:30:00+05:30',
            'updated_at': '2026-01-19T10:30:00+05:30'
        },
        {
            'id': '6',
            'amount': '50.0',
            'currency': 'USD',
            'product': 'Blender',
            'customer': 'C004',
            'status': 'paid',
            'region': 'South',
            'created_at': '2026-01-20T11:30:00+05:30',
            'updated_at': '2026-01-20T11:30:00+05:30'
        }
    ]

# Temporarily replace the fetching functions
import data_fetcher
import order_processor
original_fetch_rates = data_fetcher.fetch_rates
original_fetch_all_orders = data_fetcher.fetch_all_orders

data_fetcher.fetch_rates = mock_fetch_rates
data_fetcher.fetch_all_orders = mock_fetch_all_orders

try:
    from data_fetcher import fetch_rates, fetch_all_orders
    from order_processor import process_orders
    from question_parser import parse_question
    from query_engine import compute_answer

    # Initialize data with mocks
    print("Fetching currency rates (mock)...")
    rates = fetch_rates()
    print(f"Fetched rates: {rates}")

    print("Fetching all orders (mock)...")
    raw_orders = fetch_all_orders()
    print(f"Fetched {len(raw_orders)} raw orders")

    print("Processing orders...")
    processed_orders = process_orders(raw_orders, rates)
    print(f"Processed {len(processed_orders)} orders after deduplication")

    # Test the specific queries that were wrong
    test_queries = [
        "How many different customers placed at least one paid order for a Toaster?",
        "What is the average paid order value in USD for the South region?",
        "How many distinct customers have bought a Grinder (paid orders only)?"
    ]

    print("\n" + "="*60)
    print("TESTING QUERIES WITH FIXES")
    print("="*60)

    for question in test_queries:
        print(f"\nQuestion: {question}")
        print("-" * 50)

        # Parse the question
        parsed = parse_question(question)
        print(f"Parsed: {parsed}")

        # Compute the answer
        answer = compute_answer(processed_orders, parsed)
        print(f"Answer: {answer}")

        # Manual verification
        if "How many different customers placed at least one paid order for a Toaster?" in question:
            # Expected: 2 distinct customers (C001, C002) - C001 appears twice but should count once
            toaster_paid = [o for o in processed_orders if o['product'].lower() == 'toaster' and o['status'] == 'paid']
            distinct_customers = len(set(o['customer'] for o in toaster_paid))
            print(f"Expected: {distinct_customers} distinct customers")
            print(f"Toaster paid orders: {len(toaster_paid)} orders from customers: {sorted(set(o['customer'] for o in toaster_paid))}")

        elif "What is the average paid order value in USD for the South region?" in question:
            # Expected: average of South paid orders
            south_paid = [o for o in processed_orders if o['region'].lower() == 'south' and o['status'] == 'paid']
            if south_paid:
                total = sum(o['amount_usd'] for o in south_paid)
                avg = total / len(south_paid)
                print(f"Expected: {avg:.2f} average")
                print(f"South paid orders: {len(south_paid)} orders, total: {total:.2f}")
                print(f"Order amounts: {[o['amount_usd'] for o in south_paid]}")
            else:
                print("Expected: 0 (no South paid orders)")

        elif "How many distinct customers have bought a Grinder (paid orders only)?" in question:
            # Expected: 1 distinct customer (C003) - appears twice but should count once
            grinder_paid = [o for o in processed_orders if o['product'].lower() == 'grinder' and o['status'] == 'paid']
            distinct_customers = len(set(o['customer'] for o in grinder_paid))
            print(f"Expected: {distinct_customers} distinct customers")
            print(f"Grinder paid orders: {len(grinder_paid)} orders from customers: {sorted(set(o['customer'] for o in grinder_paid))}")

finally:
    # Restore original functions
    data_fetcher.fetch_rates = original_fetch_rates
    data_fetcher.fetch_all_orders = original_fetch_all_orders