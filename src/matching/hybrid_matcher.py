"""
Hybrid Matcher — combines rule-based and semantic matching into a final score.

Scoring formula:
    Final Score = (Rule Score × WEIGHT_RULE)
               + (Semantic Score × WEIGHT_SEMANTIC)
               + (Experience Score × WEIGHT_EXPERIENCE)

If semantic matching is unavailable:
    - Weights are redistributed: rule and experience absorb semantic's weight
    - The candidate is NOT penalized (no zero score for missing semantics)
    - The report clearly indicates semantic matching was unavailable
"""

import logging
from typing import Dict

from src.config import WEIGHT_EXPERIENCE, WEIGHT_RULE, WEIGHT_SEMANTIC
from src.embeddings.embedding_model import EmbeddingModel
from src.matching.rule_matcher import rule_based_match
from src.matching.semantic_matcher import semantic_match
from src.models.job_description import JobDescription
from src.models.resume import Resume

logger = logging.getLogger(__name__)


def hybrid_match(resume: Resume, jd: JobDescription, embedding_model: EmbeddingModel) -> Dict:
    """
    Run the full hybrid matching pipeline.

    Args:
        resume: Parsed Resume object.
        jd: Parsed JobDescription object.
        embedding_model: EmbeddingModel instance (may or may not be available).

    Returns:
        Dictionary containing:
            - rule_result: Detailed rule-based matching results
            - semantic_result: Detailed semantic matching results
            - experience_result: Experience comparison
            - final_score: Weighted combined score
            - scoring_breakdown: How the final score was calculated
            - semantic_matching_available: Boolean flag
    """
    # ── Convert to lowercase before comparing ─────────────────────────────
    resume_skills = [s.strip().lower() for s in resume.skills if s.strip()]
    resume_projects = [p.strip().lower() for p in resume.projects if p.strip()]
    resume_responsibilities = [r.strip().lower() for r in resume.responsibilities if r.strip()]

    jd_required_skills = [s.strip().lower() for s in jd.required_skills if s.strip()]
    jd_preferred_skills = [s.strip().lower() for s in jd.preferred_skills if s.strip()]
    jd_responsibilities = [r.strip().lower() for r in jd.responsibilities if r.strip()]

    # ── Step 1: Rule-based matching ───────────────────────────────────────
    rule_result = rule_based_match(
        resume_skills=resume_skills,
        jd_required_skills=jd_required_skills,
        jd_preferred_skills=jd_preferred_skills,
        resume_experience=resume.experience,
        jd_minimum_experience=jd.minimum_experience,
    )

    # ── Step 2: Semantic matching ─────────────────────────────────────────
    semantic_result = semantic_match(
        embedding_model=embedding_model,
        resume_skills=resume_skills,
        resume_projects=resume_projects,
        resume_responsibilities=resume_responsibilities,
        jd_required_skills=jd_required_skills,
        jd_preferred_skills=jd_preferred_skills,
        jd_responsibilities=jd_responsibilities,
    )

    # ── Step 3: Calculate final score ─────────────────────────────────────
    rule_score = rule_result["rule_score"]
    exp_score = rule_result["experience"]["score"]
    semantic_available = semantic_result["semantic_matching_available"]
    semantic_score = semantic_result.get("overall_score")

    if semantic_available and semantic_score is not None:
        # Full hybrid scoring
        final_score = (
            rule_score * WEIGHT_RULE
            + semantic_score * WEIGHT_SEMANTIC
            + exp_score * WEIGHT_EXPERIENCE
        )
        scoring_breakdown = {
            "rule_score": rule_score,
            "rule_weight": WEIGHT_RULE,
            "rule_contribution": round(rule_score * WEIGHT_RULE, 1),
            "semantic_score": semantic_score,
            "semantic_weight": WEIGHT_SEMANTIC,
            "semantic_contribution": round(semantic_score * WEIGHT_SEMANTIC, 1),
            "experience_score": exp_score,
            "experience_weight": WEIGHT_EXPERIENCE,
            "experience_contribution": round(exp_score * WEIGHT_EXPERIENCE, 1),
        }
    else:
        # Fallback: redistribute semantic weight proportionally
        # so the candidate is not penalized
        fallback_rule_weight = WEIGHT_RULE / (WEIGHT_RULE + WEIGHT_EXPERIENCE)
        fallback_exp_weight = WEIGHT_EXPERIENCE / (WEIGHT_RULE + WEIGHT_EXPERIENCE)

        final_score = (
            rule_score * fallback_rule_weight
            + exp_score * fallback_exp_weight
        )
        scoring_breakdown = {
            "rule_score": rule_score,
            "rule_weight": round(fallback_rule_weight, 3),
            "rule_contribution": round(rule_score * fallback_rule_weight, 1),
            "semantic_score": None,
            "semantic_weight": 0,
            "semantic_contribution": 0,
            "experience_score": exp_score,
            "experience_weight": round(fallback_exp_weight, 3),
            "experience_contribution": round(exp_score * fallback_exp_weight, 1),
            "fallback_note": (
                "Semantic matching unavailable. Weights redistributed "
                "between rule-based and experience scores."
            ),
        }

    final_score = round(final_score, 1)

    logger.info(
        "Hybrid match complete — Final Score: %.1f%% (semantic=%s)",
        final_score,
        "active" if semantic_available else "unavailable",
    )

    return {
        "rule_result": rule_result,
        "semantic_result": semantic_result,
        "final_score": final_score,
        "scoring_breakdown": scoring_breakdown,
        "semantic_matching_available": semantic_available,
    }
