import re
import uuid
import os
from typing import List, Dict, Optional, Any

# Attempt to load spaCy (optional — graceful fallback if missing)
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
except (OSError, ImportError):
    _nlp = None


# ──────────────────────────────────────────────────────────────────────────────
# Structural parsing helpers
# ──────────────────────────────────────────────────────────────────────────────

def extract_structural_id(text: str) -> Optional[str]:
    """
    Returns a match string if the line looks like a major new clause heading,
    otherwise None.  Sub-bullets (1.1, (a), (i)) are intentionally excluded so
    they remain grouped under their parent heading.
    """
    patterns = [
        r"^(Section\s+\d+)",               # Section 1
        r"^(Article\s+\d+)",               # Article 1
        r"^(\d+\.\s+[A-Z])",               # 1. Indemnification
        r"^([0-9]+\s+[A-Z][a-z]+)",        # 1 Indemnity
        r"^([IVXLCDM]+\.\s+[A-Z])",        # Roman  I. Title
        r"^([A-Z][A-Z\s]{3,})$",           # ALL CAPS HEADERS (≥ 4 chars)
        r"^(Clause\s+\d+)",                # Clause 1
    ]
    text_clean = text.strip()
    if len(text_clean) < 4:
        return None
    for pattern in patterns:
        m = re.match(pattern, text_clean)
        if m:
            return m.group(1)
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Clause classification
# ──────────────────────────────────────────────────────────────────────────────

# Ordered priority rules: each entry is (category, [regex patterns]).
# Patterns are matched against the FIRST 120 characters of lowercased text
# (heading + start of body), i.e. the "title zone".  A hit here yields a
# strong confidence boost so the ordering matters only for ties.
_TITLE_RULES: list[tuple[str, list[str]]] = [
    # ── Structural / meta ─────────────────────────────────────────────────────
    ("Header",  [
        r"non.?disclosure\s+agreement",
        r"mutual\s+non.?disclosure",
        r"this\s+agreement\s+(is\s+)?entered\s+into",
        r"entered\s+into\s+as\s+of",
        r"by\s+and\s+between",
        r"witnesseth",
        r"now,?\s+therefore",
        r"in\s+witness\s+whereof",
        r"preamble",
        r"recitals",
        r"parties\s+hereto",
        r"\bname:\s*m/s\b",
        r"\baddress:",
        r"sign\s+here",
        r"print\s+name",
        r"on\s+behalf\s+of",
        r"for\s+and\s+on\s+behalf",
    ]),
    # ── Operational clauses (check TERMINATION before TERM) ──────────────────
    ("Termination", [
        r"\btermination\b",
        r"effect\s+of\s+termination",
        r"consequences\s+of\s+termination",
        r"rights\s+upon\s+termination",
    ]),
    ("Term", [
        r"\bterm\s+of\s+(this\s+)?agreement\b",
        r"\bduration\s+of\b",
        r"\bcommencement\s+date\b",
        r"\binitial\s+term\b",
        r"\brenewal\s+term\b",
    ]),
    # ── Core commercial/legal clauses ─────────────────────────────────────────
    ("Confidentiality", [
        r"\bconfidentiality\b",
        r"non.?disclosure\b",
        r"confidential\s+information",
        r"proprietary\s+information",
    ]),
    ("Indemnity", [
        r"\bindemnif",
        r"\bindemnity\b",
        r"\bhold\s+harmless\b",
    ]),
    ("Limitation of Liability", [
        r"\blimitation\s+of\s+liability\b",
        r"\bliability\s+limit",
        r"\bcap\s+on\s+liability\b",
        r"\bmaximum\s+liability\b",
        r"\bin\s+no\s+event\s+shall",
    ]),
    ("Warranty", [
        r"\brepresentations?\s+and\s+warranties\b",
        r"\bwarranty\b",
        r"\bwarranties\b",
        r"\bwarrants\s+that\b",
        r"\bdisclaimer\s+of\s+warranties\b",
    ]),
    ("Intellectual Property Rights", [
        r"\bintellectual\s+property\b",
        r"\bip\s+rights\b",
        r"\bproprietary\s+rights\b",
        r"\bownership\s+of\s+(work|ip|intellectual)\b",
        r"\bcopyright\b",
    ]),
    ("Data Protection and Security", [
        r"\bdata\s+protection\b",
        r"\bdata\s+security\b",
        r"\bgdpr\b",
        r"\bprivacy\s+policy\b",
        r"\bpersonal\s+data\b",
    ]),
    ("Governing Law", [
        r"\bgoverning\s+law\b",
        r"\bapplicable\s+law\b",
        r"\bdispute\s+resolution\b",
        r"\bjurisdiction\b",
        r"\barbitration\b",
    ]),
    ("Force Majeure", [
        r"\bforce\s+majeure\b",
        r"\bact\s+of\s+god\b",
        r"\bbeyond\s+(the\s+)?reasonable\s+control\b",
    ]),
    ("Assignment", [
        r"\bassignment\b",
        r"\bassign\s+this\s+agreement\b",
        r"\btransfer\s+of\s+(rights|obligations)\b",
    ]),
    ("Entire Agreement", [
        r"\bentire\s+agreement\b",
        r"\bintegration\s+clause\b",
        r"\bsupersedes\s+all\s+prior\b",
        r"\bmerger\s+clause\b",
    ]),
    ("Severability", [
        r"\bseverability\b",
        r"\bif\s+any\s+provision.*invalid\b",
        r"\binvalid.*provision.*severed\b",
    ]),
    ("Notices", [
        r"\bnotices\b",
        r"\bwritten\s+notice\b",
        r"\bnotifications?\s+to\s+(the\s+)?parties\b",
    ]),
    ("Payment Terms", [
        r"\bpayment\s+terms\b",
        r"\bfees\s+and\s+payment\b",
        r"\bcompensation\b",
        r"\binvoic",
    ]),
    ("Deliverables", [
        r"\bdeliverables\b",
        r"\bwork\s+product\b",
        r"\bmilestones?\b",
        r"\bacceptance\s+criteria\b",
    ]),
    ("Service Levels (SLA)", [
        r"\bservice\s+level",
        r"\bsla\b",
        r"\buptime\b",
        r"\bdowntime\b",
    ]),
    ("Relationship", [
        r"\bindependent\s+contractor\b",
        r"\brelationship\s+of\s+(the\s+)?parties\b",
        r"\bnot\s+(an?\s+)?employee\b",
    ]),
    ("Purpose", [
        r"\bpurpose\s+of\s+(this\s+)?agreement\b",
        r"\bscope\s+of\s+(services|work)\b",
        r"\bengagement\s+description\b",
    ]),
    ("Audit Rights", [
        r"\baudit\s+rights?\b",
        r"\bright\s+to\s+audit\b",
        r"\brecord\s+keeping\b",
    ]),
    ("Non-Solicitation", [
        r"\bnon.?solicitation\b",
        r"\bsolicitation\s+of\s+employees\b",
        r"\bnot\s+to\s+solicit\b",
    ]),
    ("Non-Compete", [
        r"\bnon.?compete\b",
        r"\bnon.?competition\b",
        r"\brestrictive\s+covenant\b",
    ]),
    ("Dispute Resolution", [
        r"\bdispute\s+resolution\b",
        r"\bmediation\b",
        r"\bexpert\s+determination\b",
    ]),
]

