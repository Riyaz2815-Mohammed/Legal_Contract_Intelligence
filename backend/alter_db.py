import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
DB_URL = os.environ.get("DATABASE_URL")

try:
    conn = psycopg2.connect(DB_URL)
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE shared_contracts ADD COLUMN IF NOT EXISTS is_finalized BOOLEAN NOT NULL DEFAULT FALSE;")
    conn.commit()
    print("Column is_finalized added to shared_contracts successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
