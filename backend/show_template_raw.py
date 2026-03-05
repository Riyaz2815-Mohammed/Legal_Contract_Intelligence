"""show_template_raw.py — Show raw extracted text and parsed blocks from the template PDF."""
import sys
from pathlib import Path
sys.path.append(str(Path("e:/Yzone/LACCIS/backend")))
sys.path.append(str(Path("e:/Yzone/LACCIS/extracter")))

from extract import extract_text_from_file
from clause_engine import parse_text, classify_clause

TEMPLATE = Path("e:/Yzone/LACCIS/backend/data/uploads/template_d75e8aab_mutualnda.pdf")

print(f"File: {TEMPLATE.name} ({TEMPLATE.stat().st_size} bytes)\n")

text = extract_text_from_file(str(TEMPLATE))
print("=== Raw extracted text ===")
print(text)
print("\n=== Parsed blocks ===")
blocks = parse_text(text)
for i, b in enumerate(blocks, 1):
    heading = b["heading"]
    content = b["content"]
    full = f"{heading}\n{content}".strip()
    label = classify_clause(full)
    print(f"[{i}] Label: '{label}' | Heading: '{heading[:60]}'")
    print(f"     Body: '{content[:120]}'")
    print()
