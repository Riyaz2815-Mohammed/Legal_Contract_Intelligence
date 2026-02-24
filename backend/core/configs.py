import os

MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")

SIMILARITY_HIGH = float(os.getenv("SIMILARITY_HIGH", 0.90))
SIMILARITY_MEDIUM = float(os.getenv("SIMILARITY_MEDIUM", 0.75))

CHROMA_PATH = os.getenv("CHROMA_PATH", "./vector_store")