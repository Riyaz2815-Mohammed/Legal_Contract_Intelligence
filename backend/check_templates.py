import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
with conn.cursor() as cur:
    # Check legal clauses
    cur.execute("SELECT DISTINCT document FROM clauses WHERE source = 'legal'")
    print("Legal document types in DB:", [r[0] for r in cur.fetchall()])
    
    # Check client clauses
    cur.execute("SELECT DISTINCT document FROM clauses WHERE source = 'client'")
    print("Client document types in DB:", [r[0] for r in cur.fetchall()])
conn.close()
