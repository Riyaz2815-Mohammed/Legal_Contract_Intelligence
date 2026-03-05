"""get_doc_info.py — Get document info for re-extraction."""
import psycopg2
DB_URL = "postgresql://postgres.ciclalkhcvzcdrtdpobj:Laccis%4012345%25@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

cur.execute("""
    SELECT id, filename, s3_key, s3_url, document_type, user_role, status
    FROM documents
    WHERE id = 'doc-7e568fa7'
""")
row = cur.fetchone()
if row:
    print(f"id: {row[0]}")
    print(f"filename: {row[1]}")
    print(f"s3_key: {row[2]}")
    print(f"s3_url: {row[3]}")
    print(f"doc_type: {row[4]}")
    print(f"user_role: {row[5]}")
    print(f"status: {row[6]}")
else:
    print("NOT FOUND")

print("\n=== All clauses for doc-7e568fa7 ===")
cur.execute("SELECT clause, source, LEFT(content, 60) FROM clauses WHERE document_id = 'doc-7e568fa7'")
for r in cur.fetchall(): print(r)

conn.close()
