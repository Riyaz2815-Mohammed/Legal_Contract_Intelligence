"""inspect_legal_clauses.py — Show full content and classification of all legal clauses."""
import sys
from pathlib import Path
sys.path.append(str(Path("e:/Yzone/LACCIS/backend")))
sys.path.append(str(Path("e:/Yzone/LACCIS/extracter")))
import psycopg2
from clause_engine import classify_clause

DB_URL = "postgresql://postgres.ciclalkhcvzcdrtdpobj:Laccis%4012345%25@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

cur.execute("SELECT clause, content FROM clauses WHERE source = 'legal' ORDER BY page_number")
rows = cur.fetchall()
conn.close()

print(f"=== {len(rows)} Legal Clauses in DB ===\n")
for i, (clause, content) in enumerate(rows, 1):
    # Re-classify using the current engine
    reclassified = classify_clause(content)
    match = "OK" if reclassified == clause else f"MISMATCH -> {reclassified}"
    print(f"[{i}] DB Type: '{clause}' | Re-check: {match}")
    print(f"    Content: {content[:150]}...")
    print()
