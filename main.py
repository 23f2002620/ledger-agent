import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from typing import Dict, Any

from data_fetcher import fetch_rates, fetch_all_orders
from order_processor import process_orders
from question_parser import parse_question
from query_engine import compute_answer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryHandler(BaseHTTPRequestHandler):
    # The processed orders will be set as a class variable after initialization
    orders: list = []

    def do_POST(self):
        """Handle POST requests to /query."""
        if self.path != '/query':
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error(400, "Empty body")
            return

        body = self.rfile.read(content_length)
        try:
            data = json.loads(body.decode('utf-8'))
            question = data.get('question')
            if not question:
                self.send_error(400, "Missing 'question' field")
                return
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        try:
            # Parse the question
            parsed = parse_question(question)
            logger.info(f"Parsed question: {parsed}")

            # Compute the answer
            answer = compute_answer(self.__class__.orders, parsed)
            logger.info(f"Computed answer: {answer} (type: {type(answer)})")

            # Prepare response
            response = {
                "answer": answer
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            logger.exception("Error processing request")
            self.send_error(500, f"Internal server error: {e}")

    def log_message(self, format, *args):
        # Override to use logging
        logger.info("%s - - [%s] %s",
                    self.client_address[0],
                    self.log_date_time_string(),
                    format%args)

def initialize_data() -> list:
    """Fetch and process all data from the APIs."""
    logger.info("Fetching currency rates...")
    rates = fetch_rates()
    logger.info(f"Fetched rates: {rates}")

    logger.info("Fetching all orders (this may take a moment)...")
    raw_orders = fetch_all_orders()
    logger.info(f"Fetched {len(raw_orders)} raw orders")

    logger.info("Processing orders...")
    processed_orders = process_orders(raw_orders, rates)
    logger.info(f"Processed {len(processed_orders)} orders after deduplication")

    return processed_orders

def run(server_class=HTTPServer, handler_class=QueryHandler, port=8080):
    """Run the HTTP server."""
    # Initialize data once at startup
    orders = initialize_data()
    handler_class.orders = orders
    logger.info(f"Loaded {len(orders)} orders into memory")

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logger.info(f"Starting server on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server.")
        httpd.server_close()

if __name__ == '__main__':
    run()