import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Mistral
MISTRAL_API_KEY = os.getenv("MISTRAL_API")
MISTRAL_MODEL = "mistral-large-latest"
MISTRAL_TEMPERATURE = 0.2

# Embedding
EMBEDDING_MODEL = os.getenv("MODEL_NAME")
EMBEDDING_DEVICE = "cpu"
EMBEDDING_NORMALIZE = True

# ChromaDB
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_legal_db")
CHROMA_COLLECTION = "legal_clauses"

# Pipeline
TOP_K = 5
SBERT_HIGH_RISK_THRESHOLD = 0.60
SBERT_MEDIUM_RISK_THRESHOLD = 0.75
SBERT_LOW_RISK_THRESHOLD = 0.90