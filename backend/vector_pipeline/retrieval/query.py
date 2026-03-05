from langchain_community.vectorstores import Chroma
from vector_pipeline.config.settings import TOP_K
import logging

logger = logging.getLogger(__name__)

# Clause types that should not be matched — skip SBERT retrieval for these
_SKIP_MATCH_TYPES = {"Header", "Other", "Preamble"}

# Canonical alias map: normalises clause types that may differ slightly between
# client docs and legal templates but mean the same thing
_CLAUSE_ALIASES: dict[str, list[str]] = {
    "Term":                      ["Term", "Duration"],
    "Termination":               ["Termination", "Effect of Termination"],
    "Governing Law":             ["Governing Law", "Dispute Resolution"],
    "Confidentiality":           ["Confidentiality", "Non-Disclosure"],
    "Limitation of Liability":   ["Limitation of Liability"],
    "Intellectual Property Rights": ["Intellectual Property Rights", "IP Rights"],
    "Data Protection and Security": ["Data Protection and Security", "Privacy"],
}


def _get_clause_filter(clause_type: str):
    """Return a Chroma metadata filter that matches the canonical clause type
    and any known aliases, or None if we should not filter."""
    if not clause_type or clause_type in _SKIP_MATCH_TYPES:
        return None

    # Gather the set of acceptable metadata "clause" values
    candidates = _CLAUSE_ALIASES.get(clause_type, [clause_type])

    if len(candidates) == 1:
        return {"clause": {"$eq": candidates[0]}}
    return {"clause": {"$in": candidates}}


def query_vectorstore(
    vectorstore: Chroma,
    query_text: str,
    clause_type: str = None,
    document_type: str = None,
    k: int = TOP_K
) -> list:
    try:
        # ── Primary attempt: filter by clause type (most precise) ─────────────
        clause_filter = _get_clause_filter(clause_type)
        results = []

        if clause_filter is not None:
            try:
                results = vectorstore.similarity_search_with_score(
                    query_text,
                    k=k,
                    filter=clause_filter
                )
                logger.info(
                    f"[Query] Retrieved {len(results)} results for '{clause_type}' "
                    f"with type filter: {clause_filter}"
                )
            except Exception as filter_err:
                logger.warning(f"[Query] Clause filter failed ({filter_err}), falling back to unfiltered.")
                results = []

        # ── Fallback: no type filter — return semantic best match ─────────────
        if not results:
            results = vectorstore.similarity_search_with_score(query_text, k=k)
            logger.info(
                f"[Query] Fallback unfiltered — {len(results)} results for query: "
                f"'{query_text[:60]}...'"
            )

        return results

    except Exception as e:
        logger.error(f"Error querying vectorstore: {e}")
        raise