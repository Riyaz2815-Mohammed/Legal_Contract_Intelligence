"""
restore_client_doc.py
Downloads the client document from S3 and re-runs extraction + SBERT pipeline.
"""
import sys, os, uuid, json, tempfile, boto3
import psycopg2
from pathlib import Path

BACKEND_DIR = Path("e:/Yzone/LACCIS/backend")
sys.path.append(str(BACKEND_DIR))
sys.path.append(str(BACKEND_DIR.parent / "extracter"))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

DB_URL = "postgresql://postgres.ciclalkhcvzcdrtdpobj:Laccis%4012345%25@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
DOC_ID = "doc-06e18d79"
DOC_TYPE = "NDA"

# 1. Get S3 details from DB
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
cur.execute("SELECT s3_key, s3_url, filename FROM documents WHERE id = %s", (DOC_ID,))
row = cur.fetchone()
if not row:
    print("ERROR: Document not found in DB")
    sys.exit(1)

s3_key, s3_url, filename = row
print(f"Doc: {DOC_ID}, file: {filename}, s3_key: {s3_key}")

# 2. Download from S3
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "eu-north-1")
)
BUCKET = os.getenv("S3_BUCKET_NAME", "laccis-contracts")
local_pdf = BACKEND_DIR / "data" / "uploads" / filename
print(f"Downloading from S3 bucket={BUCKET}, key={s3_key} => {local_pdf}")
s3.download_file(BUCKET, s3_key, str(local_pdf))
print(f"Downloaded: {local_pdf.stat().st_size} bytes")

# 3. Extract + classify
from extract import extract_text_from_file
from clause_engine import parse_text, classify_clause

text = extract_text_from_file(str(local_pdf))
blocks = parse_text(text)
print(f"Parsed {len(blocks)} blocks")

# Merge client clauses by type
merged = {}
for block in blocks:
    heading = block.get("heading", "").strip()
    body = block.get("content", "").strip()
    full_text = f"{heading}\n{body}".strip()
    clause_type = classify_clause(full_text)
    print(f"  -> [{clause_type}] {heading[:60]}")
    if clause_type not in merged:
        merged[clause_type] = {
            "clause_id":   f"CLZ-{uuid.uuid4().hex[:8].upper()}",
            "clause":      clause_type,
            "content_id":  f"CNT-{uuid.uuid4().hex[:8].upper()}",
            "content":     full_text,
            "page_number": block.get("page_number", 1),
        }
    else:
        merged[clause_type]["content"] += "\n\n" + full_text

clauses = list(merged.values())
print(f"\nMerged into {len(clauses)} clause types")

# 4. Save clauses to DB
cur.execute("DELETE FROM document_reviews WHERE document_id = %s", (DOC_ID,))
cur.execute("DELETE FROM clauses WHERE document_id = %s", (DOC_ID,))
conn.commit()

for c in clauses:
    cur.execute("""
        INSERT INTO clauses (clause_id, clause, content_id, content, page_number, document, source, document_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (c["clause_id"], c["clause"], c["content_id"], c["content"],
          c["page_number"], DOC_TYPE, "client", DOC_ID))
conn.commit()
print(f"Saved {len(clauses)} clauses to DB")

# 5. SBERT pipeline
print("\nRunning SBERT pipeline...")
from vector_pipeline.pipeline.full_pipeline import run_pipeline

final_reviews = []
for clause in clauses:
    client_text = clause["content"]
    clause_type = clause["clause"]
    print(f"  Processing: {clause_type}")

    if len(client_text.strip()) <= 10 or clause_type in ("Header", "Other"):
        final_reviews.append({
            "content_id": clause["content_id"], "clause_id": clause["clause_id"],
            "clause_type": clause_type, "content": client_text,
            "page_number": clause["page_number"],
            "risk": "Low", "similarity_score": None,
            "matched_clause": None, "llm_reasoning": None, "status": "pending"
        })
        continue

    try:
        results = run_pipeline(query_text=client_text, clause_type=clause_type, document_type=DOC_TYPE)
        best = results[0] if results else None
    except Exception as e:
        print(f"    Error: {e}")
        best = None

    if best:
        final_reviews.append({
            "content_id": clause["content_id"], "clause_id": clause["clause_id"],
            "clause_type": clause_type, "content": client_text,
            "page_number": clause["page_number"],
            "risk": best["final_risk"],
            "similarity_score": best["sbert_similarity"],
            "matched_clause": {"content": best["template_content"]},
            "llm_reasoning": best.get("llm_reasoning"),
            "status": "pending"
        })
        print(f"    -> {best['final_risk']} risk, SBERT={best['sbert_similarity']:.3f}")
    else:
        final_reviews.append({
            "content_id": clause["content_id"], "clause_id": clause["clause_id"],
            "clause_type": clause_type, "content": client_text,
            "page_number": clause["page_number"],
            "risk": "High", "similarity_score": None,
            "matched_clause": None, "llm_reasoning": "No matching standard clause found.",
            "status": "pending"
        })
        print(f"    -> High risk (no match)")

# 6. Save reviews
cur.execute("""
    INSERT INTO document_reviews (document_id, review_data)
    VALUES (%s, %s)
    ON CONFLICT (document_id) DO UPDATE SET review_data = EXCLUDED.review_data
""", (DOC_ID, json.dumps(final_reviews)))
cur.execute("UPDATE documents SET status = 'uploaded' WHERE id = %s", (DOC_ID,))
conn.commit()
conn.close()

print(f"\nDone! {len(final_reviews)} clause reviews saved for {DOC_ID}.")
