"""
Quick end-to-end test for SBERT similarity + ChromaDB clause retrieval.
Tests a realistic client clause against the legal standard in ChromaDB.
"""
import sys, logging
logging.basicConfig(level=logging.ERROR)

from vector_pipeline.embeddings.embed_store import get_embedding_model, load_vectorstore
from vector_pipeline.retrieval.query import query_vectorstore
from vector_pipeline.similarity.sbert_scorer import compute_similarity
from vector_pipeline.risk.risk_tagger import tag_risk

# --- Sample client clause from a real NDA ---
test_cases = [
    {
        "clause_type": "Termination",
        "document_type": "NDA",
        "text": "Either party may terminate this Agreement by providing fifteen (15) days written notice to the other party."
    },
    {
        "clause_type": "Confidentiality",
        "document_type": "NDA",
        "text": "Both parties agree to maintain confidentiality regarding any proprietary or confidential information shared under this Agreement."
    },
    {
        "clause_type": "Limitation of Liability",
        "document_type": "NDA",
        "text": "In no event shall either party be liable for any indirect, incidental, consequential, special, or punitive damages."
    },
]

print("\n" + "="*60)
print("SBERT + ChromaDB End-to-End Test")
print("="*60)

embedding_model = get_embedding_model()
vectorstore = load_vectorstore(embedding_model)

for tc in test_cases:
    print(f"\n📋 Clause Type: {tc['clause_type']}")
    print(f"   Client Text: {tc['text'][:80]}...")

    # ChromaDB retrieval
    results = query_vectorstore(vectorstore, tc["text"], document_type=tc["document_type"], k=1)

    if not results:
        print(f"   ❌ ChromaDB: NO MATCH FOUND")
        continue

    matched_doc, chroma_score = results[0]
    print(f"   ✅ ChromaDB Score: {round(chroma_score, 4)} (lower = more similar in L2)")
    print(f"   Matched Standard: {matched_doc.page_content[:80]}...")

    # SBERT Similarity
    sbert_score = compute_similarity(tc["text"], matched_doc.page_content)
    print(f"   ✅ SBERT Cosine Similarity: {sbert_score} (higher = more similar)")

    # Risk tagging
    risk = tag_risk(tc["text"], tc["clause_type"], sbert_score)
    print(f"   🏷️  Risk: {risk['risk']} | Reason: {risk.get('risk_reason','')[:60]}")

print("\n" + "="*60)
print("Test complete.")
