import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

try:
    conn = psycopg2.connect(DB_URL)
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS client_marked_final BOOLEAN NOT NULL DEFAULT FALSE;")
    conn.commit()
    print("Column client_marked_final added to documents successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
