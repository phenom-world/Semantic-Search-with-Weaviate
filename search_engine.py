import weaviate.classes.config as wc
from fastapi import HTTPException
from weaviate.classes.query import Filter       

class SemanticSearchEngine:
    def __init__(self, client, collection_name, model):
        self.client = client
        self.collection_name = collection_name
        self.model = model

    async def search(self, query, top_k=5):
        try:
            # Encode the query into a vector
            query_vector = self.model.encode(query).tolist()

            # Perform hybrid search
            response = await self.client.collections.get(self.collection_name).query.hybrid(
            query=query,
            vector=query_vector,
            limit=top_k,
            return_properties=["customerIssue", "category", "resolutionResponse"]
            )
            return [
            {
                "Customer Issue": item.properties["customerIssue"],
                "Category": item.properties["category"],
                "Resolution Response": item.properties["resolutionResponse"]
            }
            for item in response.objects
            ]

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 

    async def search_with_filter(self, query, category, top_k=5):
        try:
            # Encode the query into a vector
            query_vector = self.model.encode(query).tolist()

            # Perform hybrid search with filter
            response = await  self.client.collections.get(self.collection_name).query.hybrid(
                query=query,  # Text query for hybrid search
                vector=query_vector,
                filters=Filter.by_property("category").equal(category),
                limit=top_k,
                return_properties=["customerIssue", "category", "resolutionResponse"]
            )
            return [
            {
                "Customer Issue": item.properties["customerIssue"],
                "Category": item.properties["category"],
                "Resolution Response": item.properties["resolutionResponse"]
            }
            for item in response.objects
            ]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))