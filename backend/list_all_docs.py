import psycopg2
DB_URL = "postgresql://postgres.ciclalkhcvzcdrtdpobj:Laccis%4012345%25@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()
print("=== ALL documents ===")
cur.execute("SELECT id, filename, document_type, user_role, status, s3_key FROM documents ORDER BY uploaded_at DESC LIMIT 20")
for r in cur.fetchall():
    print(r)
conn.close()
