from vector_pipeline.embeddings.embed_store import get_embedding_model, load_vectorstore
from vector_pipeline.retrieval.query import query_vectorstore
from vector_pipeline.similarity.sbert_scorer import compute_similarity
from vector_pipeline.risk.risk_tagger import tag_risk
from vector_pipeline.config.settings import TOP_K

import logging
logger = logging.getLogger(__name__)


def run_pipeline(query_text: str, clause_type: str = None, document_type: str = None, k: int = TOP_K) -> list[dict]:
    try:
        # Load models and vectorstore
        embedding_model = get_embedding_model()
        vectorstore = load_vectorstore(embedding_model)

        # Retrieve from ChromaDB filtered by both clause type AND document type (e.g. MSA)
        results = query_vectorstore(vectorstore, query_text, clause_type, document_type, k)

        final = []
        for doc, chroma_score in results:

            # SBERT similarity
            sbert_score = compute_similarity(query_text, doc.page_content)

            # Risk tagging
            # CRITICAL: We tag the risk of the CLIENT's clause (query_text), not the standard template (doc.page_content)
            risk_result = tag_risk(
                content=query_text,
                clause_type=doc.metadata.get("clause", ""),
                sbert_score=sbert_score
            )

            item = {
                "client_content": query_text,
                "template_content": doc.page_content,
                "chroma_score": round(chroma_score, 4),
                "sbert_similarity": sbert_score,
                **risk_result,
                "template_metadata": doc.metadata,
                "llm_reasoning": None # Made explicitly On-Demand from the Frontend
            }

            final.append(item)

        # Sort by SBERT similarity — highest first
        final = sorted(final, key=lambda x: x["sbert_similarity"], reverse=True)
        logger.info(f"✅ Pipeline complete — {len(final)} results returned")
        return final

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise