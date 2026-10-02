"""
Rule-Based Matcher — exact/normalized skill matching and experience comparison.

Refactored from V1's matcher.py and normalize.py.
Core logic preserved, enhanced with:
- Required vs preferred skill distinction
- Normalization via alias mapping (from V1 normalize.py)
- Cleaner return structures for the hybrid matcher
"""

import logging
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


# ── Skill Normalization (from V1 normalize.py) ────────────────────────────────

SKILL_ALIASES = {
    "py": "python",
    "python3": "python",
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "cpp": "c++",
    "c plus plus": "c++",
    "js": "javascript",
    "node": "node.js",
    "nodejs": "node.js",
    "tf": "tensorflow",
    "k8s": "kubernetes",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "react.js": "react",
    "reactjs": "react",
    "vue.js": "vue",
    "vuejs": "vue",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "fastapi": "fastapi",
    "flask": "flask",
    "django": "django",
}


def normalize_skill(skill: str) -> str:
    """Normalize a single skill string to its canonical form."""
    skill = skill.strip().lower()
    return SKILL_ALIASES.get(skill, skill)


def normalize_skills(skills: List[str]) -> Set[str]:
    """Normalize a list of skills and return as a set of unique values."""
    return {normalize_skill(s) for s in skills}


# ── Skill Matching (from V1 matcher.py) ───────────────────────────────────────

def match_skills(
    resume_skills: Set[str],
    required_skills: Set[str],
    preferred_skills: Set[str],
) -> Dict:
    """
    Compare resume skills against required and preferred JD skills.

    Args:
        resume_skills: Normalized set of candidate skills.
        required_skills: Normalized set of required skills from JD.
        preferred_skills: Normalized set of preferred skills from JD.

    Returns:
        Dictionary with matched, missing, and percentage breakdowns.
    """
    # Convert all skill sets to lowercase before comparison
    resume_skills = {s.strip().lower() for s in resume_skills if s.strip()}
    required_skills = {s.strip().lower() for s in required_skills if s.strip()}
    preferred_skills = {s.strip().lower() for s in preferred_skills if s.strip()}

    # Required skills analysis
    matched_required = resume_skills & required_skills
    missing_required = required_skills - resume_skills

    # Preferred skills analysis
    matched_preferred = resume_skills & preferred_skills
    missing_preferred = preferred_skills - resume_skills

    # All JD skills combined
    all_jd_skills = required_skills | preferred_skills
    all_matched = resume_skills & all_jd_skills

    # Calculate percentages (avoid division by zero)
    required_pct = (
        (len(matched_required) / len(required_skills) * 100)
        if required_skills else 100.0
    )
    overall_pct = (
        (len(all_matched) / len(all_jd_skills) * 100)
        if all_jd_skills else 100.0
    )

    return {
        "matched_required": sorted(matched_required),
        "missing_required": sorted(missing_required),
        "matched_preferred": sorted(matched_preferred),
        "missing_preferred": sorted(missing_preferred),
        "required_match_percentage": round(required_pct, 1),
        "overall_match_percentage": round(overall_pct, 1),
    }


# ── Experience Matching (from V1 matcher.py) ──────────────────────────────────

def match_experience(resume_exp: Optional[int], minimum_exp: int) -> Dict:
    """
    Compare candidate experience with the minimum experience required.

    Args:
        resume_exp: Years of experience extracted from the resume.
        minimum_exp: Minimum years of experience required by the JD.

    Returns:
        A dictionary containing the comparison result and score.
    """
    if resume_exp is None:
        return {
            "matched": False,
            "candidate_experience": None,
            "required_experience": minimum_exp,
            "score": 0.0,
            "message": "Experience could not be extracted from the resume.",
        }

    if minimum_exp == 0:
        # No experience requirement
        return {
            "matched": True,
            "candidate_experience": resume_exp,
            "required_experience": minimum_exp,
            "score": 100.0,
            "message": "No minimum experience requirement.",
        }

    # Score: 100% if meets/exceeds requirement, proportional otherwise
    if resume_exp >= minimum_exp:
        score = 100.0
        message = "Experience requirement satisfied."
    else:
        score = (resume_exp / minimum_exp) * 100
        message = (
            f"Candidate has {resume_exp} years but "
            f"{minimum_exp} years required."
        )

    return {
        "matched": resume_exp >= minimum_exp,
        "candidate_experience": resume_exp,
        "required_experience": minimum_exp,
        "score": round(score, 1),
        "message": message,
    }


# ── Combined Rule-Based Match ─────────────────────────────────────────────────

def rule_based_match(
    resume_skills: List[str],
    jd_required_skills: List[str],
    jd_preferred_skills: List[str],
    resume_experience: Optional[int],
    jd_minimum_experience: int,
) -> Dict:
    """
    Run the full rule-based matching pipeline.

    Returns:
        Dictionary with skills match, experience match, and overall rule score.
    """
    # Convert all skills to lowercase before comparing
    resume_skills = [s.strip().lower() for s in resume_skills if s.strip()]
    jd_required_skills = [s.strip().lower() for s in jd_required_skills if s.strip()]
    jd_preferred_skills = [s.strip().lower() for s in jd_preferred_skills if s.strip()]

    # Normalize all skills
    norm_resume = normalize_skills(resume_skills)
    norm_required = normalize_skills(jd_required_skills)
    norm_preferred = normalize_skills(jd_preferred_skills)

    skills_result = match_skills(norm_resume, norm_required, norm_preferred)
    exp_result = match_experience(resume_experience, jd_minimum_experience)

    # Rule-based score: weighted combination of skill match and experience
    # Skills are weighted more heavily since they're the primary signal
    rule_score = (skills_result["required_match_percentage"] * 0.7) + (exp_result["score"] * 0.3)

    return {
        "skills": skills_result,
        "experience": exp_result,
        "rule_score": round(rule_score, 1),
    }
