
import jwt
from datetime import datetime, timedelta
import requests

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

def create_token(user_id, email, role):
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def test_download(endpoint, token):
    url = f"http://localhost:8000{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Testing {url}...")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        if response.status_code != 200:
            print(f"Body: {response.text}")
        else:
            print(f"Preview: {response.content[:100]}")
    except Exception as e:
        print(f"Error: {e}")

# Admin Token
admin_token = create_token("admin-1", "admin@laccis.com", "admin")
# Client Token
client_token = create_token("client-0c599bf9", "saravanavel.1136@gmail.com", "client")

print("--- TESTING DOWNLOAD SHARED CONTRACT (Issue 1) ---")
test_download("/api/contracts/download/sc-ac5e9798", client_token)

print("\n--- TESTING DOWNLOAD TEMPLATE (Issue 2) ---")
test_download("/api/templates/download/tmpl-a0cf29ee", admin_token)

print("\n--- TESTING DOWNLOAD DOCUMENT (Issue 3) ---")
test_download("/api/documents/download/doc-2", admin_token)
