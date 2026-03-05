import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("SELECT column_name, data_type, character_maximum_length, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'clauses';")
rows = cur.fetchall()

print(f"{'Column Name':<20} | {'Data Type':<20} | {'Max Length':<12} | {'Nullable':<8} | {'Default'}")
print("-" * 80)
for r in rows:
    print(f"{str(r[0]):<20} | {str(r[1]):<20} | {str(r[2]):<12} | {str(r[3]):<8} | {str(r[4])}")