# Full-body keyword scoring (used when title zone has no decisive match)
# Format: category -> [(keyword, weight)]
_BODY_RULES: dict[str, list[tuple[str, int]]] = {
    "Confidentiality":            [("confidential", 2), ("non-disclosure", 3), ("proprietary information", 3), ("trade secret", 3), ("secrecy", 2)],
    "Indemnity":                  [("indemnify", 3), ("hold harmless", 3), ("defend", 2), ("indemnification", 3), ("losses and damages", 2)],
    "Limitation of Liability":    [("limitation of liability", 4), ("consequential damages", 3), ("indirect damages", 3), ("maximum liability", 3), ("in no event shall", 3), ("cap on liability", 4)],
    "Warranty":                   [("warrant", 2), ("warranty", 2), ("warranties", 2), ("merchantability", 3), ("fitness for a particular purpose", 3), ("as-is", 2), ("disclaimer", 2)],
    "Termination":                [("terminate this agreement", 3), ("written notice to terminate", 3), ("survival upon termination", 3), ("effect of termination", 4), ("termination for cause", 4), ("termination for convenience", 4)],
    "Term":                       [("initial term", 3), ("term of this agreement", 4), ("in force for a period", 3), ("automatically renew", 3), ("commencement date", 2), ("effective date", 1)],
    "Governing Law":              [("governed by the laws", 3), ("jurisdiction of", 2), ("courts of", 2), ("arbitration clause", 3), ("dispute resolution", 2)],
    "Intellectual Property Rights": [("intellectual property", 3), ("ip rights", 3), ("copyright", 2), ("trademark", 2), ("patent", 2), ("license grant", 3), ("moral rights", 2)],
    "Data Protection and Security": [("personal data", 3), ("data protection", 3), ("gdpr", 4), ("privacy", 2), ("data breach", 3), ("security measures", 2)],
    "Force Majeure":              [("force majeure", 4), ("act of god", 3), ("pandemic", 2), ("beyond reasonable control", 3), ("unforeseeable", 2)],
    "Assignment":                 [("assignment", 2), ("assign this agreement", 3), ("successors and assigns", 3), ("transfer of rights", 3)],
    "Entire Agreement":           [("entire agreement", 4), ("supersedes", 3), ("prior agreements", 3), ("merger clause", 4)],
    "Severability":               [("severability", 4), ("if any provision", 2), ("invalid or unenforceable", 3), ("severed", 2)],
    "Notices":                    [("notice shall be", 3), ("written notice", 2), ("notice to the other party", 3)],
    "Payment Terms":              [("payment", 2), ("invoice", 2), ("fees", 1), ("billing", 2), ("taxes", 1), ("compensation", 2)],
    "Deliverables":               [("deliverables", 3), ("work product", 3), ("milestone", 2), ("acceptance criteria", 3)],
    "Service Levels (SLA)":       [("service level", 3), ("uptime", 3), ("downtime", 3), ("credit", 1), ("maintenance", 1)],
    "Relationship":               [("independent contractor", 4), ("not an employee", 3), ("employer-employee", 3)],
    "Non-Solicitation":           [("non-solicitation", 4), ("not to solicit", 3), ("solicitation of employees", 4)],
    "Non-Compete":                [("non-compete", 4), ("non-competition", 4), ("restrictive covenant", 3)],
    "Dispute Resolution":         [("dispute resolution", 3), ("mediation", 3), ("expert determination", 3)],
    "Audit Rights":               [("audit rights", 4), ("right to audit", 4), ("record keeping", 2), ("inspection rights", 3)],
    "Purpose":                    [("purpose of this agreement", 4), ("scope of services", 3), ("engagement description", 3)],
}


