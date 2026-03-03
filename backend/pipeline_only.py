"""
pipeline_only.py — reads clauses already in DB, runs SBERT pipeline, saves review data.
"""
import sys
import json
from pathlib import Path
import psycopg2

BACKEND_DIR = Path("e:/Yzone/LACCIS/backend")
sys.path.append(str(BACKEND_DIR))

DB_URL = "postgresql://postgres.ciclalkhcvzcdrtdpobj:Laccis%4012345%25@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
DOC_ID = "doc-2841761c"
DOC_TYPE = "NDA"

print(f"Running pipeline for {DOC_ID}...")

# Load clauses from DB
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
cur.execute(
    "SELECT clause_id, clause, content_id, content, page_number FROM clauses WHERE document_id = %s",
    (DOC_ID,)
)
rows = cur.fetchall()
conn.close()

if not rows:
    print("ERROR: No clauses found in DB for this document. Run manual_trigger.py first.")
    sys.exit(1)

clauses = [
    {"clause_id": r[0], "clause": r[1], "content_id": r[2], "content": r[3], "page_number": r[4]}
    for r in rows
]
print(f"  Loaded {len(clauses)} clauses.")

# Run SBERT pipeline
from vector_pipeline.pipeline.full_pipeline import run_pipeline

final_reviews = []
for clause in clauses:
    client_text = clause["content"] or ""
    clause_type = clause["clause"]
    print(f"  Processing: {clause_type}")

    if len(client_text.strip()) <= 10 or clause_type in ("Other",):
        final_reviews.append({
            "content_id": clause["content_id"], "clause_id": clause["clause_id"],
            "clause_type": clause_type, "content": client_text,
            "page_number": clause["page_number"],
            "risk": "Low", "similarity_score": None,
            "matched_clause": None, "llm_reasoning": None, "status": "pending"
        })
        continue

    try:
        pipeline_results = run_pipeline(query_text=client_text, clause_type=clause_type, document_type=DOC_TYPE)
        best = pipeline_results[0] if pipeline_results else None
    except Exception as e:
        print(f"    Pipeline error: {e}")
        best = None

    if best:
        final_risk = "Low" if clause_type == "Header" else best["final_risk"]
        final_status = "approved" if clause_type == "Header" else "pending"
        
        final_reviews.append({
            "content_id": clause["content_id"], "clause_id": clause["clause_id"],
            "clause_type": clause_type, "content": client_text,
            "page_number": clause["page_number"],
            "risk": final_risk,
            "similarity_score": best["sbert_similarity"],
            "matched_clause": {"content": best["template_content"]},
            "llm_reasoning": best.get("llm_reasoning"),
            "status": final_status
        })
        print(f"    -> {final_risk} risk, SBERT={best['sbert_similarity']:.3f}")
    else:
        final_reviews.append({
            "content_id": clause["content_id"], "clause_id": clause["clause_id"],
            "clause_type": clause_type, "content": client_text,
            "page_number": clause["page_number"],
            "risk": "Low" if clause_type == "Header" else "High",
            "similarity_score": None,
            "matched_clause": None, "llm_reasoning": "No matching standard clause found.",
            "status": "approved" if clause_type == "Header" else "pending"
        })
        print(f"    -> High risk (no match)")

# Save to DB
print("\nSaving review data...")
conn2 = psycopg2.connect(DB_URL)
cur2 = conn2.cursor()
cur2.execute(
    """
    INSERT INTO document_reviews (document_id, review_data)
    VALUES (%s, %s)
    ON CONFLICT (document_id) DO UPDATE SET review_data = EXCLUDED.review_data
    """,
    (DOC_ID, json.dumps(final_reviews))
)
cur2.execute("UPDATE documents SET status = 'uploaded' WHERE id = %s", (DOC_ID,))
conn2.commit()
conn2.close()

print(f"\n✅ Done! Saved {len(final_reviews)} clause reviews for {DOC_ID}.")
