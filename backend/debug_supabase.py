import psycopg2

DB_URL = "postgresql://postgres.ciclalkhcvzcdrtdpobj:Laccis%4012345%25@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
DOC_ID = "doc-06e18d79"

print(f"Checking Supabase for {DOC_ID}...")
try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT id, status, filename, uploaded_at FROM documents WHERE id = %s", (DOC_ID,))
    doc = cur.fetchone()
    print(f"Document: {doc}")
    
    cur.execute("SELECT COUNT(*) FROM clauses WHERE document_id = %s", (DOC_ID,))
    clause_count = cur.fetchone()[0]
    print(f"Clause count in 'clauses' table: {clause_count}")
    
    cur.execute("SELECT COUNT(*) FROM document_reviews WHERE document_id = %s", (DOC_ID,))
    review_count = cur.fetchone()[0]
    print(f"Review count in 'document_reviews' table: {review_count}")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
