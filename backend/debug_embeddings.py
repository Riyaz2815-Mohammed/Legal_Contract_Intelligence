import psycopg2
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent))

from vector_pipeline.config.settings import DATABASE_URL
from vector_pipeline.embeddings.embed_store import fetch_legal_clauses, run_embed_pipeline

conn = None
try:
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM clauses WHERE source = 'legal'")
        raw_count = cur.fetchone()[0]
        print(f"Total legal clauses in DB: {raw_count}")

        cur.execute("SELECT count(*) FROM clause_embeddings")
        embed_count = cur.fetchone()[0]
        print(f"Total embeddings in DB: {embed_count}")

        # Check document types in clauses vs embeddings
        cur.execute("SELECT DISTINCT document FROM clauses WHERE source = 'legal'")
        print("Documents in clauses:", [r[0] for r in cur.fetchall()])

        cur.execute("SELECT DISTINCT document FROM clause_embeddings")
        print("Documents in embeddings:", [r[0] for r in cur.fetchall()])

    print("\n--- Running embedding pipeline manually ---")
    run_embed_pipeline()

except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    if conn:
        conn.close()
