import os
import sys

# Append backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(".env")

import psycopg2
from main import trigger_extraction

def reprocess_all():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        with conn.cursor() as cur:
            cur.execute("SELECT id, file_name, document_type FROM documents WHERE source = 'client'")
            docs = cur.fetchall()
            
        print(f"Found {len(docs)} client documents to reprocess.")
        for doc_id, file_name, doc_type in docs:
            print(f"Reprocessing {doc_id} / {file_name}")
            trigger_extraction(file_name, doc_type, 'client', document_id=doc_id)
            
        print("All documents reprocessed.")
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    reprocess_all()
