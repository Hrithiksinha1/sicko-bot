"""
ChromaDB database setup and management
"""
import chromadb
from chromadb.config import Settings
from app.config import CHROMA_DB_PATH, COLLECTION_NAME
import os

# Initialize ChromaDB client
client = None
collection = None

def init_db():
    """Initialize ChromaDB client and collection"""
    global client, collection
    
    # Create directory if it doesn't exist
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"Loaded existing collection: {COLLECTION_NAME}")
    except:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"Created new collection: {COLLECTION_NAME}")
    
    return collection

def get_collection():
    """Get the ChromaDB collection"""
    global collection
    if collection is None:
        init_db()
    return collection

def get_client():
    """Get the ChromaDB client"""
    global client
    if client is None:
        init_db()
    return client