def classify_clause(text: str) -> str:
    """
    Classify a clause block into a standardised type.

    Strategy (priority order):
    1. Explicit header-pattern match in the first 120 chars of the text.
    2. Weighted title-zone hits using _TITLE_RULES.
    3. Full-body keyword scoring using _BODY_RULES.
    4. Falls back to "Other".
    """
    text_clean = text.strip()
    text_lower = text_clean.lower()
    title_zone = text_lower[:120]   # heading + first line of body

    # ── Pass 0: hard-wired preamble / header starts ───────────────────────────
    for pat in [
        r"^preamble", r"^non.disclosure agreement", r"^non\u2013disclosure",
        r"^this non.?disclosure agreement", r"^this agreement is entered",
    ]:
        if re.search(pat, text_lower):
            return "Header"

    # Count strong header signals in the title zone
    header_hits = sum(
        1 for pat in _TITLE_RULES[0][1]    # index 0 == Header
        if re.search(pat, title_zone)
    )
    if header_hits >= 2:
        return "Header"

    # ── Pass 1: title-zone scan (ordered, first decisive match wins) ──────────
    title_scores: dict[str, int] = {}
    for category, patterns in _TITLE_RULES:
        if category == "Header":
            continue  # already handled
        for pat in patterns:
            if re.search(pat, title_zone):
                title_scores[category] = title_scores.get(category, 0) + 3

    if title_scores:
        best = max(title_scores, key=title_scores.__getitem__)
        if title_scores[best] >= 3:          # at least one title-zone hit
            return best

    # ── Pass 2: full-body weighted keyword scoring ────────────────────────────
    body_scores: dict[str, int] = {}
    for category, kwds in _BODY_RULES.items():
        score = sum(w for kw, w in kwds if kw in text_lower)
        if score > 0:
            body_scores[category] = score

    if body_scores:
        best = max(body_scores, key=body_scores.__getitem__)
        if body_scores[best] >= 2:           # require at least moderate confidence
            return best

    # ── Pass 3: spaCy lemma fallback (cheap, if model loaded) ────────────────
    if _nlp:
        try:
            doc = _nlp(text_lower[:600])     # limit for speed
            lemmas = " ".join(t.lemma_ for t in doc)
            lemma_scores: dict[str, int] = {}
            for category, kwds in _BODY_RULES.items():
                s = sum(w for kw, w in kwds if kw in lemmas)
                if s > 0:
                    lemma_scores[category] = s
            if lemma_scores:
                best = max(lemma_scores, key=lemma_scores.__getitem__)
                if lemma_scores[best] >= 2:
                    return best
        except Exception:
            pass

    return "Other"


# ──────────────────────────────────────────────────────────────────────────────
# Text parsing
# ──────────────────────────────────────────────────────────────────────────────

def _split_inline_clauses(text: str) -> str:
    """
    Pre-process raw extracted text to handle dense paragraph NDAs where clause
    headings are inline with body text, e.g.:
        '2. Confidentiality: Both parties agree to maintain...'
    Splits these into two lines:
        '2. Confidentiality'
        'Both parties agree to maintain...'
    This allows parse_text() to detect the heading normally.
    """
    # Pattern: line starts with N. Word(s): rest-of-text
    # We only split if the heading portion is short (< 80 chars before the colon)
    # so we don't accidentally split sentences that happen to start with a number.
    inline_pattern = re.compile(
        r'^(\d+\.\s+[A-Za-z][A-Za-z\s/\-]{0,70}):(\s+.+)$'
    )
    lines_out = []
    for line in text.splitlines():
        m = inline_pattern.match(line.strip())
        if m:
            heading_part = m.group(1).strip()
            body_part    = m.group(2).strip()
            lines_out.append(heading_part)   # heading on its own line
            if body_part:
                lines_out.append(body_part)  # body on next line
        else:
            lines_out.append(line)
    return "\n".join(lines_out)


def parse_text(text: str) -> List[Dict[str, Any]]:
    """
    Parse raw document text into structured blocks.
    Supports both:
    - Documents with explicit standalone headings  ('3. Termination\\n<body>')
    - Dense paragraph PDFs with inline headings    ('3. Termination: <body>')

    Each major heading detected by extract_structural_id() starts a new block.
    """
    # Pre-process: split inline numbered headings into separate lines
    text = _split_inline_clauses(text)

    extracted_blocks = []
    current_page = 1
    current_heading = "Preamble"
    current_content_lines: list[str] = []
    current_block_start_page = 1

    for line in text.splitlines():
        line_stripped = line.strip()

        # Track page markers
        page_match = re.match(r"^PAGE\s+(\d+)", line_stripped, re.IGNORECASE)
        if page_match:
            current_page = int(page_match.group(1))
            continue

        # Skip separator lines & blank lines
        if re.match(r"^-+$", line_stripped) or not line_stripped:
            continue

        match = extract_structural_id(line_stripped)
        if match is not None:
            # Flush previous block
            full_content = "\n".join(current_content_lines).strip()
            if len(full_content) > 10 or current_heading != "Preamble":
                extracted_blocks.append({
                    "page_number": current_block_start_page,
                    "heading":     current_heading,
                    "content":     full_content,
                })
            current_heading = line_stripped
            current_content_lines = []
            current_block_start_page = current_page
        else:
            current_content_lines.append(line_stripped)

    # Flush last block
    full_content = "\n".join(current_content_lines).strip()
    if len(full_content) > 10 or current_heading != "Preamble":
        extracted_blocks.append({
            "page_number": current_block_start_page,
            "heading":     current_heading,
            "content":     full_content,
        })

    return extracted_blocks



def parse_text_file(file_path: str) -> List[Dict[str, Any]]:
    """Backwards-compatibility wrapper: parse a file path."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return parse_text(f.read())


# ──────────────────────────────────────────────────────────────────────────────
# Document processing
# ──────────────────────────────────────────────────────────────────────────────

def process_document(
    extracted_blocks: List[Dict[str, Any]],
    document: str = "Unknown",
    source: str = "unknown",
) -> List[Dict[str, Any]]:
    """
    Classify each extracted text block and return structured records.
    The 'content' field preserves the literal heading + body exactly as parsed.
    """
    structured_records = []

    for block in extracted_blocks:
        heading  = block.get("heading", "Clause").strip()
        body     = block.get("content", "").strip()
        page_num = block.get("page_number", 1)

        full_text_for_class = f"{heading}\n{body}".strip()
        clause_type = classify_clause(full_text_for_class)

        # Truncate runaway headings
        if len(heading) > 150:
            heading = heading[:150] + "…"

        structured_records.append({
            "clause_id":   f"CLZ-{uuid.uuid4().hex[:8].upper()}",
            "clause":      clause_type,
            "content_id":  f"CNT-{uuid.uuid4().hex[:8].upper()}",
            "content":     full_text_for_class,
            "page_number": page_num,
            "document":    document,
            "source":      source,
        })

    return structured_records

