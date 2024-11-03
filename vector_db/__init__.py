import weaviate
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import MetadataQuery

class ProductDatabase:
    def __init__(self, host, port, grpc_port):
        self.client = weaviate.connect_to_local(host=host, port=port, grpc_port=grpc_port)
        self.product_db = None
        self.products = []

    def connect(self):
        if not self.client.is_ready():
            raise ConnectionError("Failed to connect to Weaviate.")
        print("Connection to Weaviate established.")

    def create_product_collection(self):
        # Create the Product collection
        self.client.collections.create(
            "Product",
            description="Jiji product data",
            vectorizer_config=None,
            properties=[
                Property(name="item_name", data_type=DataType.TEXT),
                Property(name="price", data_type=DataType.TEXT),
                Property(name="description", data_type=DataType.TEXT),
                Property(name="location", data_type=DataType.TEXT),
            ]
        )
        self.product_db = self.client.collections.get("Product")
        print("Product collection created.")

    def add_products_with_embeddings(self, chunks, get_gemini_embeddings):
        # Generate embeddings and add products to the collection
        for chunk in chunks:
            embedding = get_gemini_embeddings(chunk["Full"].to_list())
            chunk.reset_index(drop=True, inplace=True)
            for index, row in chunk.iterrows():
                self.products.append({
                    "class": "Product",
                    "properties": {
                        "item_name": row["Item Name"],
                        "price": row["Price"],
                        "description": row["Description"],
                        "location": row["Location"]
                    },
                    "vector": embedding[index]
                })
        print(f"{len(self.products)} products prepared with embeddings.")

    def batch_insert_products(self):
        # Insert products in batch mode
        with self.product_db.batch.dynamic() as batch:
            for product in self.products:
                batch.add_object(
                    properties=product["properties"],
                    vector=product["vector"]
                )
        print("Products batch-inserted into the collection.")

    def query_similar_products(self, user_query, query_embedding, llm):
        # Embed the user query and retrieve similar products
        results = self.product_db.query.near_vector(
            near_vector=query_embedding,
            return_metadata=MetadataQuery(distance=True)
        )
        
        print(f"Found {len(results.objects)} similar products for the query.")

        # Prepare context for LLM response
        context = "\n".join([
            f"Item Name: {doc.properties['item_name']}, Description: {doc.properties['description']}, Price: {doc.properties['price']}, Location: {doc.properties['location']}"
            for doc in results.objects
        ])
        final_prompt = f"Given the following products:\n{context}\nAnswer the user's question: {user_query}"
        
        # Use LLM to generate an answer
        answer = llm.invoke(final_prompt)
        print("Generated Answer:", answer.content)
        return answer.content

    def close_connection(self):
        # Close the connection
        self.client.close()
        print("Connection to Weaviate closed.")
