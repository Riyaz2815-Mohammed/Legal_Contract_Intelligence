
import os
import json
from pathlib import Path

DATA_DIR = Path("data")
DOCUMENTS_FILE = DATA_DIR / "documents.json"
SHARED_CONTRACTS_FILE = DATA_DIR / "shared_contracts.json"
TEMPLATES_FILE = DATA_DIR / "standard_templates.json"

def check_files(file_path):
    print(f"\nChecking {file_path}...")
    if not file_path.exists():
        print(f"  FAILED: {file_path} does not exist")
        return
    with open(file_path, 'r') as f:
        data = json.load(f)
    for item in data:
        p = item.get("file_path")
        if p:
            exists = Path(p).exists()
            print(f"  {'✅' if exists else '❌'} {p}")
        else:
            print(f"  ❓ No file_path for {item.get('id')}")

print(f"CWD: {os.getcwd()}")
check_files(DOCUMENTS_FILE)
check_files(SHARED_CONTRACTS_FILE)
check_files(TEMPLATES_FILE)
