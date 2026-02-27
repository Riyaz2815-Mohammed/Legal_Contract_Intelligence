from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser
from llm.prompt import LEGAL_ANALYSIS_PROMPT
from config.settings import MISTRAL_API_KEY, MISTRAL_MODEL, MISTRAL_TEMPERATURE
import logging

logger = logging.getLogger(__name__)

# Load once
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatMistralAI(
            model=MISTRAL_MODEL,
            mistral_api_key=MISTRAL_API_KEY,
            temperature=MISTRAL_TEMPERATURE
        )
        logger.info("✅ Mistral LLM loaded")
    return _llm


def run_llm_reasoning(item: dict) -> str:
    try:
        llm = get_llm()
        chain = LEGAL_ANALYSIS_PROMPT | llm | StrOutputParser()

        response = chain.invoke({
            "clause_type": item.get("clause", ""),
            "content": item.get("content", ""),
            "sbert_score": item.get("sbert_similarity", ""),
            "keyword_risk": item.get("keyword_risk", ""),
            "score_risk": item.get("score_risk", ""),
            "final_risk": item.get("final_risk", "")
        })

        logger.info(f"✅ LLM reasoning complete for clause: {item.get('clause')}")
        return response

    except Exception as e:
        logger.error(f"LLM reasoning failed: {e}")
        return f"LLM reasoning failed: {str(e)}"