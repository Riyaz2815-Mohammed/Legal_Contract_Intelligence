import re
import uuid
import spacy
import os
from typing import List, Dict, Optional, Any

# Attempt to load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None


def extract_structural_id(text: str) -> Optional[str]:
    """
    Extracts structural clause numbering (e.g., "1.", "2.1", "Section 3", "(a)")
    from the start of the text. Used as a label – NOT used as the unique clause_id.
    """
    patterns = [
        r"^(Section\s+\d+(\.\d+)*)",     # Section 1, Section 1.2
        r"^(Article\s+\d+(\.\d+)*)",     # Article 1
        r"^(\d+(\.\d+)+)",               # 1.1, 1.1.1 (multi-part)
        r"^(\d+\.)",                     # 1. (simple)
        r"^(\([a-zA-Z0-9]+\))",          # (a), (1)
        r"^([a-zA-Z]\.)",                # a. , b.
        r"^([IVXLCDM]+\.)",              # Roman numerals I., IV.
    ]

    for pattern in patterns:
        match = re.match(pattern, text.strip(), re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def classify_clause(text: str) -> str:
    """
    Classifies the clause text into a standardized type using rules and keywords.
    """
    if not nlp:
        doc = None
    else:
        doc = nlp(text.lower())

    text_lower = text.lower()

    rules = {
        "Indemnity": ["indemnify", "indemnification", "hold harmless"],
        "Limitation of Liability": ["limitation of liability", "cap on liability", "exclude liability", "consequential damages"],
        "Confidentiality": ["confidential", "non-disclosure", "proprietary information"],
        "Termination": ["terminate", "termination", "cancellation", "term and termination"],
        "Payment Terms": ["payment", "invoice", "fees", "billing"],
        "SLA": ["service level", "sla", "uptime", "availability"],
        "Governing Law": ["governing law", "choice of law", "jurisdiction", "laws of"],
        "Jurisdiction": ["jurisdiction", "venue", "courts of"],
        "Force Majeure": ["force majeure", "act of god", "unforeseen circumstances"],
        "Intellectual Property": ["intellectual property", "ip rights", "copyright", "trademark", "ownership"],
        "Warranty": ["warranty", "warranties", "represent and warrant"],
        "Data Protection": ["data protection", "gdpr", "personal data", "privacy"],
    }

    scores = {category: 0 for category in rules}

    tokens = [token.lemma_ for token in doc] if doc else text_lower.split()
    token_text = " ".join(tokens)

    for category, keywords in rules.items():
        for keyword in keywords:
            if keyword in token_text or keyword in text_lower:
                scores[category] += 1

    best_match = max(scores, key=scores.get)

    if scores[best_match] > 0:
        return best_match

    return "Other"


def parse_text_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parses a text file with 'PAGE X' delimiters and clause numbering.
    Returns a list of blocks like {"page_number": 1, "raw_text": "..."}
    """
    extracted_blocks = []

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return []

    current_page = 1
    current_text_lines = []
    current_block_start_page = 1

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line_stripped = line.strip()

        # Check for Page Header
        page_match = re.match(r"^PAGE\s+(\d+)", line_stripped, re.IGNORECASE)
        if page_match:
            current_page = int(page_match.group(1))
            continue

        # Skip separator lines
        if re.match(r"^-+$", line_stripped):
            continue

        if not line_stripped:
            continue

        # Check if line starts a new clause
        is_new_clause = extract_structural_id(line_stripped) is not None

        if is_new_clause:
            # Save previous block if exists
            if current_text_lines:
                full_text = " ".join(current_text_lines)
                extracted_blocks.append({
                    "page_number": current_block_start_page,
                    "raw_text": full_text
                })

            # Start new block
            current_text_lines = [line_stripped]
            current_block_start_page = current_page
        else:
            # If no block started (e.g., preamble), start one
            if not current_text_lines:
                current_block_start_page = current_page

            # Append to current
            current_text_lines.append(line_stripped)

    # Flush last block
    if current_text_lines:
        full_text = " ".join(current_text_lines)
        extracted_blocks.append({
            "page_number": current_block_start_page,
            "raw_text": full_text
        })

    return extracted_blocks


def process_document(
    extracted_blocks: List[Dict[str, Any]],
    document: str = "Unknown",
    source: str = "unknown"
) -> List[Dict[str, Any]]:
    """
    Process extracted text blocks and return structured data.

    Each record contains:
      - clause_id   : unique UUID for this clause record (e.g. CLZ-XXXXXXXX)
      - clause      : classified clause type (e.g. "Confidentiality")
      - content_id  : unique UUID for the raw content block (e.g. CNT-XXXXXXXX)
      - content     : raw text of the clause block
      - page_number : page number where the clause starts
      - document    : document type (e.g. "NDA", "MSA", "SOW")
      - source      : who uploaded it — "client" or "legal"
    """
    structured_records = []

    for block in extracted_blocks:
        raw_text = block.get("raw_text", "")
        page_num = block.get("page_number")

        clause_id  = f"CLZ-{uuid.uuid4().hex[:8].upper()}"
        content_id = f"CNT-{uuid.uuid4().hex[:8].upper()}"
        clause_type = classify_clause(raw_text)

        record = {
            "clause_id":   clause_id,
            "clause":      clause_type,
            "content_id":  content_id,
            "content":     raw_text,
            "page_number": page_num,
            "document":    document,
            "source":      source,
        }

        structured_records.append(record)

    return structured_records
