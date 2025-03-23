from fastapi import FastAPI, Query
from support_service import SupportService
from typing import List, Dict
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import json

collection_name = "CustomerSupport"
model = SentenceTransformer("all-MiniLM-L6-v2")

app = FastAPI(
    title="Semantic Search API",
    description="A semantic search engine for customer support issues",
    version="1.0.0",
)

support_service = SupportService()

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, str]]

class FilteredSearchResponse(SearchResponse):
    category: str

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {"message": "Welcome to the Semantic Search Engine API!"}


@app.get("/load-data")
async def load_data():
    with open('customer_support_data.json', 'r') as f:
        data = json.load(f)
    support_service.load_data_in_batches(data)
    return {"message": "Data loaded successfully", "totalTickets": len(data)}


@app.get("/search")
def search(query: str = Query(..., description="Enter search query"), top_k: int = 5):
    results =  support_service.search(query, top_k)
    return {"query": query, "results": results}



@app.get("/search/filter")
def search_with_filter(query: str = Query(..., description="Enter search query"), category: str = Query(..., description="Filter by category"), top_k: int = 5):
    results = support_service.search_with_filter(query, category, top_k)
    return {"query": query, "category": category, "results": results}


