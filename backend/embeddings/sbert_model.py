# backend/embedding/sbert_model.py

from sentence_transformers import SentenceTransformer

from core.configs import MODEL_NAME

_model_instance = None


def load_model():
    """
    Load SBERT model only once.
    """
    global _model_instance

    if _model_instance is None:
        _model_instance = SentenceTransformer(MODEL_NAME)

    return _model_instance


def get_model():
    """
    Return loaded model instance.
    """
    global _model_instance

    if _model_instance is None:
        _model_instance = load_model()

    return _model_instance