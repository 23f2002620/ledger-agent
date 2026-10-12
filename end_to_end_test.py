import json
import urllib.request
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import the app components
import sys
sys.path.insert(0, '.')

def start_test_server():
    """Start the server in a background thread"""
    from main import QueryHandler, run

    class TestQueryHandler(QueryHandler):
        # Override to use a different port for testing
        pass

    # We'll run the server on a different port to avoid conflicts
    server_address = ('', 8081)
    httpd = HTTPServer(server_address, QueryHandler)

    # Initialize data (this will fetch from APIs)
    print("Initializing data for test server...")
    orders = []
    try:
        from data_fetcher import fetch_rates, fetch_all_orders
        from order_processor import process_orders

        rates = fetch_rates()
        raw_orders = fetch_all_orders()
        orders = process_orders(raw_orders, rates)
        QueryHandler.orders = orders
        print(f"Initialized with {len(orders)} orders")
    except Exception as e:
        print(f"Error initializing data: {e}")
        # Create some mock data for testing if APIs fail
        orders = []
        QueryHandler.orders = orders

    # Serve for a short time
    print("Test server started on port 8081")
    httpd.serve_forever()

def test_query(question):
    """Send a query to the test server"""
    try:
        data = json.dumps({"question": question}).encode('utf-8')
        req = urllib.request.Request(
            'http://localhost:8081/query',
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            return result.get('answer')
    except Exception as e:
        print(f"Error testing query '{question}': {e}")
        return None

def main():
    # Start server in background thread
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()

    # Wait a moment for server to start
    time.sleep(3)

    # Test queries
    test_questions = [
        "How many different customers placed at least one paid order for a Toaster?",
        "What is the average paid order value in USD for the South region?",
        "How many distinct customers have bought a Grinder (paid orders only)?"
    ]

    print("\n" + "="*60)
    print("END-TO-END TEST WITH ACTUAL SERVER")
    print("="*60)

    for question in test_questions:
        print(f"\nQuestion: {question}")
        answer = test_query(question)
        print(f"Answer: {answer}")

    print("\nTest completed. Server will shut down when this script ends.")

if __name__ == "__main__":
    main()