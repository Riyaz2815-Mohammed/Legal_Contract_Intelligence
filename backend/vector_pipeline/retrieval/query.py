from langchain_community.vectorstores import Chroma
from vector_pipeline.config.settings import TOP_K
import logging

logger = logging.getLogger(__name__)


def query_vectorstore(
    vectorstore: Chroma,
    query_text: str,
    clause_type: str = None,
    document_type: str = None,
    k: int = TOP_K
) -> list:
    try:
        filters = []
        if clause_type:
            filters.append({"clause": clause_type})
        if document_type and document_type != "Unknown":
            filters.append({"document": document_type})

        # Chroma requires $and if multiple filters exist
        if len(filters) > 1:
            filter_dict = {"$and": filters}
        elif len(filters) == 1:
            filter_dict = filters[0]
        else:
            filter_dict = None

        results = vectorstore.similarity_search_with_score(
            query_text,
            k=k,
            filter=filter_dict
        )

        logger.info(f"Retrieved {len(results)} clauses for query: '{query_text}' with filters: {filter_dict}")
        return results

    except Exception as e:
        logger.error(f"Error querying vectorstore: {e}")
        raise