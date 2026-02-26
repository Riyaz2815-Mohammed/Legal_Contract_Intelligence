import os
import json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load settings
load_dotenv()
USERS_FILE = Path("data/users.json")
DOCS_FILE = Path("data/documents.json")
MSGS_FILE = Path("data/messages.json")
SHARED_FILE = Path("data/shared_contracts.json")
ACTIVITY_FILE = Path("data/activity_log.json")

# Users to keep
KEEP_IDS = ["admin-1", "legal-2"] 
# Ensure we don't accidentally delete everything if connection fails
CONNECTED_TO_SUPABASE = False
def load_json(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def cleanup():
    print("[CLEANUP] Starting Database Cleanup...")
    
    # --- Supabase Cleanup ---
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key:
        try:
            supabase = create_client(url, key)
            print("Connected to Supabase.")
            
            # Fetch all users to identify who to delete
            res = supabase.table("users").select("id").execute()
            all_ids = [u["id"] for u in res.data]
            to_delete = [uid for uid in all_ids if uid not in KEEP_IDS]
            
            if to_delete:
                print(f"Deleting {len(to_delete)} users from Supabase...")
                for uid in to_delete:
                    # Cascade delete should handle related table rows
                    supabase.table("users").delete().eq("id", uid).execute()
                print("Supabase cleanup finished (Users & Cascaded data).")
            
            # Additional cleanup for activities if needed (though cascade should handle it)
            # supabase.table("activity_log").delete().neq("user_id", KEEP_IDS[0]).neq("user_id", KEEP_IDS[1]).execute()
            
        except Exception as e:
            print(f"Supabase Cleanup Error: {e}")
    else:
        print("Skipping Supabase (no credentials).")

    # --- Local JSON Cleanup ---
    users = load_json(USERS_FILE)
    filtered_users = [u for u in users if u["id"] in KEEP_IDS]
    save_json(USERS_FILE, filtered_users)
    print(f"Local Users: Kept {len(filtered_users)}, removed {len(users) - len(filtered_users)}")

    # Activities
    activities = load_json(ACTIVITY_FILE)
    filtered_activities = [a for a in activities if a.get("user_id") in KEEP_IDS]
    save_json(ACTIVITY_FILE, filtered_activities)
    print(f"Local Activities: Kept {len(filtered_activities)}, removed {len(activities) - len(filtered_activities)}")

    # Messages
    msgs = load_json(MSGS_FILE)
    filtered_msgs = [m for m in msgs if m.get("sender_id") in KEEP_IDS and m.get("recipient_id") in KEEP_IDS]
    save_json(MSGS_FILE, filtered_msgs)
    print(f"Local Messages: Kept {len(filtered_msgs)}, removed {len(msgs) - len(filtered_msgs)}")

    # Documents
    docs = load_json(DOCS_FILE)
    filtered_docs = [d for d in docs if d.get("user_id") in KEEP_IDS]
    save_json(DOCS_FILE, filtered_docs)
    print(f"Local Documents: Kept {len(filtered_docs)}, removed {len(docs) - len(filtered_docs)}")

    # Shared Contracts - Only keep if both parties are in KEEP_IDS
    shared = load_json(SHARED_FILE)
    filtered_shared = [s for s in shared if s.get("client_id") in KEEP_IDS and s.get("shared_by") in KEEP_IDS]
    save_json(SHARED_FILE, filtered_shared)
    print(f"Local Shared Contracts: Kept {len(filtered_shared)}, removed {len(shared) - len(filtered_shared)}")

    print("[SUCCESS] Cleanup Complete.")

if __name__ == "__main__":
    cleanup()
