# Semantic Search with FastAPI and AI

A FastAPI-based semantic search engine for customer support issues using Weaviate and Sentence Transformers. This API provides semantic search capabilities for customer support tickets with category filtering.

## Features

- Semantic search using Sentence Transformers (all-MiniLM-L6-v2)
- Category-based filtering
- Hybrid search combining vector and keyword search
- RESTful API endpoints
- Sample customer support dataset included

## Prerequisites

- Python 3.10+
- Weaviate running locally (default: localhost:8080)

## Setup

1. Create a virtual environment:

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Start Weaviate locally (if not already running)

2. Start the FastAPI server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Available Endpoints

- `GET /`: Welcome message and API information
- `GET /load-data`: Load the sample customer support dataset into Weaviate
- `GET /search`: Perform semantic search across all categories
  - Query parameters:
    - `query`: Search query text
    - `top_k`: Number of results to return (default: 5)
- `GET /search/filter`: Perform semantic search with category filter
  - Query parameters:
    - `query`: Search query text
    - `category`: Category to filter results
    - `top_k`: Number of results to return (default: 5)

## Sample Data

The application includes a sample dataset with customer support tickets across various categories:

- Billing Issues
- Technical Support
- Account Access
- Product Inquiry
- Refund Requests
- Shipping Delays
- Subscription Cancellation
- Order Tracking

## Dependencies

- weaviate-client==4.11.2
- sentence-transformers==2.0.0
- numpy==2.2.4
- pandas==2.2.3
- fastapi[standard]

## License

MIT
