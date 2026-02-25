# backend/embeddings/embedder.py

from typing import List
from embeddings.sbert_model import get_model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Encode a list of texts into SBERT embeddings.
    Returns a list of float vectors (one per text).
    """
    if not texts:
        return []
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.tolist()


def embed_single(text: str) -> List[float]:
    """
    Encode a single text string into an SBERT embedding vector.
    """
    result = embed_texts([text])
    return result[0] if result else []
