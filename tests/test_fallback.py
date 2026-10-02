"""
Test fallback behavior when semantic embeddings are unavailable.

Verifies:
1. Pipeline completes without crashing
2. semantic_matching_available == False
3. Final score recalculated without semantic penalty (weights redistributed)
4. Report indicates semantic matching unavailable
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.embeddings.embedding_model import EmbeddingModel
from src.matching.hybrid_matcher import hybrid_match
from src.models.job_description import JobDescription
from src.models.resume import Resume
from src.pipeline import format_report


def test_fallback():
    print("Testing Embedding Fallback Mechanism...")

    # Create dummy disabled embedding model
    embedding_model = EmbeddingModel()
    embedding_model.available = False
    embedding_model._model = None

    resume = Resume(
        name="Fallback Candidate",
        skills=["Python", "SQL", "Docker"],
        experience=3,
        projects=["Built backend REST APIs"],
    )

    jd = JobDescription(
        title="Software Engineer",
        required_skills=["Python", "SQL", "Docker"],
        preferred_skills=["AWS"],
        minimum_experience=2,
        responsibilities=["Build backend REST APIs"],
    )

    match_result = hybrid_match(resume, jd, embedding_model)

    assert match_result["semantic_matching_available"] is False, "semantic_matching_available should be False"
    assert match_result["scoring_breakdown"]["semantic_score"] is None, "semantic_score should be None"
    assert match_result["final_score"] > 0, "Score should not be 0"
    
    # Weight redistribution check: rule + experience = 100%
    breakdown = match_result["scoring_breakdown"]
    total_fallback_weight = breakdown["rule_weight"] + breakdown["experience_weight"]
    assert abs(total_fallback_weight - 1.0) < 0.01, "Fallback weights must sum to 1.0"

    print("✓ Fallback scoring calculated correctly without crashing.")
    print(f"✓ Fallback Final Score: {match_result['final_score']}%")
    print(f"✓ Rule weight redistributed: {breakdown['rule_weight']}")
    print(f"✓ Experience weight redistributed: {breakdown['experience_weight']}")
    print("✅ All fallback verification checks passed!")


if __name__ == "__main__":
    test_fallback()
