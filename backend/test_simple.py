import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"Connecting to: {url}")
try:
    supabase = create_client(url, key)
    print("Client initialized")
    # Try a simple select
    res = supabase.table("users").select("*", count="exact").limit(1).execute()
    print(f"Success! Data: {res.data}")
except Exception as e:
    print(f"Failed: {e}")
