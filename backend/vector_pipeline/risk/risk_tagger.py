from vector_pipeline.risk.risk_config import RISK_CONFIG, DEFAULT_RISK, RISK_PRIORITY
from vector_pipeline.config.settings import SBERT_HIGH_RISK_THRESHOLD, SBERT_MEDIUM_RISK_THRESHOLD
import logging

logger = logging.getLogger(__name__)


def tag_risk(content: str, clause_type: str, sbert_score: float) -> dict:
    try:
        content_lower = content.lower()
        keywords = RISK_CONFIG.get(clause_type.lower(), DEFAULT_RISK)

        # Keyword based risk
        if any(kw in content_lower for kw in keywords["high"]):
            keyword_risk = "high"
        elif any(kw in content_lower for kw in keywords["medium"]):
            keyword_risk = "medium"
        else:
            keyword_risk = "low"

        # SBERT score based risk
        if sbert_score < SBERT_HIGH_RISK_THRESHOLD:
            score_risk = "high"
        elif sbert_score < SBERT_MEDIUM_RISK_THRESHOLD:
            score_risk = "medium"
        else:
            score_risk = "low"

        # Final risk — take higher of both
        final_risk = max(keyword_risk, score_risk, key=lambda x: RISK_PRIORITY[x])

        return {
            "keyword_risk": keyword_risk,
            "score_risk": score_risk,
            "final_risk": final_risk,
            "needs_llm": final_risk == "high"
        }

    except Exception as e:
        logger.error(f"Error in risk tagging: {e}")
        return {
            "keyword_risk": "unknown",
            "score_risk": "unknown",
            "final_risk": "unknown",
            "needs_llm": False
        }