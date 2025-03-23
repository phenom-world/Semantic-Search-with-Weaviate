import weaviate
from sentence_transformers import SentenceTransformer
import weaviate.classes.config as wc


class SupportService:
    def __init__(self, host="localhost", port=8080, collection_name="CustomerSupport", model_name="all-MiniLM-L6-v2"):
        self.client = weaviate.connect_to_local( host, port )
        self.collection_name = collection_name
        self.model = SentenceTransformer(model_name)

    def search(self, query, top_k=5):
        query_vector = self.model.encode(query).tolist()
        support_collection = self.client.collections.get(self.collection_name)
        response = support_collection.query.hybrid(
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

    def search_with_filter(self, query, category, top_k=5):
        from weaviate.classes.query import Filter        
        query_vector = self.model.encode(query).tolist()
        response = (
            self.client.collections.get(self.collection_name)
            .query
            .hybrid(
                query=query,  # Text query for hybrid search
                vector=query_vector,
                filters=Filter.by_property("category").equal(category),
                limit=top_k,
                return_properties=["customerIssue", "category", "resolutionResponse"]
            )
        )
        
        return [
            {
                "Customer Issue": item.properties["customerIssue"],
                "Category": item.properties["category"],
                "Resolution Response": item.properties["resolutionResponse"]
            }
            for item in response.objects
        ]

    def load_data_in_batches(self, data):
        # Delete collection if it already exists
        if self.client.collections.exists(self.collection_name):
            self.client.collections.delete(self.collection_name)

        # Create collection
        self.client.collections.create(
            name=self.collection_name,
            description="Customer support issues and resolutions",
            vectorizer_config=None,  # Since we're providing vectors manually
            properties=[
                wc.Property(name="ticketId", data_type=wc.DataType.TEXT),
                wc.Property(name="category", data_type=wc.DataType.TEXT),
                wc.Property(name="customerIssue", data_type=wc.DataType.TEXT),
                wc.Property(name="resolutionResponse", data_type=wc.DataType.TEXT),
            ]
        )

        collection = self.client.collections.get(self.collection_name)
        with collection.batch.dynamic() as batch:
            for entry in data:
                vector = self.model.encode(entry["customer_issue"]).tolist()
                batch.add_object(
                    properties={
                        "ticketId": entry["ticket_id"],
                        "category": entry["category"], 
                        "customerIssue": entry["customer_issue"],
                        "resolutionResponse": entry["resolution_response"]
                    },
                    vector=vector
                )
                if batch.number_errors > 100:
                    print("Batch import stopped due to excessive errors.")
                    break

        failed_objects = collection.batch.failed_objects
        if failed_objects:
            print(f"Number of failed imports: {len(failed_objects)}")
            print(f"First failed object: {failed_objects[0]}")

        return {"message": "Data successfully loaded into Weaviate ✅"}
