# backend/risk/risk_engine.py

from core.configs import SIMILARITY_HIGH, SIMILARITY_MEDIUM
from typing import Optional


def tag_risk(similarity_score: Optional[float]) -> str:
    """
    Convert a cosine similarity score (0-1) into a risk label.

    Logic:
      ≥ SIMILARITY_HIGH  (default 0.90) → Low   (very close to the standard template)
      ≥ SIMILARITY_MEDIUM (default 0.75) → Medium
      < SIMILARITY_MEDIUM                → High  (deviates significantly)
      None (no standard in DB)           → High  (no comparison possible)
    """
    if similarity_score is None:
        return "High"
    if similarity_score >= SIMILARITY_HIGH:
        return "Low"
    if similarity_score >= SIMILARITY_MEDIUM:
        return "Medium"
    return "High"


def risk_color(risk: str) -> str:
    """Return a hex colour string for a risk label (used in metadata/logs)."""
    return {
        "Low":    "#10b981",   # green
        "Medium": "#f59e0b",   # amber
        "High":   "#ef4444",   # red
    }.get(risk, "#64748b")
