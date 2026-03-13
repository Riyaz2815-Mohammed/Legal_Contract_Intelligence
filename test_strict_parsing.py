
from extracter.clause_engine import parse_text

sample_text = """
MEMORANDUM OF UNDERSTANDING
This MoU is entered into by and between:
Referrer: XYZ Corp
Solution Provider: ABC Solns
(Herein after referred as “Solution provider”)

WHEREAS:
1. The Referrer is a technology company specializing in platform development.
2. The Solution Provider desires to avail the professional referral services.

NOW THEREFORE, IT IS AGREED AS FOLLOWS:

1. Purpose
This agreement defines the relationship.

2. Term
This lasts for 5 years.

3. Referrer’s Responsibilities
The referrer shall:
- Send leads
- Update status

4. Solution Provider’s Responsibilities
The Solution provider agrees to:
a) Follow up with the Referred Leads...
b) Own and drive all commercial discussions...
c) Notify the Referrer of any successful sales...

5. Referral Fee
Pay 10 percent.
"""

if __name__ == "__main__":
    blocks = parse_text(sample_text)
    print(f"Total blocks extracted: {len(blocks)}")
    for i, b in enumerate(blocks, 1):
        print(f"{i}. {b['heading']}")
