import sys
import os
import requests
import json
import difflib

# Adjust path and url
API_URL = "http://localhost:8000"

def test_endpoints():
    print("--- Testing LACCIS Redline Features ---")
    
    # Login as admin to get token
    login_res = requests.post(
        f"{API_URL}/api/auth/login",
        json={"email": "admin@laccis.com", "password": "admin"}
    )
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    token = login_res.json().get("token")
    if not token:
        print("No token in login response")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch a document
    print("\n1. Fetching document list...")
    res = requests.get(f"{API_URL}/api/documents/list", headers=headers)
    if res.status_code != 200:
        print(f"Failed to fetch documents: {res.text}")
        return
    docs = res.json().get("documents", [])
    if not docs:
        print("No documents found in database.")
        return
    
    doc_id = docs[0]["id"]
    print(f"Using Document ID: {doc_id}")

    # 2. Get Analysis (Clauses)
    print("\n2. Fetching clauses for document...")
    res = requests.get(f"{API_URL}/api/documents/analysis/{doc_id}", headers=headers)
    if res.status_code != 200:
        print(f"Failed to fetch analysis: {res.text}")
        return
    
    clauses = res.json().get("clauses", [])
    if not clauses:
        print("No clauses found for this document.")
        return
        
    clause_to_edit = clauses[0]
    content_id = clause_to_edit["content_id"]
    original_text = clause_to_edit["content"]
    
    print(f"Selected Clause Content ID: {content_id}")
    print(f"Original Text: {original_text[:50]}...")

    # 3. Edit Clause
    print("\n3. Testing Edit Endpoint...")
    edited_text = original_text + "\n\n[EDITED BY LEGAL TEAM]"
    res = requests.post(
        f"{API_URL}/api/documents/review/{doc_id}/edit", 
        headers=headers,
        json={"content_id": content_id, "edited_content": edited_text}
    )
    print(f"Edit Response: {res.status_code} - {res.text}")

    # 4. Comment on Clause
    print("\n4. Testing Comment Endpoint...")
    res = requests.post(
        f"{API_URL}/api/documents/review/{doc_id}/comment", 
        headers=headers,
        json={"content_id": content_id, "comment": "This clause needs to be reviewed by the managing partner."}
    )
    print(f"Comment Response: {res.status_code} - {res.text}")

    # 5. Verify data saved
    print("\n5. Verifying Analysis Endpoint returns edited data...")
    res = requests.get(f"{API_URL}/api/documents/analysis/{doc_id}", headers=headers)
    updated_clauses = res.json().get("clauses", [])
    updated_clause = next((c for c in updated_clauses if c["content_id"] == content_id), None)
    if updated_clause:
        print(f"Has Edited Content? {'Yes' if updated_clause.get('edited_content') else 'No'}")
        print(f"Has Comment? {'Yes' if updated_clause.get('comment') else 'No'}")
    
    # 6. Download Redline
    print("\n6. Testing Redline Download Endpoint...")
    res = requests.get(f"{API_URL}/api/documents/download-redline/{doc_id}", headers=headers)
    print(f"Download Response: {res.status_code}")
    if res.status_code == 200:
        filename = "test_redline_output.docx"
        with open(filename, "wb") as f:
            f.write(res.content)
        print(f"Successfully saved {filename} ({len(res.content)} bytes)")
    else:
        print(f"Download Error: {res.text}")

if __name__ == "__main__":
    test_endpoints()
