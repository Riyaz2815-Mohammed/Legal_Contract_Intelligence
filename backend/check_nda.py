import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_nda():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        cur.execute("SELECT id, filename, document_type, template_type FROM documents WHERE document_type = 'template' AND template_type = 'NDA'")
        rows = cur.fetchall()
        print(f"Found {len(rows)} NDA templates:")
        for row in rows:
            print(row)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_nda()
