from langchain_community.vectorstores import Chroma
from config.settings import TOP_K
import logging

logger = logging.getLogger(__name__)


def query_vectorstore(
    vectorstore: Chroma,
    query_text: str,
    clause_type: str = None,
    k: int = TOP_K
) -> list:
    try:
        filter_dict = {"clause": clause_type} if clause_type else None

        results = vectorstore.similarity_search_with_score(
            query_text,
            k=k,
            filter=filter_dict
        )

        logger.info(f"Retrieved {len(results)} clauses for query: '{query_text}'")
        return results

    except Exception as e:
        logger.error(f"Error querying vectorstore: {e}")
        raise