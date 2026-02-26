import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ Missing Supabase credentials in .env")
    exit(1)

try:
    supabase = create_client(url, key)
    # Try to select from users table (which should have the seed admin)
    response = supabase.table("users").select("*").limit(1).execute()
    print(f"✅ Connection successful!")
    print(f"📊 Users found: {len(response.data)}")
    if response.data:
        print(f"👤 First user: {response.data[0]['email']}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
