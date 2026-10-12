# Ledger Query Service

A natural language query service for analyzing order data. This service allows users to ask questions about orders, revenue, refunds, and customer/product insights in plain English, and returns computed answers based on processed order data.

**Live Endpoint** - https://ledger-agent-i0ax.onrender.com

## Features

- **Natural Language Understanding**: Parses questions into structured queries
- **Multi-dimensional Analysis**: Supports filtering by region, product, customer, status, and time ranges
- **Aggregation Computations**: Calculates sums, averages, counts, and top-N rankings
- **Grouping Capabilities**: Group results by product or customer
- **Distinct Counting**: Count unique customers or items
- **HTTP API**: Simple POST endpoint for querying
- **Zero External Dependencies**: Uses only Python standard library

## Architecture

The service consists of several modules:

1. **Data Fetcher** (`data_fetcher.py`): Retrieves currency exchange rates and order data from APIs
2. **Order Processor** (`order_processor.py`): Processes raw orders, applies currency conversion, and deduplicates
3. **Question Parser** (`question_parser.py`): Parses natural language questions into structured query objects
4. **Query Engine** (`query_engine.py`): Executes the parsed queries against processed order data
5. **Main Server** (`main.py`): HTTP server that exposes the query functionality via a REST endpoint

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ledger_query_service
   ```

2. Ensure you have Python 3.6+ installed

3. No additional dependencies are required (uses only Python standard library)

## Usage

Start the server:
```bash
python main.py
```

The server will start on port 8080 by default. You can change the port by modifying the `run()` function in `main.py`.

### API Endpoint

**POST /query**

Send a JSON payload with a `question` field:

```json
{
  "question": "What is the total revenue from paid orders in North region?"
}
```

Response:
```json
{
  "answer": 1250.50
}
```

### Example Questions

Here are some example questions the service can answer:

- **Revenue Queries**:
  - "What is the total revenue from paid orders?"
  - "What is the average order value for Blender products?"
  - "Which product generated the highest revenue?"

- **Count Queries**:
  - "How many orders were placed in May 2026?"
  - "How many different customers placed paid orders?"
  - "Count the refunded North orders placed in May 2026."

- **Top-N Queries**:
  - "Which customer had the highest revenue?"
  - "Top 3 products by revenue"
  - "Top 5 customers by order count"

- **Time-based Queries**:
  - "What was the revenue in March 2026?"
  - "How many orders were placed last week?"
  - "What is the average order value today?"

### Supported Filters

- **Region**: North, South, East, West, Central
- **Product**: Blender, Mixer, Kettle, Air Fryer, Juicer, Grinder, Toaster, Rice Cooker (and others from data)
- **Customer**: Customer IDs in format C###
- **Status**: Paid, Refunded, Void
- **Time**: Month/Year, Year, Relative (today, yesterday, last week, last month)

## Testing

Run the test suite:
```bash
python test_logic.py
python test_fixes.py
python test_new_errors.py
```

The test files contain mock data and verify the correctness of the query parsing and execution.

## Project Structure

```
ledger_query_service/
├── data_fetcher.py        # Fetches currency rates and order data
├── order_processor.py     # Processes and enriches order data
├── question_parser.py     # Parses natural language questions
├── query_engine.py        # Executes queries against processed data
├── main.py                # HTTP server entry point
├── test_logic.py          # Core functionality tests
├── test_fixes.py          # Tests for previously fixed issues
├── test_new_errors.py     # Tests for specific error cases
├── requirements.txt       # Dependency information (none)
└── README.md              # This file
```

## Implementation Details

The service processes questions in four stages:

1. **Parsing**: The question parser identifies intent (revenue, refunded_amount, order_count, top_product, top_customer), extracts filters (region, product, customer, status, time range), and determines grouping and limits.

2. **Data Preparation**: On startup, the service fetches currency rates and order data, processes the orders (applying currency conversion and deduplication), and stores them in memory.

3. **Query Execution**: The query engine applies filters to the processed orders, then computes the requested aggregation (sum, average, count, grouping, etc.) based on the parsed intent.

4. **Response Formation**: The computed answer is returned as a JSON response.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details (if applicable).

---

*Built with Python standard library only.*