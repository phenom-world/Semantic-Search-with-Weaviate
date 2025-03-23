from fastapi import FastAPI, Query, HTTPException, Depends
from search_engine import SemanticSearchEngine
from typing import List, Dict
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from load_data import load_data
import weaviate
from contextlib import asynccontextmanager


collection_name = "CustomerSupport"
model = SentenceTransformer("all-MiniLM-L6-v2")

# Lifespan for the FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the Weaviate client
    client = weaviate.use_async_with_local(host="localhost", port=8080)
    await client.connect()
    # Load data into Weaviate
    await load_data(client, collection_name, model)
    # Store the client in the app state
    app.state.weaviate_client = client
    yield
    # Close the client when the app shuts down
    await client.close()


app = FastAPI(
    title="Semantic Search API",
    description="A semantic search engine for customer support issues",
    version="1.0.0",
    lifespan=lifespan
)


class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, str]]

class FilteredSearchResponse(SearchResponse):
    category: str

# Dependency to get the Weaviate client
async def get_weaviate_client():
    if not await app.state.weaviate_client.is_ready():
        raise HTTPException(status_code=503, detail="Weaviate is not ready")
    return app.state.weaviate_client


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {"message": "Welcome to the Semantic Search Engine API!"}


@app.get("/search")
async def search(query: str = Query(..., description="Enter search query"),
                top_k: int = 5, client = Depends(get_weaviate_client)):
    """
    Perform semantic search using the search engine.
    :param query: The user query
    :param top_k: Number of results to return (default: 5)
    :param client: Weaviate client
    :return: List of relevant customer support issues
    """
    search_engine = SemanticSearchEngine(client, collection_name, model)
    results = await search_engine.search(query, top_k)
    return {"query": query, "results": results}

@app.get("/search/filter")
async def search_with_filter(query: str = Query(..., description="Enter search query"), category: str = Query(..., description="Filter by category"), 
                            top_k: int = 5, client = Depends(get_weaviate_client)):  
    """
    Perform semantic search using the search engine.
    :param query: The user query
    :param category: The category to filter by
    :param top_k: Number of results to return (default: 5)
    :param client: Weaviate client
    :return: List of relevant customer support issues filtered by category
    """          
    search_engine = SemanticSearchEngine(client, collection_name, model)
    results = await search_engine.search_with_filter(query, category, top_k)
    return {"query": query, "category": category, "results": results}