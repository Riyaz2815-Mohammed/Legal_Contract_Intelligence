import psycopg2
from vector_pipeline.config.settings import DATABASE_URL
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='documents' ORDER BY ordinal_position")
print('documents columns:', [r[0] for r in cur.fetchall()])

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='clauses' ORDER BY ordinal_position")
print('clauses columns:', [r[0] for r in cur.fetchall()])

# Also show current data counts
cur.execute("SELECT COUNT(*) FROM documents")
print('Total documents:', cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM clauses")
print('Total clauses:', cur.fetchone()[0])

cur.execute("SELECT id, filename, document_type FROM documents")
for r in cur.fetchall():
    print(f"  Doc: {r[0]} | {r[1]} | type={r[2]}")

conn.close()
