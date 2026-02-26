import os
from dotenv import load_dotenv
from supabase import create_client, Client, ClientOptions
from httpx import Timeout

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"URL: {SUPABASE_URL}")
print(f"KEY: {SUPABASE_KEY}")

try:
    supabase = create_client(
        SUPABASE_URL, 
        SUPABASE_KEY,
        options=ClientOptions(
            postgrest_client_timeout=Timeout(10.0),
            storage_client_timeout=Timeout(10.0)
        )
    )
    print("[SUCCESS] Client initialized")
    res = supabase.table("users").select("count", count="exact").execute()
    print(f"[SUCCESS] Connection works! User count: {res.count}")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
