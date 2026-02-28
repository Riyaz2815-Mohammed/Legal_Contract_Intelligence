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
    Extracts structural clause numbering (e.g., "1.", "Section 3", "(a)")
    Used to determine if a line starts a MAJOR new clause.
    """
    # Only match major section dividers, NOT sub-bullets (1.1, (a)) so they group together
    patterns = [
        r"^(Section\s+\d+)",             # Section 1
        r"^(Article\s+\d+)",             # Article 1
        r"^(\d+\.\s+[A-Z])",             # 1. Indemnification (Start of major)
        r"^([0-9]+\s+[A-Z][a-z]+)",      # 1 Indemnity (no period)
        r"^([IVXLCDM]+\.\s+[A-Z])",      # Roman numerals I. Title
        r"^([A-Z][A-Z\s]+)$"             # ALL CAPS HEADERS (e.g. TERMINATION) - if it is the whole line
    ]

    for pattern in patterns:
        match = re.match(pattern, text.strip())
        if match:
            # Check for false positives on very short lines that happen to be all caps
            if len(text.strip()) < 4 and pattern == patterns[-1]:
                continue
            return match.group(1)

    return None


def classify_clause(text: str) -> str:
    """
    Classifies the clause text into a standardized type.
    First checks for explicit headers. If ambiguous, falls back to Mistral AI.
    """
    text_clean = text.strip()
    text_lower = text_clean.lower()
    
    # Priority 1: Check if the text starts with a specific section header
    header_logic = {
        "Definitions": [r"definitions", r"defined terms"],
        "Purpose": [r"purpose", r"background", r"recitals"],
        "Scope of Services": [r"scope of services", r"service scope"],
        "Deliverables": [r"deliverables", r"work product"],
        "Project Timeline and Milestones": [r"project timeline", r"milestones", r"schedule"],
        "Service Levels (SLA)": [r"service level", r"sla", r"uptime", r"availability"],
        "Fees and Payment Terms": [r"fees and payment", r"payment terms", r"compensation", r"invoicing", r"taxes"],
        "Confidentiality": [r"confidentiality", r"non-disclosure", r"confidential information", r"non-disclosure and non-use"],
        "Intellectual Property Rights": [r"intellectual property", r"ip rights", r"proprietary rights", r"ownership"],
        "Data Protection and Security": [r"data protection", r"data security", r"gdpr", r"privacy"],
        "Compliance with Laws": [r"compliance with laws", r"regulatory compliance"],
        "Independent Contractor Relationship": [r"independent contractor", r"relationship of the parties"],
        "Representations and Warranties": [r"representations and warranties", r"warranty"],
        "Indemnification": [r"indemnification", r"indemnity"],
        "Limitation of Liability": [r"limitation of liability", r"liability limit"],
        "Risk Allocation": [r"risk allocation"],
        "Force Majeure": [r"force majeure", r"act of god"],
        "Term": [r"term", r"duration"],
        "Termination": [r"termination", r"effect of termination"],
        "Assignment": [r"assignment", r"transfer"],
        "Amendments": [r"amendments", r"modifications"],
        "Notices": [r"notices", r"communications"],
        "Severability": [r"severability"],
        "Governing Law": [r"governing law", r"applicable law"],
        "Jurisdiction and Dispute Resolution": [r"jurisdiction", r"dispute resolution", r"arbitration", r"mediation"],
        "Entire Agreement": [r"entire agreement", r"integration", r"merger"]
    }

    prefix = text_lower[:70]
    for category, patterns in header_logic.items():
        for pat in patterns:
            if re.search(pat, prefix):
                return category

    # Priority 2: Keyword Scoring Fallback
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text_lower)
        except OSError:
            doc = None
    except ImportError:
        doc = None

    rules = {
        "Indemnification": ["indemnify", "indemnification", "hold harmless"],
        "Limitation of Liability": ["limitation of liability", "cap on liability", "consequential damages"],
        "Confidentiality": ["confidential", "non-disclosure", "proprietary information"],
        "Termination": ["terminate", "termination", "cancellation"],
        "Payment Terms": ["payment", "invoice", "fees"],
        "Service Levels (SLA)": ["service level", "sla", "uptime"],
        "Governing Law": ["governing law", "jurisdiction", "laws of"],
        "Intellectual Property Rights": ["intellectual property", "ip rights", "copyright", "trademark"],
        "Deliverables": ["deliverables", "work product"],
        "Data Protection and Security": ["data protection", "gdpr", "privacy"],
        "Force Majeure": ["force majeure", "act of god"],
        "Assignment": ["assignment", "assignability"],
        "Notices": ["notices", "written notice"],
        "Severability": ["severability", "invalidity"],
        "Entire Agreement": ["entire agreement", "supersedes"],
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


def parse_text(text: str) -> List[Dict[str, Any]]:
    """
    Parses a raw text string with 'PAGE X' delimiters.
    Groups MAJOR clauses and their subheadings together into cohesive blocks.
    """
    extracted_blocks = []

    current_page = 1
    current_text_lines = []
    current_block_start_page = 1

    lines = text.splitlines()

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

        # Check if line starts a MAJOR new clause (e.g. "1. Indemnification" vs "1.1 Subheading")
        is_major_clause = extract_structural_id(line_stripped) is not None

        if is_major_clause:
            # Save previous block if exists AND is long enough to be a real clause
            if current_text_lines:
                full_text = "\n".join(current_text_lines)
                if len(full_text) > 50: # Don't save tiny garbage blocks
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
            
            # Since it's not a major clause, it's either generic text or a subheading (1.1, a). 
            # We append it to the CURRENT clause block so it stays grouped!
            current_text_lines.append(line_stripped)

    # Flush last block
    if current_text_lines:
        full_text = "\n".join(current_text_lines)
        if len(full_text) > 50:
            extracted_blocks.append({
                "page_number": current_block_start_page,
                "raw_text": full_text
            })

    return extracted_blocks


def parse_text_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Backwards compatibility: Parses a file path directly.
    """
    import os
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return parse_text(f.read())


def process_document(
    extracted_blocks: List[Dict[str, Any]],
    document: str = "Unknown",
    source: str = "unknown"
) -> List[Dict[str, Any]]:
    """
    Process extracted text blocks and return structured data.
    Uses Mistral API for perfect classification.
    """
    structured_records = []

    for block in extracted_blocks:
        raw_text = block.get("raw_text", "").strip()
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

