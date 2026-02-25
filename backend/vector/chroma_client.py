# backend/vector/chroma_client.py

import chromadb
from chromadb.config import Settings
from core.configs import CHROMA_PATH

_client = None
_collection = None

COLLECTION_NAME = "standard_clauses"


def get_chroma_client() -> chromadb.PersistentClient:
    """Return a singleton persistent ChromaDB client."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
    return _client


def get_collection():
    """Return the standard_clauses collection, creating it if needed."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}   # use cosine distance
        )
    return _collection