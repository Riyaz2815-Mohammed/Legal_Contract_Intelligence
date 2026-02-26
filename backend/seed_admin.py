import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

try:
    supabase = create_client(url, key)
    admin_user = {
        "id": "admin-1",
        "name": "Legal Team Admin",
        "email": "admin@laccis.com",
        "password_hash": "admin123",  # Correct schema: password_hash
        "role": "admin",
        "created_at": datetime.now().isoformat()
    }
    
    print(f"Seeding admin user into {url}...")
    res = supabase.table("users").upsert(admin_user).execute()
    print(f"[SUCCESS] Admin user seeded: {res.data}")
except Exception as e:
    print(f"[ERROR] Seeding failed: {e}")
