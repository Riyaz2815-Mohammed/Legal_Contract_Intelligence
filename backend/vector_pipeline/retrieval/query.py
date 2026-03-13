import psycopg2
from pgvector.psycopg2 import register_vector
from vector_pipeline.config.settings import DATABASE_URL, TOP_K
import logging

logger = logging.getLogger(__name__)

# Clause types that should not be matched
_SKIP_MATCH_TYPES = {"Header", "Other", "Preamble"}

# Canonical alias map
_CLAUSE_ALIASES: dict[str, list[str]] = {
    "Term":                      ["Term", "Duration"],
    "Termination":               ["Termination", "Effect of Termination"],
    "Governing Law / Jurisdiction / Dispute Resolution": ["Governing Law", "Dispute Resolution", "Governing Law / Jurisdiction / Dispute Resolution"],
    "Confidentiality":           ["Confidentiality", "Non-Disclosure"],
    "Limitation of Liability":   ["Limitation of Liability"],
    "Intellectual Property Rights": ["Intellectual Property Rights", "IP Rights"],
    "Data Protection and Security": ["Data Protection and Security", "Privacy"],
}


def search_similar_clauses(query_embedding: list, top_k: int = TOP_K, clause_type: str = None) -> list:
    """
    Search for similar clauses in Supabase using pgvector cosine distance.
    Returns a list of dicts with content and metadata.
    """
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        register_vector(conn)
        
        candidates = _CLAUSE_ALIASES.get(clause_type, [clause_type]) if clause_type and clause_type not in _SKIP_MATCH_TYPES else []
        
        with conn.cursor() as cur:
            if candidates:
                # Filter by clause type aliases
                query = """
                    SELECT clause_id, clause, content_id, content, page_number, 
                           document, document_id, created_at,
                           embedding <=> %s::vector AS distance
                    FROM clause_embeddings
                    WHERE clause IN %s
                    ORDER BY distance ASC
                    LIMIT %s
                """
                cur.execute(query, (query_embedding, tuple(candidates), top_k))
            else:
                # Unfiltered fallback
                query = """
                    SELECT clause_id, clause, content_id, content, page_number, 
                           document, document_id, created_at,
                           embedding <=> %s::vector AS distance
                    FROM clause_embeddings
                    ORDER BY distance ASC
                    LIMIT %s
                """
                cur.execute(query, (query_embedding, top_k))
            
            results = []
            for row in cur.fetchall():
                # Convert distance (cosine distance) to similarity score (1 - distance)
                similarity = 1.0 - float(row[8]) if row[8] is not None else 0.0
                results.append({
                    "page_content": row[3],
                    "metadata": {
                        "clause_id": row[0],
                        "clause": row[1],
                        "content_id": row[2],
                        "page_number": row[4],
                        "document": row[5],
                        "document_id": row[6],
                        "created_at": row[7]
                    },
                    "score": similarity
                })
            return results
    except Exception as e:
        logger.error(f"Error searching Supabase: {e}")
        raise
    finally:
        if conn:
            conn.close()


def query_vectorstore(query_text: str, embedding_model, clause_type: str = None, top_k: int = TOP_K) -> list:
    """
    Adapter function to replace the ChromaDB query logic.
    """
    try:
        # Generate embedding for the query text
        query_embedding = embedding_model.embed_query(query_text)
        
        # Search in Supabase
        results = search_similar_clauses(query_embedding, top_k, clause_type)
        
        # Convert to the format expected by full_pipeline (list of (Document, score))
        formatted_results = []
        for r in results:
            from langchain_core.documents import Document
            doc = Document(page_content=r["page_content"], metadata=r["metadata"])
            # The downstream code expects (doc, score) where score is distance (or similar metric)
            # In Chroma's similarity_search_with_score, it's often L2 distance (lower is better).
            # full_pipeline uses sbert_score later, so we just need something here.
            formatted_results.append((doc, r["score"]))
            
        return formatted_results
    except Exception as e:
        logger.error(f"Error in query_vectorstore: {e}")
        raise
