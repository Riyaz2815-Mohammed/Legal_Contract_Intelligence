import psycopg2
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from pgvector.psycopg2 import register_vector

from vector_pipeline.config.settings import (
    DATABASE_URL,
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
    EMBEDDING_NORMALIZE
)

import logging
logger = logging.getLogger(__name__)

# ── Module-level model cache ──────────────────────────────────────────────────
_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"[Embed] Loading embedding model '{EMBEDDING_MODEL}' …")
        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": EMBEDDING_DEVICE},
            encode_kwargs={"normalize_embeddings": EMBEDDING_NORMALIZE}
        )
        logger.info("[Embed] Embedding model loaded.")
    return _embedding_model


def fetch_legal_clauses() -> pd.DataFrame:
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        df = pd.read_sql("""
            SELECT clause_id, clause, content, content_id, source,
                   page_number, document, document_id, created_at
            FROM clauses
            WHERE source = 'legal'
        """, conn)
        logger.info(f"Fetched {len(df)} legal clauses from DB")
        return df
    except Exception as e:
        logger.error(f"Error fetching clauses: {e}")
        raise
    finally:
        if conn:
            conn.close()


def store_clause_embedding(conn, clause_data: dict, embedding: list):
    """
    Insert or update a clause embedding in Supabase pgvector table.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO clause_embeddings (
                    clause_id, clause, content_id, content, embedding, 
                    document, document_id, page_number, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (content_id) DO UPDATE SET
                    clause = EXCLUDED.clause,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    document = EXCLUDED.document,
                    document_id = EXCLUDED.document_id,
                    page_number = EXCLUDED.page_number,
                    created_at = EXCLUDED.created_at
            """, (
                clause_data["clause_id"],
                clause_data["clause"],
                clause_data["content_id"],
                clause_data["content"],
                embedding,
                clause_data["document"],
                clause_data["document_id"],
                clause_data["page_number"],
                clause_data["created_at"]
            ))
    except Exception as e:
        logger.error(f"Error storing embedding: {e}")
        raise


def run_embed_pipeline():
    """
    Wipe clause_embeddings table and re-embed ALL legal clauses from DB.
    """
    embedding_model = get_embedding_model()
    df = fetch_legal_clauses()
    
    if df.empty:
        logger.warning("[Embed] No legal clauses in DB — pgvector not updated.")
        return

    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        register_vector(conn)
        
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE clause_embeddings")
            logger.info("[Embed] Wiped old embeddings in Supabase")

        count = 0
        for _, row in df.iterrows():
            # Generate embedding
            embedding = embedding_model.embed_query(row["content"])
            
            # Store in Supabase
            store_clause_embedding(conn, row.to_dict(), embedding)
            count += 1
            
        conn.commit()
        logger.info(f"✅ Embed pipeline complete — {count} clauses stored in Supabase pgvector")
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error in embed pipeline: {e}")
        raise
    finally:
        if conn:
            conn.close()
