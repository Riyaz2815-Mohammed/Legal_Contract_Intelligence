"""
reembed_templates.py — Wipes ChromaDB and re-embeds all legal clauses from the DB.
Run this after uploading a new template or after changing the clause storage strategy.
"""
import sys
from pathlib import Path
sys.path.append(str(Path("e:/Yzone/LACCIS/backend")))

import shutil
from vector_pipeline.config.settings import CHROMA_PERSIST_DIR
from vector_pipeline.embeddings.embed_store import (
    get_embedding_model, fetch_legal_clauses, build_documents, embed_and_store
)

print("=== Re-embedding all legal templates ===\n")

# 1. Wipe existing ChromaDB to start fresh
chroma_path = Path(CHROMA_PERSIST_DIR)
if chroma_path.exists():
    shutil.rmtree(chroma_path)
    print(f"  Wiped old ChromaDB at {chroma_path}")
else:
    print(f"  No existing ChromaDB found at {chroma_path}")

# 2. Load embedding model
print("  Loading SBERT model...")
model = get_embedding_model()
print("  Model loaded.")

# 3. Fetch legal clauses from DB
print("  Fetching legal clauses from DB...")
df = fetch_legal_clauses()
if df.empty:
    print("  ERROR: No legal clauses found in DB. Upload a standard template first.")
    sys.exit(1)

print(f"  Found {len(df)} legal clause rows.")
print(f"  Clause types: {sorted(df['clause'].unique().tolist())}")

# 4. Build LangChain documents and embed
print("  Building embedding documents...")
docs = build_documents(df)

print(f"  Embedding {len(docs)} documents into ChromaDB...")
vectorstore = embed_and_store(docs, model)

count = vectorstore._collection.count()
print(f"\n✅ Done! ChromaDB now has {count} embedded clause chunks.")
print("   Restart the backend server to use the updated embeddings.")
