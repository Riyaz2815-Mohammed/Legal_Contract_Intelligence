import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

sql = """
CREATE TABLE IF NOT EXISTS edited_clauses (
    content_id TEXT PRIMARY KEY REFERENCES clauses(content_id) ON DELETE CASCADE,
    original_clause TEXT NOT NULL,
    edited_clause TEXT,
    comment TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

try:
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("Table edited_clauses created successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
