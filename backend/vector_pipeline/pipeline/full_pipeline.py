from vector_pipeline.embeddings.embed_store import get_embedding_model
from vector_pipeline.retrieval.query import query_vectorstore
from vector_pipeline.similarity.sbert_scorer import compute_similarity
from vector_pipeline.risk.risk_tagger import tag_risk
from vector_pipeline.config.settings import TOP_K

import logging
logger = logging.getLogger(__name__)


def run_pipeline(query_text: str, clause_type: str = None, document_type: str = None, k: int = TOP_K) -> list[dict]:
    try:
        embedding_model = get_embedding_model()

        # Retrieve from Supabase (pgvector)
        results = query_vectorstore(query_text, embedding_model, clause_type, k)

        if not results:
            logger.warning(f"[Pipeline] No similar clauses found for: '{query_text[:60]}...'")
            return []

        final = []
        for doc, score in results:
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
                "vector_score":      round(float(score), 4),
                "sbert_similarity":  sbert_score,
                **risk_result,
                "template_metadata": doc.metadata,
                "llm_reasoning":     None  # On-demand from frontend
            }
            final.append(item)

        # Sort by SBERT similarity — highest first
        final = sorted(final, key=lambda x: x["sbert_similarity"], reverse=True)
        logger.info(f"✅ Pipeline complete — {len(final)} results returned from Supabase")
        return final

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise
