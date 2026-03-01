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
    # Exclude sub-bullets like 1.1 or (a) so they stay grouped under their major header
    patterns = [
        r"^(Section\s+\d+)",             # Section 1
        r"^(Article\s+\d+)",             # Article 1
        r"^(\d+\.\s+[A-Z])",             # 1. Indemnification (Start of major)
        r"^([0-9]+\s+[A-Z][a-z]+)",      # 1 Indemnity (no period)
        r"^([IVXLCDM]+\.\s+[A-Z])",      # Roman numerals I. Title
        r"^([A-Z][A-Z\s]+)$",            # ALL CAPS HEADERS (e.g. TERMINATION) - if it is the whole line
        r"^(Clause\s+\d+)"               # Clause 1
    ]

    text_clean = text.strip()
    
    # Very short single words are usually OCR noise or signatures, ignore them
    if len(text_clean) < 4:
        return None

    for pattern in patterns:
        match = re.match(pattern, text_clean)
        if match:
            return match.group(1)

    return None


def classify_clause(text: str) -> str:
    """
    Classifies the clause text into a standardized type.
    First checks for explicit headers. If ambiguous, falls back to SpaCy Keyword Matching.
    """
    text_clean = text.strip()
    text_lower = text_clean.lower()
    
    # Priority 1: Check if the text starts with a specific section header
    header_logic = {
        "Purpose": [r"purpose", r"background", r"recitals", r"engagement"],
        "Deliverables": [r"deliverables", r"work product", r"milestones", r"schedule"],
        "Service Levels (SLA)": [r"service level", r"sla", r"uptime", r"availability"],
        "Payment Terms": [r"fees", r"payment terms", r"compensation", r"invoicing", r"taxes"],
        "Confidentiality": [r"confidentiality", r"non-disclosure", r"confidential information"],
        "Intellectual Property Rights": [r"intellectual property", r"ip rights", r"proprietary rights", r"ownership"],
        "Data Protection and Security": [r"data protection", r"data security", r"gdpr", r"privacy", r"personal data"],
        "Relationship": [r"independent contractor", r"relationship of the parties", r"employment"],
        "Warranty": [r"representations and warranties", r"warranty"],
        "Indemnity": [r"indemnification", r"indemnity"],
        "Limitation of Liability": [r"limitation of liability", r"liability limit"],
        "Force Majeure": [r"force majeure", r"act of god"],
        "Term": [r"term", r"duration", r"commencement"],
        "Termination": [r"termination", r"effect of termination"],
        "Assignment": [r"assignment", r"transfer"],
        "Notices": [r"notices", r"communications"],
        "Severability": [r"severability"],
        "Governing Law": [r"governing law", r"applicable law", r"dispute resolution", r"jurisdiction", r"arbitration"],
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
        "Confidentiality": ["confidential", "non-disclosure", "secrecy", "proprietary information", "trade secret"],
        "Indemnity": ["indemnify", "indemnification", "hold harmless", "defend", "liable"],
        "Limitation of Liability": ["limitation of liability", "cap on liability", "consequential damages", "indirect damages", "maximum liability"],
        "Warranty": ["warrant", "warranty", "representation", "merchantability", "fitness for a particular purpose", "as is"],
        "Termination": ["terminate", "termination", "cancellation", "expiration", "survival", "breach"],
        "Payment Terms": ["payment", "invoice", "fees", "taxes", "billing", "compensation"],
        "Service Levels (SLA)": ["service level", "sla", "uptime", "downtime", "credit", "support", "maintenance"],
        "Governing Law": ["governing law", "jurisdiction", "venue", "dispute resolution", "arbitration", "courts"],
        "Intellectual Property Rights": ["intellectual property", "ip rights", "copyright", "trademark", "patent", "license", "ownership", "moral rights"],
        "Deliverables": ["deliverables", "work product", "milestone", "acceptance criteria"],
        "Data Protection and Security": ["data protection", "gdpr", "privacy", "security", "personal data", "ccpa"],
        "Force Majeure": ["force majeure", "act of god", "pandemic", "unforeseeable", "beyond reasonable control"],
        "Assignment": ["assignment", "assign", "transfer", "successors"],
        "Notices": ["notices", "written notice", "communication"],
        "Severability": ["severability", "invalidity", "enforceability"],
        "Entire Agreement": ["entire agreement", "supersedes", "integration", "prior agreements"],
        "Term": ["term", "duration", "commencement", "effective date", "renewal"],
        "Purpose": ["purpose", "engagement", "scope", "services"],
        "Relationship": ["independent contractor", "relationship of the parties", "employment", "agency", "partnership"]
    }

    scores = {category: 0 for category in rules}
    tokens = [token.lemma_ for token in doc] if doc else text_lower.split()
    token_text = " ".join(tokens)

    for category, keywords in rules.items():
        for keyword in keywords:
            # Check for exact keyword match or if it's a substring
            if keyword in token_text or keyword in text_lower:
                scores[category] += 1
                
    # Boost title matches
    for category, keywords in rules.items():
        for keyword in keywords:
            if keyword in text_lower[:50]: # Title/Start of string
                 scores[category] += 2

    best_match = max(scores, key=scores.get)
    if scores[best_match] > 0:
        return best_match

    return "Other"


def parse_text(text: str) -> List[Dict[str, Any]]:
    """
    Parses a raw text string. Identifies literal headings and groups the text 
    underneath them into cohesive blocks.
    """
    extracted_blocks = []
    current_page = 1
    current_heading = "Preamble"
    current_content_lines = []
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

        # Check if line starts a MAJOR new clause
        match = extract_structural_id(line_stripped)

        if match is not None:
            # Save the previous block
            full_content = "\n".join(current_content_lines).strip()
            if full_content or current_heading != "Preamble":
                if len(full_content) > 10 or current_heading != "Preamble":
                    extracted_blocks.append({
                        "page_number": current_block_start_page,
                        "heading": current_heading,
                        "content": full_content
                    })

            # Start new block with the exact literal heading
            current_heading = line_stripped 
            current_content_lines = []
            current_block_start_page = current_page
        else:
            # Just another line of text - append to current block
            current_content_lines.append(line_stripped)

    # Flush last block
    full_content = "\n".join(current_content_lines).strip()
    if full_content or current_heading != "Preamble":
        if len(full_content) > 10 or current_heading != "Preamble":
            extracted_blocks.append({
                "page_number": current_block_start_page,
                "heading": current_heading,
                "content": full_content
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
    Uses AI/regex to classify the clause, but saves the literal heading + body 
    precisely as the 'content' field in the DB.
    """
    structured_records = []

    for block in extracted_blocks:
        heading = block.get("heading", "Clause").strip()
        body = block.get("content", "").strip()
        page_num = block.get("page_number", 1)

        # Full context string used for classification
        full_text_for_class = f"{heading}\n{body}".strip()
        
        # Determine the standardized category (e.g. 'Payment Terms')
        clause_type = classify_clause(full_text_for_class)

        # Truncate heading just in case it's huge
        if len(heading) > 150:
            heading = heading[:150] + "..."

        clause_id  = f"CLZ-{uuid.uuid4().hex[:8].upper()}"
        content_id = f"CNT-{uuid.uuid4().hex[:8].upper()}"

        record = {
            "clause_id":   clause_id,
            "clause":      clause_type,
            "content_id":  content_id,
            "content":     full_text_for_class, # Stores Heading + Body precisely without splitting
            "page_number": page_num,
            "document":    document,
            "source":      source,
        }

        structured_records.append(record)

    return structured_records

