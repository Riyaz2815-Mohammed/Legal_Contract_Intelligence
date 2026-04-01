"""
reasoning.py — Calls LLM via generic LangChain wrapper.
Compares client clause vs standard clause and returns concise reasoning + suggestions.
"""
from vector_pipeline.llm.llm_factory import get_llm_instance
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger(__name__)


def run_llm_reasoning(item: dict) -> str:
    """
    Legacy function: called during background pipeline for high-risk clauses.
    """
    try:
        llm = get_llm_instance()
        prompt = f"""You are a legal contract analyst. Analyze this clause briefly.

Clause Type: {item.get('clause', 'Unknown')}
Risk Level: {item.get('final_risk', 'Unknown')}
Clause Text: {item.get('content', '')[:800]}

Give:
1. Why it is risky (2-3 sentences)
2. One clear suggestion to improve it

Be concise and professional."""

        res = llm.invoke([HumanMessage(content=prompt)])
        return res.content
    except Exception as e:
        logger.error(f"LLM reasoning failed: {e}")
        return f"Analysis unavailable: {str(e)}"


def compare_clauses(client_clause: str, standard_clause: str, clause_type: str, risk: str) -> str:
    """
    Called from the ask-llm endpoint.
    Compares client clause vs standard clause and gives reasoning + suggestions.
    """
    try:
        llm = get_llm_instance()

        has_standard = bool(standard_clause and standard_clause.strip())

        if has_standard:
            prompt = f"""You are a legal contract analyst. Compare these two clauses and give a concise review.

Clause Type: {clause_type}
Risk Level: {risk}

CLIENT CLAUSE (uploaded contract):
{client_clause[:1000]}

STANDARD CLAUSE (reference template):
{standard_clause[:800]}

Provide:
1. **Key Differences** — What is different between the two?
2. **Risk Reasoning** — Why is the client clause risky or acceptable?
3. **Suggestion** — One clear, specific improvement to the client clause.

Keep it brief and professional. No bullet sub-points, no headers beyond the 3 above."""
        else:
            prompt = f"""You are a legal contract analyst. Review this clause.

Clause Type: {clause_type}
Risk Level: {risk}

CLIENT CLAUSE:
{client_clause[:1000]}

Provide:
1. **Risk Reasoning** — Why is this clause risky or acceptable?
2. **Suggestion** — One specific improvement.

Keep it brief and professional."""

        res = llm.invoke([HumanMessage(content=prompt)])
        return res.content
    except Exception as e:
        logger.error(f"LLM comparison failed: {e}")
        return f"Analysis unavailable: {str(e)}"
