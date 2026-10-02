"""
Centralized configuration for TalentLens-AI V2.

All configurable values are loaded from environment variables (.env file).
This ensures no magic strings are scattered throughout the codebase.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ── API Keys ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── LLM Configuration ────────────────────────────────────────────────────────
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

# ── Embedding Configuration ──────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# ── Scoring Weights (must sum to 1.0) ────────────────────────────────────────
WEIGHT_RULE = float(os.getenv("WEIGHT_RULE", "0.40"))
WEIGHT_SEMANTIC = float(os.getenv("WEIGHT_SEMANTIC", "0.35"))
WEIGHT_EXPERIENCE = float(os.getenv("WEIGHT_EXPERIENCE", "0.25"))


def validate_config():
    """Validate that critical configuration values are present."""
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Please add it to your .env file."
        )

    total_weight = WEIGHT_RULE + WEIGHT_SEMANTIC + WEIGHT_EXPERIENCE
    if abs(total_weight - 1.0) > 0.01:
        raise ValueError(
            f"Scoring weights must sum to 1.0, got {total_weight:.2f} "
            f"(rule={WEIGHT_RULE}, semantic={WEIGHT_SEMANTIC}, experience={WEIGHT_EXPERIENCE})"
        )
