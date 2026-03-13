try:
    print("Testing sentence-transformers import...")
    from sentence_transformers import SentenceTransformer
    print("Success: sentence-transformers imported")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
