# backend/llm/reasoner.py

import os
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API", "")


def ask_llm(clause_text: str, clause_type: str, question: str) -> str:
    """
    Ask Mistral's chat model about a specific contract clause.

    Args:
        clause_text:  The full text of the clause.
        clause_type:  Classified clause type (e.g. 'Indemnity').
        question:     The user's question about the clause.

    Returns:
        The model's text response, or an error message string.
    """
    if not MISTRAL_API_KEY:
        return "⚠️ Mistral API key not configured. Please set MISTRAL_API in your .env file."

    try:
        from mistralai import Mistral

        client = Mistral(api_key=MISTRAL_API_KEY.strip().strip('"'))

        system_prompt = (
            "You are an expert legal analyst specialising in contract law. "
            "You receive a contract clause and a user question. "
            "Give a clear, concise, professional answer. "
            "Highlight any potential risks or ambiguities. "
            "Do not give specific legal advice — recommend consulting a qualified solicitor for binding decisions."
        )

        user_message = (
            f"**Clause Type**: {clause_type}\n\n"
            f"**Clause Text**:\n{clause_text}\n\n"
            f"**Question**: {question}"
        )

        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            max_tokens=600,
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except ImportError:
        return "⚠️ mistralai package is not installed. Run: pip install mistralai"
    except Exception as e:
        return f"⚠️ LLM error: {str(e)}"
