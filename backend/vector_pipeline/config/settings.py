import os
from dotenv import load_dotenv

# Load .env from the backend root directory
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=env_path)

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# LLM 
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").strip().lower()
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# Embedding
EMBEDDING_MODEL = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
EMBEDDING_DEVICE = "cpu"
EMBEDDING_NORMALIZE = True



# Pipeline
TOP_K = 5
SBERT_HIGH_RISK_THRESHOLD = 0.80
SBERT_MEDIUM_RISK_THRESHOLD = 0.90
# >= 0.90 is low risk