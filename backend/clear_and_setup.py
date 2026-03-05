import psycopg2
import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "").strip(' "')
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "").strip(' "')
AWS_REGION = os.getenv("REGION", "").strip(' "')
BUCKET_NAME = os.getenv("BUCKET_NAME", "").strip(' "')

def clear_db():
    print("Clearing database tables...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # document_reviews, clauses, etc. are likely cascaded from documents, but let's delete explicitly if needed
        cur.execute("DELETE FROM document_reviews;"); print("Deleted document_reviews")
        cur.execute("DELETE FROM clauses WHERE source = 'client';"); print("Deleted client clauses")
        cur.execute("DELETE FROM documents;"); print("Deleted documents")
        
        # Set up redlined_clauses table
        cur.execute("""
            CREATE EXTENSION IF NOT EXISTS "pgcrypto";
            CREATE TABLE IF NOT EXISTS redlined_clauses (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
                clause_type TEXT NOT NULL,
                content_id TEXT, -- ID of original clause if applicable
                original_content TEXT,
                updated_content TEXT,
                comments TEXT,
                status TEXT DEFAULT 'reviewed',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("Created redlined_clauses table")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database cleared and schema updated successfully.")
    except Exception as e:
        print(f"Error clearing DB: {e}")

def clear_s3():
    print("Clearing S3 bucket...")
    if not BUCKET_NAME:
        print("No BUCKET_NAME set, skipping S3 cleanup.")
        return
        
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION,
            config=Config(connect_timeout=10, read_timeout=30)
        )
        
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET_NAME)

        delete_us = dict(Objects=[])
        for item in pages.search('Contents'):
            if item:
                delete_us['Objects'].append(dict(Key=item['Key']))

                # flush once AWS limit reached
                if len(delete_us['Objects']) >= 1000:
                    s3.delete_objects(Bucket=BUCKET_NAME, Delete=delete_us)
                    delete_us = dict(Objects=[])

        # flush rest
        if len(delete_us['Objects']):
            s3.delete_objects(Bucket=BUCKET_NAME, Delete=delete_us)
            
        print(f"Cleared all objects from S3 bucket '{BUCKET_NAME}'.")
    except Exception as e:
        print(f"Error clearing S3: {e}")

if __name__ == "__main__":
    clear_db()
    clear_s3()
