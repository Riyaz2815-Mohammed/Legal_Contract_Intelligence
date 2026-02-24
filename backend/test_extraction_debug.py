import sys
from pathlib import Path
import os
import json

def test_extraction_standalone(file_name):
    print(f"Testing extraction for: {file_name}")
    try:
        backend_dir = Path(os.getcwd())
        project_root = backend_dir.parent
        extracter_dir = project_root / "extracter"
        
        print(f"Backend Dir: {backend_dir}")
        print(f"Extracter Dir: {extracter_dir}")

        if str(extracter_dir) not in sys.path:
            sys.path.append(str(extracter_dir))
        
        # Import extraction logic
        try:
            from extract import extract_text_from_file
            print("✓ Successfully imported extract_text_from_file")
        except ImportError as e:
            print(f"✗ Failed to import extract: {e}")
            return

        try:
            from clause_engine import parse_text_file, process_document
            print("✓ Successfully imported clause_engine functions")
        except ImportError as e:
            print(f"✗ Failed to import clause_engine: {e}")
            return
        
        # Local path for the file
        uploads_dir = backend_dir / "data" / "uploads"
        local_path = uploads_dir / file_name
        
        if not local_path.exists():
            print(f"✗ File not found at {local_path}")
            return

        print(f"✓ Found file at {local_path}")

        # 1. Extract text
        print("Starting extract_text_from_file...")
        extracted_text = extract_text_from_file(str(local_path))
        print(f"✓ Extracted {len(extracted_text)} characters")
        
        # 2. Save .txt
        extract_docs_dir = extracter_dir / "extracted_texts"
        extract_docs_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = Path(file_name).stem
        txt_path = extract_docs_dir / f"{base_name}.txt"
        
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        print(f"✓ Saved .txt to {txt_path}")
        
        # 3. Classify
        print("Starting classification...")
        raw_blocks = parse_text_file(str(txt_path))
        print(f"✓ Found {len(raw_blocks)} blocks")
        
        results = process_document(raw_blocks)
        print(f"✓ Classified {len(results)} clauses")
        
        json_path = extract_docs_dir / f"{base_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"✓ Saved .json to {json_path}")
        print("--- TEST COMPLETE ---")

    except Exception as e:
        import traceback
        print(f"✗ Error during extraction: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    # Test with one of the files found in uploads
    test_extraction_standalone("client-2_Non Disclosure Agreement.docx")
