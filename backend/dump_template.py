"""dump_template.py — Dump all legal clause content to a text file for inspection."""
import sys
from pathlib import Path
sys.path.append(str(Path("e:/Yzone/LACCIS/backend")))
sys.path.append(str(Path("e:/Yzone/LACCIS/extracter")))

from extract import extract_text_from_file
from clause_engine import parse_text, classify_clause

TEMPLATE = Path("e:/Yzone/LACCIS/backend/data/uploads/template_d75e8aab_mutualnda.pdf")
text = extract_text_from_file(str(TEMPLATE))

# Write raw text to file
out = Path("e:/Yzone/LACCIS/backend/template_raw.txt")
out.write_text(text, encoding="utf-8")
print(f"Raw text written to: {out} ({len(text)} chars)")

# Parse and classify
blocks = parse_text(text)
print(f"\n=== {len(blocks)} Parsed Blocks ===")
for i, b in enumerate(blocks, 1):
    heading = b["heading"]
    content = b["content"]
    full = f"{heading}\n{content}".strip()
    label = classify_clause(full)
    print(f"\n[{i}] Label: '{label}'")
    print(f"    Heading: {heading[:80]}")
    print(f"    Body (first 200 chars): {content[:200]}")
