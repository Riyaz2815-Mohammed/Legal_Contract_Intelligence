import os
from dotenv import load_dotenv

# Load .env from the backend root directory
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=env_path)

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Mistral
MISTRAL_API_KEY = os.getenv("MISTRAL_API")
MISTRAL_MODEL = "mistral-large-latest"
MISTRAL_TEMPERATURE = 0.2

# Embedding
EMBEDDING_MODEL = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
EMBEDDING_DEVICE = "cpu"
EMBEDDING_NORMALIZE = True

# ChromaDB
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_legal_db")
CHROMA_COLLECTION = "legal_clauses"

# Pipeline
TOP_K = 5
SBERT_HIGH_RISK_THRESHOLD = 0.60
SBERT_MEDIUM_RISK_THRESHOLD = 0.75
SBERT_LOW_RISK_THRESHOLD = 0.90