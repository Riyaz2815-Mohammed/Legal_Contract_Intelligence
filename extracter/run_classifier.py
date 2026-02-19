
import json
import os
from clause_engine import parse_text_file, process_document

def main():
    # File provided by colleague/extraction process
    input_file = "Mutual NDA.txt"
    file_path = os.path.join(os.path.dirname(__file__), input_file)
    
    print(f"Processing: {file_path}")
    
    # 1. Parse text file into blocks
    raw_blocks = parse_text_file(file_path)
    print(f"Found {len(raw_blocks)} text blocks.")
    
    # 2. Classify and structure
    results = process_document(raw_blocks)
    
    # 3. Output
    output_path = os.path.join(os.path.dirname(__file__), "output.json")
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    print(f"Classification complete. Results saved to {output_path}")
    
    # Preview
    for res in results:
        print(f"[{res['page_number']}] {res['clause_id'] or 'None'} - {res['clause']}")

if __name__ == "__main__":
    main()
