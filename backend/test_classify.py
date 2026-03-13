import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from extracter.clause_engine import classify_clause

tests = [
    "Referrer's Responsibilities: The referrer shall find new clients.",
    "Company obligations include payment.",
    "Commission will be paid as a referral fee.",
    "Mutual notice must be given.",
    "Visibility and reporting rights are given to the client.",
    "Non-circumvention is crucial.",
    "This is an exclusive agreement.",
    "Amendments must be in writing.",
    "Governing Law: This agreement is governed by the laws of Texas."
]

for t in tests:
    print(f"'{t}' -> {classify_clause(t)}")
