import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def add_nda_rejected_column():
    conn = None
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        print("Checking/Adding nda_rejected column to users table...")
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS nda_rejected BOOLEAN DEFAULT FALSE")
        conn.commit()
        print("Colum nda_rejected added successfully or already exists.")
        cur.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_nda_rejected_column()
