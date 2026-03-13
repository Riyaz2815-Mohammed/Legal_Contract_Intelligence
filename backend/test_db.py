import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connection successful")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
