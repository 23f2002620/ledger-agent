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
            'product': 'Rice Cooker',
            'customer': 'C001',
            'status': 'paid',
            'region': 'North',
            'created_at': '2026-05-15T10:30:00+05:30',
            'updated_at': '2026-05-15T10:30:00+05:30'
        },
        {
            'id': '2',
            'amount': '150.0',
            'currency': 'USD',
            'product': 'Rice Cooker',
            'customer': 'C001',  # Same customer as above
            'status': 'paid',
            'region': 'North',
            'created_at': '2026-05-16T11:30:00+05:30',
            'updated_at': '2026-05-16T11:30:00+05:30'
        },
        {
            'id': '3',
            'amount': '200.0',
            'currency': 'USD',
            'product': 'Rice Cooker',
            'customer': 'C002',
            'status': 'paid',
            'region': 'South',
            'created_at': '2026-05-17T12:30:00+05:30',
            'updated_at': '2026-05-17T12:30:00+05:30'
        },
        {
            'id': '4',
            'amount': '75.0',
            'currency': 'USD',
            'product': 'Toaster',
            'customer': 'C003',
            'status': 'refunded',
            'region': 'North',
            'created_at': '2026-05-18T09:30:00+05:30',
            'updated_at': '2026-05-18T09:30:00+05:30'
        },
        {
            'id': '5',
            'amount': '100.0',
            'currency': 'USD',
            'product': 'Blender',
            'customer': 'C004',
            'status': 'refunded',
            'region': 'North',
            'created_at': '2026-05-19T10:30:00+05:30',
            'updated_at': '2026-05-19T10:30:00+05:30'
        },
        {
            'id': '6',
            'amount': '50.0',
            'currency': 'USD',
            'product': 'Rice Cooker',
            'customer': 'C005',
            'status': 'paid',
            'region': 'Central',
            'created_at': '2026-05-20T11:30:00+05:30',
            'updated_at': '2026-05-20T11:30:00+05:30'
        },
        {
            'id': '7',
            'amount': '200.0',
            'currency': 'USD',
            'product': 'Rice Cooker',
            'customer': 'C006',
            'status': 'paid',
            'region': 'Central',
            'created_at': '2026-05-21T12:30:00+05:30',
            'updated_at': '2026-05-21T12:30:00+05:30'
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
        "Count the refunded North orders placed in May 2026.",
        "On average, how many US dollars is a paid Central order worth?",
        "How many different customers placed at least one paid order for a Rice Cooker?"
    ]

    print("\n" + "="*60)
    print("TESTING NEW ERROR QUERIES WITH FIXES")
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
        if "Count the refunded North orders placed in May 2026." in question:
            # Should count refunded North orders in May 2026
            may_2026_refunded_north = [
                o for o in processed_orders
                if o['status'] == 'refunded'
                and o['region'].lower() == 'north'
                and o['created_at'].year == 2026
                and o['created_at'].month == 5
            ]
            expected = len(may_2026_refunded_north)
            print(f"Expected: {expected} (count of refunded North orders in May 2026)")
            print(f"Actual refunded North May orders: {len(may_2026_refunded_north)}")
            for o in may_2026_refunded_north:
                print(f"  - Order {o['id']}: {o['amount_usd']} USD, customer {o['customer']}")

        elif "On average, how many US dollars is a paid Central order worth?" in question:
            # Should compute average of paid Central orders
            paid_central = [
                o for o in processed_orders
                if o['status'] == 'paid'
                and o['region'].lower() == 'central'
            ]
            if paid_central:
                total = sum(o['amount_usd'] for o in paid_central)
                avg = total / len(paid_central)
                expected = round(avg, 2)
                print(f"Expected: {expected} (average of paid Central orders)")
                print(f"Paid Central orders: {len(paid_central)} orders, total: {total:.2f}")
                print(f"Order amounts: {[o['amount_usd'] for o in paid_central]}")
            else:
                expected = 0
                print(f"Expected: {expected} (no paid Central orders)")

        elif "How many different customers placed at least one paid order for a Rice Cooker?" in question:
            # Should count distinct customers who paid for Rice Cooker
            paid_rice_cooker = [
                o for o in processed_orders
                if o['status'] == 'paid'
                and o['product'].lower() == 'rice cooker'
            ]
            distinct_customers = len(set(o['customer'] for o in paid_rice_cooker))
            expected = distinct_customers
            print(f"Expected: {expected} (distinct customers who paid for Rice Cooker)")
            print(f"Paid Rice Cooker orders: {len(paid_rice_cooker)} orders from customers: {sorted(set(o['customer'] for o in paid_rice_cooker))}")

finally:
    # Restore original functions
    data_fetcher.fetch_rates = original_fetch_rates
    data_fetcher.fetch_all_orders = original_fetch_all_orders