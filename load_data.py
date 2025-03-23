import weaviate.classes.config as wc
import json
from weaviate.classes.data import DataObject


async def load_data(client, collection_name, model):
    with open('customer_support_data.json', 'r') as f:
        data = json.load(f)

    # Delete collection if it already exists
    if await client.collections.exists(collection_name):
        await client.collections.delete(collection_name)
    # Create collection
    await client.collections.create(
        name=collection_name,
        description="Customer support issues and resolutions",
        vectorizer_config=None,  # Since we're providing vectors manually
        properties=[
            wc.Property(name="ticketId", data_type=wc.DataType.TEXT),
            wc.Property(name="category", data_type=wc.DataType.TEXT),
            wc.Property(name="customerIssue", data_type=wc.DataType.TEXT),
            wc.Property(name="resolutionResponse", data_type=wc.DataType.TEXT),
        ]
    )
    collection = client.collections.get(collection_name)

    objects = []
    for entry in data:
        vector = model.encode(entry["customer_issue"]).tolist()
        data_object = DataObject(
            properties={
                "ticketId": entry["ticket_id"],
                "category": entry["category"], 
                "customerIssue": entry["customer_issue"],
                "resolutionResponse": entry["resolution_response"]
            },
            vector=vector
        )
        objects.append(data_object)
    
    # Insert objects in batches
    batch_size = 100
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i+batch_size]
        result = await collection.data.insert_many(batch)
        if hasattr(result, 'errors') and result.errors:
            print(f"Errors in batch {i//batch_size}: {result.errors}")
    
    print(f"Data successfully loaded into Weaviate ✅, Total tickets: {len(data)}")