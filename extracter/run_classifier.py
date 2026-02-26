"""
run_classifier.py
-----------------
Standalone CLI tool to classify clauses in an already-extracted .txt file.

Usage:
    python run_classifier.py
        Processes extracted_texts/Mutual NDA.txt with defaults (NDA / client)

    python run_classifier.py --file "extracted_texts/My Contract.txt" --document MSA --source legal

Output:
    extracted_texts/<basename>.json  — full 7-field clause records
"""

import json
import os
import argparse
from pathlib import Path
from clause_engine import parse_text_file, process_document


def main():
    parser = argparse.ArgumentParser(description="Classify clauses from an extracted text file.")
    parser.add_argument(
        "--file",
        default=os.path.join(os.path.dirname(__file__), "extracted_texts", "Mutual NDA.txt"),
        help="Path to extracted .txt file (default: extracted_texts/Mutual NDA.txt)"
    )
    parser.add_argument(
        "--document",
        default="NDA",
        help="Document type label (e.g. NDA, MSA, SOW, RA). Default: NDA"
    )
    parser.add_argument(
        "--source",
        default="client",
        choices=["client", "legal", "unknown"],
        help="Source of the document — who uploaded it. Default: client"
    )
    args = parser.parse_args()

    file_path = args.file
    document  = args.document
    source    = args.source

    print(f"\n{'='*60}")
    print(f"  LACCIS Clause Classifier")
    print(f"{'='*60}")
    print(f"  File     : {file_path}")
    print(f"  Document : {document}")
    print(f"  Source   : {source}")
    print(f"{'='*60}\n")

    if not os.path.exists(file_path):
        print(f"[X] File not found: {file_path}")
        return

    # 1. Parse text file into blocks
    raw_blocks = parse_text_file(file_path)
    print(f"[*] Found {len(raw_blocks)} text block(s).\n")

    # 2. Classify and structure
    results = process_document(raw_blocks, document=document, source=source)

    # 3. Write output JSON alongside the .txt file (in extracted_texts/)
    base_name   = Path(file_path).stem
    output_dir  = Path(file_path).parent
    output_path = output_dir / (base_name + ".json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[OK] Classification complete --> {output_path}\n")

    # 4. Preview table
    col_widths = {"clause_id": 14, "clause": 26, "content_id": 14, "page": 4, "doc": 10, "src": 8}
    header = (
        f"{'clause_id':<{col_widths['clause_id']}}  "
        f"{'clause':<{col_widths['clause']}}  "
        f"{'content_id':<{col_widths['content_id']}}  "
        f"{'pg':>{col_widths['page']}}  "
        f"{'document':<{col_widths['doc']}}  "
        f"{'source':<{col_widths['src']}}"
    )
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['clause_id']:<{col_widths['clause_id']}}  "
            f"{r['clause']:<{col_widths['clause']}}  "
            f"{r['content_id']:<{col_widths['content_id']}}  "
            f"{str(r['page_number']):>{col_widths['page']}}  "
            f"{r['document']:<{col_widths['doc']}}  "
            f"{r['source']:<{col_widths['src']}}"
        )

    print(f"\n{len(results)} record(s) saved to {output_path}")


if __name__ == "__main__":
    main()
