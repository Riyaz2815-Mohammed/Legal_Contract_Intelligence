from embeddings.embed_store import get_embedding_model, load_vectorstore
from retrieval.query import query_vectorstore
from similarity.sbert_scorer import compute_similarity
from risk.risk_tagger import tag_risk
from llm.reasoning import run_llm_reasoning
from config.settings import TOP_K

import logging
logger = logging.getLogger(__name__)


def run_pipeline(query_text: str, clause_type: str = None, k: int = TOP_K) -> list[dict]:
    try:
        # Load models and vectorstore
        embedding_model = get_embedding_model()
        vectorstore = load_vectorstore(embedding_model)

        # Retrieve from ChromaDB
        results = query_vectorstore(vectorstore, query_text, clause_type, k)

        final = []
        for doc, chroma_score in results:

            # SBERT similarity
            sbert_score = compute_similarity(query_text, doc.page_content)

            # Risk tagging
            risk_result = tag_risk(
                content=doc.page_content,
                clause_type=doc.metadata.get("clause", ""),
                sbert_score=sbert_score
            )

            item = {
                "content": doc.page_content,
                "chroma_score": round(chroma_score, 4),
                "sbert_similarity": sbert_score,
                **risk_result,
                **doc.metadata
            }

            # Auto LLM for high risk
            if item["needs_llm"]:
                logger.warning(f"🔴 High risk clause detected: {item.get('clause')} — triggering LLM")
                item["llm_reasoning"] = run_llm_reasoning(item)
            else:
                item["llm_reasoning"] = None

            final.append(item)

        # Sort by SBERT similarity — highest first
        final = sorted(final, key=lambda x: x["sbert_similarity"], reverse=True)
        logger.info(f"✅ Pipeline complete — {len(final)} results returned")
        return final

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise