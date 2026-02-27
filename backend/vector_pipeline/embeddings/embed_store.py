import psycopg2
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


from vector_pipeline.config.settings import (
    DATABASE_URL,
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
    EMBEDDING_NORMALIZE,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION
)

import logging
logger = logging.getLogger(__name__)


def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": EMBEDDING_DEVICE},
        encode_kwargs={"normalize_embeddings": EMBEDDING_NORMALIZE}
    )


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
        logger.info(f"Fetched {len(df)} legal clauses from Supabase")
        return df
    except Exception as e:
        logger.error(f"Error fetching clauses: {e}")
        raise
    finally:
        if conn:
            conn.close()


def build_documents(df: pd.DataFrame) -> list[Document]:
    docs = []
    for _, row in df.iterrows():
        doc = Document(
            page_content=row["content"],
            metadata={
                "clause_id": str(row["clause_id"]),
                "clause": str(row["clause"]),
                "content_id": str(row["content_id"]),
                "source": str(row["source"]),
                "page_number": str(row["page_number"]),
                "document": str(row["document"]),
                "document_id": str(row["document_id"]),
                "created_at": str(row["created_at"])
            }
        )
        docs.append(doc)
    logger.info(f"Prepared {len(docs)} documents")
    return docs


def embed_and_store(docs: list[Document], embedding_model) -> Chroma:
    try:
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embedding_model,
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name=CHROMA_COLLECTION
        )
        vectorstore.persist()
        logger.info("✅ Embedded and stored in ChromaDB")
        return vectorstore
    except Exception as e:
        logger.error(f"Error storing in ChromaDB: {e}")
        raise


def load_vectorstore(embedding_model) -> Chroma:
    return Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embedding_model,
        collection_name=CHROMA_COLLECTION
    )


def run_embed_pipeline():
    embedding_model = get_embedding_model()
    df = fetch_legal_clauses()
    docs = build_documents(df)
    embed_and_store(docs, embedding_model)
    logger.info("✅ Embed pipeline complete")