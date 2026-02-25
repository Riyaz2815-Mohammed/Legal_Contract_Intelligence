# backend/similarity/matcher.py

import math
from typing import List, Optional


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    Returns a value in [0.0, 1.0] (clipped, never negative).
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot   = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    similarity = dot / (mag_a * mag_b)
    return round(max(0.0, min(1.0, similarity)), 4)


def best_similarity(query_embedding: List[float], hits: List[dict]) -> Optional[float]:
    """
    Given the ChromaDB query hits (which already include a 'similarity' field),
    return the highest similarity score among them, or None if hits is empty.
    """
    if not hits:
        return None
    return max(h["similarity"] for h in hits)