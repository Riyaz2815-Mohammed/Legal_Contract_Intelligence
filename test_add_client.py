import requests

API_URL = "http://localhost:8000"

def test_add_client():
    login_res = requests.post(f"{API_URL}/api/auth/login", json={
        "email": "admin@laccis.com",
        "password": "admin123"
    })
    print(f"Login Status: {login_res.status_code}")
    if login_res.status_code != 200:
        print(f"Login Failed: {login_res.text}")
        return
    token = login_res.json()["token"]
    
    # Add client
    add_res = requests.post(f"{API_URL}/api/clients/create", 
        json={"name": "Test Client", "email": "test@example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {add_res.status_code}")
    print(f"Response: {add_res.text}")

if __name__ == "__main__":
    test_add_client()
