import os
import sys
from pathlib import Path
import psycopg2
import json
import uuid
import tempfile

# Setup paths
BACKEND_DIR = Path("e:/Yzone/LACCIS/backend")
sys.path.append(str(BACKEND_DIR))
sys.path.append(str(BACKEND_DIR.parent / "extracter"))

# DB
DB_URL = "postgresql://postgres.ciclalkhcvzcdrtdpobj:Laccis%4012345%25@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
UPLOADS_DIR = BACKEND_DIR / "data" / "uploads"

DOC_ID = "doc-06e18d79"
FILE_NAME = "client-b9d52eef_client-side-nda-sample.pdf"
DOC_TYPE = "NDA"
SOURCE = "client"

print(f"Manually triggering extraction for {DOC_ID}...")

# ── Step 1: Extract text ──────────────────────────────────────────────────────
from extract import extract_text_from_file
from clause_engine import parse_text_file, process_document

local_path = UPLOADS_DIR / FILE_NAME
if not local_path.exists():
    print(f"Error: File not found at {local_path}")
    sys.exit(1)

print("Extracting text...")
extracted_text = extract_text_from_file(str(local_path))

print("Parsing clauses...")
with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
    f.write(extracted_text)
    tmp_path = f.name

try:
    extracted_blocks = parse_text_file(tmp_path)
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

print("Classifying...")
raw_results = process_document(extracted_blocks, document=DOC_TYPE, source=SOURCE)

# Merge clauses of same type
merged = {}
for clause in raw_results:
    ctype = clause.get("clause", "Unknown")
    ccontent = clause.get("content", "").strip()
    if ctype not in merged:
        merged[ctype] = {
            "clause_id": f"CLZ-{uuid.uuid4().hex[:8].upper()}",
            "clause": ctype,
            "content_id": f"CNT-{uuid.uuid4().hex[:8].upper()}",
            "content": ccontent,
            "page_number": clause.get("page_number", 1)
        }
    else:
        merged[ctype]["content"] += "\n\n" + ccontent

results = list(merged.values())
print(f"  Found {len(results)} clause types: {[r['clause'] for r in results]}")

# ── Step 2: Save clauses to DB (commit separately) ────────────────────────────
print("\nSaving clauses to DB...")
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Wipe old data cleanly
cur.execute("DELETE FROM document_reviews WHERE document_id = %s", (DOC_ID,))
cur.execute("DELETE FROM clauses WHERE document_id = %s", (DOC_ID,))
conn.commit()
print("  Old data cleared.")

for clause in results:
    cur.execute(
        """
        INSERT INTO clauses (clause_id, clause, content_id, content, page_number, document, source, document_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (clause["clause_id"], clause["clause"], clause["content_id"],
         clause["content"], clause["page_number"], DOC_TYPE, SOURCE, DOC_ID)
    )
conn.commit()
print(f"  Saved {len(results)} clauses.")

conn.close()

# ── Step 3: Run vector pipeline ───────────────────────────────────────────────
print("\nRunning SBERT vector review pipeline...")
from vector_pipeline.pipeline.full_pipeline import run_pipeline

final_reviews = []
for clause in results:
    client_text = clause.get("content", "")
    clause_type = clause.get("clause", "Unknown")
    print(f"  Processing: {clause_type}")

    if len(client_text.strip()) <= 10 or clause_type in ("Header", "Other"):
        final_reviews.append({
            "content_id": clause["content_id"], "clause_id": clause["clause_id"],
            "clause_type": clause_type, "content": client_text,
            "page_number": clause.get("page_number", 1),
            "risk": "Low", "similarity_score": None,
            "matched_clause": None, "llm_reasoning": None, "status": "pending"
        })
        continue

    try:
        pipeline_results = run_pipeline(query_text=client_text, clause_type=clause_type, document_type=DOC_TYPE)
        best = pipeline_results[0] if pipeline_results else None
    except Exception as e:
        print(f"    Pipeline error for {clause_type}: {e}")
        best = None

    if best:
        final_reviews.append({
            "content_id": clause["content_id"], "clause_id": clause["clause_id"],
            "clause_type": clause_type, "content": client_text,
            "page_number": clause.get("page_number", 1),
            "risk": best["final_risk"],
            "similarity_score": best["sbert_similarity"],
            "matched_clause": {"content": best["template_content"]},
            "llm_reasoning": best.get("llm_reasoning"),
            "status": "pending"
        })
        print(f"    -> Risk: {best['final_risk']}, SBERT: {best['sbert_similarity']}")
    else:
        final_reviews.append({
            "content_id": clause["content_id"], "clause_id": clause["clause_id"],
            "clause_type": clause_type, "content": client_text,
            "page_number": clause.get("page_number", 1),
            "risk": "High", "similarity_score": None,
            "matched_clause": None, "llm_reasoning": "No matching standard clause found.",
            "status": "pending"
        })
        print(f"    -> No match found, marked High risk")

# ── Step 4: Save review + update document status ──────────────────────────────
print("\nSaving review data to DB...")
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

cur2.execute("UPDATE documents SET status = 'complete' WHERE id = %s", (DOC_ID,))
conn2.commit()
conn2.close()

print(f"\n✅ Done! Document {DOC_ID} processed with {len(final_reviews)} clause reviews.")
