import psycopg2

DB_URL = "postgresql://postgres.ciclalkhcvzcdrtdpobj:Laccis%4012345%25@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

print("=== All client NDA documents ===")
cur.execute("""
    SELECT id, filename, document_type, status, s3_key, s3_url
    FROM documents
    WHERE document_type = 'NDA' OR (user_role = 'client' AND document_type != 'template')
    ORDER BY uploaded_at DESC
    LIMIT 10
""")
for r in cur.fetchall():
    print(r)

print("\n=== All documents ===")
cur.execute("SELECT id, filename, document_type, user_role, status FROM documents ORDER BY uploaded_at DESC LIMIT 10")
for r in cur.fetchall():
    print(r)

print("\n=== Clause counts by document ===")
cur.execute("SELECT document_id, source, COUNT(*) FROM clauses GROUP BY document_id, source ORDER BY document_id")
for r in cur.fetchall():
    print(r)

conn.close()
