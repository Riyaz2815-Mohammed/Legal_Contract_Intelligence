from vector_pipeline.embeddings.embed_store import get_embedding_model, load_vectorstore
from vector_pipeline.retrieval.query import query_vectorstore
from vector_pipeline.similarity.sbert_scorer import compute_similarity
from vector_pipeline.risk.risk_tagger import tag_risk
from vector_pipeline.config.settings import TOP_K

import logging
logger = logging.getLogger(__name__)

# ── Module-level vectorstore cache (loaded once, reused across all clauses) ───
_vectorstore = None


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        logger.info("[Pipeline] Loading vectorstore …")
        embedding_model = get_embedding_model()
        _vectorstore = load_vectorstore(embedding_model)
        logger.info("[Pipeline] Vectorstore loaded.")
    return _vectorstore


def run_pipeline(query_text: str, clause_type: str = None, document_type: str = None, k: int = TOP_K) -> list[dict]:
    try:
        vectorstore = get_vectorstore()

        # Check if vectorstore has any documents before querying
        try:
            count = vectorstore._collection.count()
        except Exception:
            count = 0

        if count == 0:
            logger.warning("[Pipeline] ChromaDB is empty — no standard templates have been uploaded yet. Returning no results.")
            return []

        # Retrieve from ChromaDB
        results = query_vectorstore(vectorstore, query_text, clause_type, document_type, k)

        if not results:
            return []

        final = []
        for doc, chroma_score in results:
            # SBERT similarity
            sbert_score = compute_similarity(query_text, doc.page_content)

            # Risk tagging — based on CLIENT's clause vs standard template similarity
            risk_result = tag_risk(
                content=query_text,
                clause_type=doc.metadata.get("clause", ""),
                sbert_score=sbert_score
            )

            item = {
                "client_content":    query_text,
                "template_content":  doc.page_content,
                "chroma_score":      round(chroma_score, 4),
                "sbert_similarity":  sbert_score,
                **risk_result,
                "template_metadata": doc.metadata,
                "llm_reasoning":     None  # On-demand from frontend
            }
            final.append(item)

        # Sort by SBERT similarity — highest first
        final = sorted(final, key=lambda x: x["sbert_similarity"], reverse=True)
        logger.info(f"✅ Pipeline complete — {len(final)} results returned")
        return final

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise