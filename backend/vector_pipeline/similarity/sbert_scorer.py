from sentence_transformers import SentenceTransformer, util
from config.settings import EMBEDDING_MODEL
import logging

logger = logging.getLogger(__name__)

# Load once — reuse across calls
_sbert_model = None

def get_sbert_model() -> SentenceTransformer:
    global _sbert_model
    if _sbert_model is None:
        _sbert_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"✅ SBERT model loaded: {EMBEDDING_MODEL}")
    return _sbert_model


def compute_similarity(query_text: str, content: str) -> float:
    model = get_sbert_model()
    query_emb = model.encode(query_text, convert_to_tensor=True)
    content_emb = model.encode(content, convert_to_tensor=True)
    score = util.cos_sim(query_emb, content_emb).item()
    return round(score, 4)