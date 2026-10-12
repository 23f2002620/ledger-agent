import json
from data_fetcher import fetch_rates, fetch_all_orders
from order_processor import process_orders
from question_parser import parse_question
from query_engine import compute_answer

# Initialize data
print("Fetching currency rates...")
rates = fetch_rates()
print(f"Fetched rates: {rates}")

print("Fetching all orders...")
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

for question in test_queries:
    print(f"\n{'='*60}")
    print(f"Testing question: {question}")
    print('='*60)

    # Parse the question
    parsed = parse_question(question)
    print(f"Parsed: {json.dumps(parsed, indent=2, default=str)}")

    # Compute the answer
    answer = compute_answer(processed_orders, parsed)
    print(f"Answer: {answer}")

    # Let's also manually verify some aspects for the first query
    if "How many different customers placed at least one paid order for a Toaster?" in question:
        # Manual verification
        toaster_orders = [o for o in processed_orders if o['product'].lower() == 'toaster' and o['status'] == 'paid']
        unique_customers = set(o['customer'] for o in toaster_orders)
        print(f"Manual verification - Toaster paid orders: {len(toaster_orders)}")
        print(f"Manual verification - Unique customers: {len(unique_customers)}")
        print(f"Customer IDs: {sorted(unique_customers)}")

    elif "What is the average paid order value in USD for the South region?" in question:
        # Manual verification
        south_paid_orders = [o for o in processed_orders if o['region'].lower() == 'south' and o['status'] == 'paid']
        if south_paid_orders:
            total_value = sum(o['amount_usd'] for o in south_paid_orders)
            avg_value = total_value / len(south_paid_orders)
            print(f"Manual verification - South paid orders: {len(south_paid_orders)}")
            print(f"Manual verification - Total value: {total_value:.2f}")
            print(f"Manual verification - Average value: {avg_value:.2f}")
        else:
            print("Manual verification - No south paid orders found")

    elif "How many distinct customers have bought a Grinder (paid orders only)?" in question:
        # Manual verification
        grinder_orders = [o for o in processed_orders if o['product'].lower() == 'grinder' and o['status'] == 'paid']
        unique_customers = set(o['customer'] for o in grinder_orders)
        print(f"Manual verification - Grinder paid orders: {len(grinder_orders)}")
        print(f"Manual verification - Unique customers: {len(unique_customers)}")
        print(f"Customer IDs: {sorted(unique_customers)}")