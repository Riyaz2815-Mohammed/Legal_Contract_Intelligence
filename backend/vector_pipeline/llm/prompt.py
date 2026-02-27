from langchain_core.prompts import PromptTemplate

LEGAL_ANALYSIS_PROMPT = PromptTemplate.from_template("""
You are an expert legal contract analyst.

Clause Type     : {clause_type}
Clause Content  : {content}
SBERT Similarity: {sbert_score}
Keyword Risk    : {keyword_risk}
Score Risk      : {score_risk}
Overall Risk    : {final_risk}

Based on the above, provide:
1. Why this clause is risky
2. Potential legal consequences
3. Suggested mitigation or rephrasing
4. Risk confidence score out of 10

Be concise and professional.
""")