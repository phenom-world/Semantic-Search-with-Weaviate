import weaviate.classes.config as wc
from sentence_transformers import SentenceTransformer
import weaviate
import json



host = "localhost"
port = 8080
collection_name = "CustomerSupport"
model_name = "all-MiniLM-L6-v2"

# connect to weaviate
client = weaviate.connect_to_local( host, port )

# load the model
model = SentenceTransformer(model_name)

# load the data
with open('customer_support_data.json', 'r') as f:
    data = json.load(f)
# Delete collection if it already exists
if client.collections.exists(collection_name):
    client.collections.delete(collection_name)
# Create collection
client.collections.create(
    name=collection_name,
    description="Customer support issues and resolutions",
    vectorizer_config=None,  # Since we're providing vectors manually
    properties=[
            wc.Property(name=
            "ticketId", data_type=wc.DataType.TEXT),
            wc.Property(name="category", data_type=wc.DataType.TEXT),
            wc.Property(name="customerIssue", data_type=wc.DataType.TEXT),
            wc.Property(name="resolutionResponse", data_type=wc.DataType.TEXT),
        ]
    )
collection = client.collections.get(collection_name)
with collection.batch.dynamic() as batch:
    for entry in data:
        vector = model.encode(entry["customer_issue"]).tolist()
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
