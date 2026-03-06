
import os
import sys

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from vector_pipeline.embeddings.embed_store import get_embedding_model
from vector_pipeline.retrieval.query import search_similar_clauses

if __name__ == "__main__":
    print("Testing Supabase pgvector Similarity Search...")
    try:
        embedding_model = get_embedding_model()
        query_text = "This agreement shall be governed by the laws of India."
        query_embedding = embedding_model.embed_query(query_text)
        
        results = search_similar_clauses(query_embedding, top_k=3, clause_type="Governing Law")
        
        print(f"\nResults for query: '{query_text}'")
        for i, res in enumerate(results):
            print(f"{i+1}. [{res['metadata']['clause']}] Score: {res['score']:.4f}")
            print(f"   Content: {res['page_content'][:100]}...")
            
    except Exception as e:
        print(f"Error during search test: {e}")
        sys.exit(1)
