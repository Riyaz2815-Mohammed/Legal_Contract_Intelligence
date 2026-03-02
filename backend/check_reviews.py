import psycopg2
from vector_pipeline.config.settings import DATABASE_URL

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Check table structure
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='document_reviews' ORDER BY ordinal_position")
print('Columns in document_reviews:', cur.fetchall())

# Check existing rows
cur.execute("SELECT document_id FROM document_reviews")
rows = cur.fetchall()
print('Rows:', rows)
conn.close()
