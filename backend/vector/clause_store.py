# backend/vector/clause_store.py

from typing import List, Dict, Any, Optional
from vector.chroma_client import get_collection


def store_clauses(clauses: List[Dict[str, Any]], document_type: str = "Unknown") -> int:
    """
    Store standard template clause embeddings into ChromaDB.

    Each clause dict must have:
        content_id, content, clause_id, clause (type), embedding (List[float])

    Returns the number of clauses stored.
    """
    collection = get_collection()

    ids = []
    embeddings = []
    metadatas = []

    for clause in clauses:
        embedding = clause.get("embedding")
        content = clause.get("content", "").strip()
        if not embedding or not content:
            continue

        ids.append(clause["content_id"])
        embeddings.append(embedding)
        metadatas.append({
            "clause_id":      str(clause.get("clause_id") or ""),
            "clause_type":    clause.get("clause", "Other"),
            "content":        content[:2000],          # ChromaDB metadata char limit
            "document_type":  document_type,
            "page_number":    str(clause.get("page_number") or ""),
        })

    if not ids:
        return 0

    # Upsert so re-processing a template doesn't create duplicates
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(ids)


def query_similar(embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Query ChromaDB for the top-k most similar standard clauses.

    Returns a list of dicts with:
        content_id, clause_type, content, document_type, distance, similarity
    """
    collection = get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, collection.count()),
        include=["metadatas", "distances", "embeddings"]
    )

    hits = []
    for i, meta in enumerate(results["metadatas"][0]):
        distance  = results["distances"][0][i]
        # ChromaDB cosine collection returns distance in [0,2].
        # similarity = 1 - (distance / 2)  maps [0,2] → [1,0]
        similarity = round(max(0.0, 1.0 - distance / 2.0), 4)
        hits.append({
            "content_id":    results["ids"][0][i],
            "clause_type":   meta.get("clause_type", "Other"),
            "content":       meta.get("content", ""),
            "document_type": meta.get("document_type", ""),
            "distance":      round(distance, 4),
            "similarity":    similarity,
        })

    return hits
