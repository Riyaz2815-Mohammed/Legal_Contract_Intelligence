"""
reclassify_templates.py
Re-extracts all legal template PDF files using the NEW clause_engine and
stores individual, correctly-classified clause sections back to the DB.
Then triggers a ChromaDB rebuild.
"""
import sys
import os
import uuid
import shutil
import psycopg2
from pathlib import Path

BACKEND_DIR = Path("e:/Yzone/LACCIS/backend")
sys.path.append(str(BACKEND_DIR))
sys.path.append(str(BACKEND_DIR.parent / "extracter"))

DB_URL = "postgresql://postgres.ciclalkhcvzcdrtdpobj:Laccis%4012345%25@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
UPLOADS_DIR = BACKEND_DIR / "data" / "uploads"

print("=== Reclassifying legal template clauses ===\n")

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Find template documents (document_type = 'template' OR user_role = 'legal_team')
cur.execute("""
    SELECT DISTINCT d.id, d.filename, d.s3_key, d.document_type
    FROM documents d
    INNER JOIN clauses c ON c.document_id = d.id
    WHERE c.source = 'legal'
    ORDER BY d.id
""")
templates = cur.fetchall()
print(f"Found {len(templates)} legal template documents:")
for t in templates:
    print(f"  {t[0]}: {t[1]} ({t[3]})")

if not templates:
    # Try broader query
    cur.execute("""
        SELECT id, filename, s3_key, document_type
        FROM documents
        WHERE document_type = 'template'
        ORDER BY uploaded_at DESC
    """)
    templates = cur.fetchall()
    print(f"  (fallback) Found {len(templates)} template-type documents:")
    for t in templates:
        print(f"  {t[0]}: {t[1]} ({t[3]})")

if not templates:
    print("ERROR: No legal templates found. Upload a standard template first.")
    conn.close()
    sys.exit(1)

# Re-extract each template file
from extract import extract_text_from_file
from clause_engine import parse_text, classify_clause

all_new_clauses = []

for doc_id, filename, s3_key, doc_type in templates:
    # Try various locations for the file
    candidates = [
        UPLOADS_DIR / filename,
    ]
    if s3_key:
        candidates.append(UPLOADS_DIR / Path(s3_key).name)
    # Also check if filename is a full path
    candidates.append(Path(filename))

    local_path = None
    for c in candidates:
        if c.exists():
            local_path = c
            break

    if local_path is None:
        print(f"\n  [{doc_id}] File not found, searching uploads dir...")
        # Search for any file matching part of the filename
        base = Path(filename).stem[:20]
        found = list(UPLOADS_DIR.glob(f"*{base}*"))
        if found:
            local_path = found[0]
            print(f"    Found: {local_path.name}")
        else:
            all_files = list(UPLOADS_DIR.iterdir())
            print(f"    Files in uploads: {[f.name for f in all_files[:10]]}")
            print(f"  Skipping {doc_id}.")
            continue

    print(f"\n  [{doc_id}] Extracting: {local_path.name}")
    try:
        text = extract_text_from_file(str(local_path))
    except Exception as e:
        print(f"    Extraction error: {e}")
        continue

    blocks = parse_text(text)
    print(f"    Parsed {len(blocks)} raw blocks")

    for block in blocks:
        heading = block.get("heading", "").strip()
        body = block.get("content", "").strip()
        full_text = f"{heading}\n{body}".strip()
        clause_type = classify_clause(full_text)
        print(f"    -> [{clause_type}] {heading[:60]}")
        all_new_clauses.append({
            "clause_id":   f"CLZ-{uuid.uuid4().hex[:8].upper()}",
            "clause":      clause_type,
            "content_id":  f"CNT-{uuid.uuid4().hex[:8].upper()}",
            "content":     full_text,
            "page_number": block.get("page_number", 1),
            "document":    doc_type or "template",
            "source":      "legal",
            "document_id": doc_id,
        })

print(f"\n  Total new clause rows: {len(all_new_clauses)}")
type_counts = {}
for c in all_new_clauses:
    type_counts[c["clause"]] = type_counts.get(c["clause"], 0) + 1
print(f"  Types: {dict(sorted(type_counts.items()))}")

# Wipe existing legal clauses and re-insert
print("\n  Clearing old legal clauses from DB...")
cur.execute("DELETE FROM clauses WHERE source = 'legal'")
conn.commit()

print(f"  Inserting {len(all_new_clauses)} new clauses...")
for clause in all_new_clauses:
    cur.execute("""
        INSERT INTO clauses (clause_id, clause, content_id, content, page_number, document, source, document_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (content_id) DO NOTHING
    """, (
        clause["clause_id"], clause["clause"], clause["content_id"],
        clause["content"], clause["page_number"], clause["document"],
        clause["source"], clause["document_id"]
    ))
conn.commit()
conn.close()
print("  DB updated.")

# Rebuild ChromaDB
print("\n  Rebuilding ChromaDB...")
from vector_pipeline.config.settings import CHROMA_PERSIST_DIR
from vector_pipeline.embeddings.embed_store import get_embedding_model, fetch_legal_clauses, build_documents, embed_and_store

chroma_path = Path(CHROMA_PERSIST_DIR)
if chroma_path.exists():
    shutil.rmtree(chroma_path)

model = get_embedding_model()
df = fetch_legal_clauses()
print(f"  Fetched {len(df)} legal clauses from DB")
print(f"  Types: {sorted(df['clause'].unique().tolist())}")

docs = build_documents(df)
vs = embed_and_store(docs, model)
print(f"  ChromaDB rebuilt with {vs._collection.count()} chunks.")
print("\nDone! Restart the backend server to use the updated knowledge base.")
