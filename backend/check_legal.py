import psycopg2

DB_URL = "postgresql://postgres.ciclalkhcvzcdrtdpobj:Laccis%4012345%25@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

print("=== All legal clauses in DB ===")
cur.execute("SELECT clause_id, clause, LEFT(content, 100), source FROM clauses WHERE source = 'legal' ORDER BY clause")
rows = cur.fetchall()
print(f"Total: {len(rows)}")
for r in rows:
    print(f"  [{r[1]}] {r[2][:80]}")

conn.close()
