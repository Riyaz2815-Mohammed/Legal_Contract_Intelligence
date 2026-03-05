"""
One-time sync script:
1. Reads all review JSON files from data/reviews/ and upserts them into document_reviews table
2. Rebuilds ChromaDB from legal clauses already in the DB

Run from: e:\Yzone\LACCIS\backend
  python sync_reviews_and_chroma.py
"""

import os, json, sys
from pathlib import Path
from dotenv import load_dotenv

# ── Load env ──────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not found in .env")
    sys.exit(1)

import psycopg2

# ─────────────────────────────────────────────────────────
# Step 1: Sync JSON review files → document_reviews table
# ─────────────────────────────────────────────────────────
reviews_dir = Path(__file__).parent / "data" / "reviews"
review_files = list(reviews_dir.glob("*.json"))

print(f"\n[STEP 1] Found {len(review_files)} review JSON file(s) to sync\n")

conn = psycopg2.connect(DATABASE_URL)
synced = 0
skipped = 0

for jf in review_files:
    doc_id = jf.stem          # e.g.  "doc-7bc1821c"
    try:
        with open(jf, "r", encoding="utf-8") as f:
            review_data = json.load(f)

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO document_reviews (document_id, review_data)
                SELECT %s, %s
                WHERE EXISTS (SELECT 1 FROM documents WHERE id = %s)
                ON CONFLICT (document_id) DO UPDATE
                  SET review_data = EXCLUDED.review_data,
                      created_at  = NOW()
                """,
                (doc_id, json.dumps(review_data), doc_id)
            )
        conn.commit()
        print(f"  ✅ Synced {jf.name}  ({len(review_data)} clauses)")
        synced += 1
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Failed {jf.name}: {e}")
        skipped += 1

print(f"\n[STEP 1] Done — {synced} synced, {skipped} failed\n")

# ─────────────────────────────────────────────────────────
# Step 2: Rebuild ChromaDB from legal clauses in DB
# ─────────────────────────────────────────────────────────
print("[STEP 2] Rebuilding ChromaDB from legal clauses in DB …\n")

try:
    # Add vector_pipeline to path
    sys.path.insert(0, str(Path(__file__).parent))

    from vector_pipeline.embeddings.embed_store import run_embed_pipeline
    run_embed_pipeline()
    print("\n[STEP 2] ✅ ChromaDB rebuilt successfully")
except Exception as e:
    import traceback
    print(f"\n[STEP 2] ❌ ChromaDB rebuild failed: {e}")
    traceback.print_exc()

conn.close()
print("\n✅ All done.\n")
