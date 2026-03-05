import requests

API_URL = "http://localhost:8000"
DOC_ID = "doc-06e18d79"

# We need a token. I'll use the admin credentials if possible or just try to get it.
# Actually, I can just check the DB to see why 'clauses' is empty.
# But let's check the API first.

print(f"Fetching review for {DOC_ID}...")
try:
    # No auth for this check if I use local DB access or I can just mock the Token
    # Let's just use Python to check the DB properly.
    import psycopg2
    # Check connection string from main.py or common defaults
    conn = psycopg2.connect("dbname=laccis user=postgres password=postgres host=localhost port=5432")
    cur = conn.cursor()
    
    cur.execute("SELECT status, filename FROM documents WHERE id = %s", (DOC_ID,))
    doc = cur.fetchone()
    print(f"Document record: {doc}")
    
    cur.execute("SELECT COUNT(*) FROM clauses WHERE document_id = %s", (DOC_ID,))
    clause_count = cur.fetchone()[0]
    print(f"Clause count in DB: {clause_count}")
    
    cur.execute("SELECT review_data FROM document_reviews WHERE document_id = %s", (DOC_ID,))
    review = cur.fetchone()
    print(f"Review data in DB present: {review is not None}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
