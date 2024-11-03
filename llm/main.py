import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import pandas as pd


class GeminiEmbeddingHandler:
    def __init__(self, api_key, model_name="gemini-pro", embedding_model="models/embedding-001"):
        # Load the API key from the environment variable
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API key not found in environment variables.")
        
        # Initialize the LLM and embedding model
        self.llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=self.api_key)
        self.embedding_model = embedding_model
        self.embeddings = GoogleGenerativeAIEmbeddings(model=self.embedding_model)
        
    def get_embeddings_for_documents(self, chunk_list, batch_size=100):
        """Generate embeddings for a list of documents in chunks."""
        return self.embeddings.embed_documents(chunk_list, batch_size=batch_size)
    
    def get_embedding_for_query(self, query):
        """Generate an embedding for a single query."""
        return self.embeddings.embed_query(query)
    
    def import_data_in_chunks(self, file_path, chunk_size=100):
        """Load data in chunks from a CSV file."""
        processed_chunks=[]
        for chunk in pd.read_csv(file_path,chunksize=chunk_size):
            # Append to a list, or directly store each chunk in Weaviate after embedding
            processed_chunks.append(chunk)
        return processed_chunks
        
