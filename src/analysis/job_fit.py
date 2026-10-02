"""
Job Fit Analysis — structured assessment of how well a candidate fits the role.

Combines all matching signals (rule-based, semantic, experience) into
a structured evidence-based analysis. The LLM does NOT generate this —
it's deterministically computed from matching data.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def _determine_fit_level(score: float) -> str:
    """Map a score to a human-readable fit level."""
    if score >= 85:
        return "Strong Match"
    elif score >= 70:
        return "Good Match"
    elif score >= 55:
        return "Moderate Match"
    elif score >= 40:
        return "Weak Match"
    else:
        return "Poor Match"


def _identify_relevant_projects(
    resume_projects: List[str],
    jd_responsibilities: List[str],
) -> List[str]:
    """
    Identify resume projects that are relevant to JD responsibilities.

    Simple keyword overlap approach — semantic matching for project
    relevance is handled separately in the semantic matcher.
    """
    if not resume_projects or not jd_responsibilities:
        return []

    # Gather keywords from JD responsibilities
    jd_keywords = set()
    for resp in jd_responsibilities:
        for word in resp.lower().split():
            if len(word) > 3:  # Skip short words
                jd_keywords.add(word.strip(".,;:()"))

    relevant = []
    for project in resume_projects:
        project_words = {w.strip(".,;:()") for w in project.lower().split() if len(w) > 3}
        overlap = project_words & jd_keywords
        if len(overlap) >= 2:  # At least 2 keyword matches
            relevant.append(project)

    return relevant


def _identify_major_gaps(match_result: Dict, skill_gap: Dict) -> List[str]:
    """Identify the most significant gaps between candidate and JD."""
    gaps = []

    # Missing required skills
    missing_req = skill_gap.get("missing_required", [])
    if missing_req:
        gaps.append(
            f"Missing {len(missing_req)} required skill(s): {', '.join(missing_req)}"
        )

    # Experience gap
    exp_data = match_result["rule_result"]["experience"]
    if not exp_data["matched"] and exp_data["candidate_experience"] is not None:
        gaps.append(
            f"Experience gap: has {exp_data['candidate_experience']} years, "
            f"needs {exp_data['required_experience']} years"
        )
    elif exp_data["candidate_experience"] is None:
        gaps.append("Experience could not be determined from resume")

    # Low semantic relevance (if available)
    semantic = match_result.get("semantic_result", {})
    if semantic.get("semantic_matching_available"):
        overall_sem = semantic.get("overall_score", 0)
        if overall_sem is not None and overall_sem < 50:
            gaps.append(
                f"Low semantic relevance ({overall_sem}%) — "
                "resume content may not align well with JD context"
            )

    return gaps


def analyze_job_fit(
    match_result: Dict,
    skill_gap: Dict,
    resume_projects: List[str],
    jd_responsibilities: List[str],
) -> Dict:
    """
    Generate a structured job fit analysis.

    Args:
        match_result: Output from hybrid_match.
        skill_gap: Output from analyze_skill_gaps.
        resume_projects: Candidate's project list.
        jd_responsibilities: JD responsibilities list.

    Returns:
        Dictionary containing:
            - overall_score and fit_level
            - skill_match details
            - semantic_relevance details
            - experience_match details
            - relevant_projects
            - major_gaps
    """
    final_score = match_result["final_score"]
    fit_level = _determine_fit_level(final_score)
    semantic = match_result.get("semantic_result", {})
    exp_data = match_result["rule_result"]["experience"]
    skills_data = match_result["rule_result"]["skills"]

    # Find relevant projects
    relevant_projects = _identify_relevant_projects(resume_projects, jd_responsibilities)

    # Identify major gaps
    major_gaps = _identify_major_gaps(match_result, skill_gap)

    return {
        "overall_score": final_score,
        "fit_level": fit_level,
        "skill_match": {
            "required_match_percentage": skills_data["required_match_percentage"],
            "overall_match_percentage": skills_data["overall_match_percentage"],
            "matched_count": len(skills_data["matched_required"]) + len(skills_data["matched_preferred"]),
            "total_jd_skills": (
                len(skills_data["matched_required"]) + len(skills_data["missing_required"])
                + len(skills_data["matched_preferred"]) + len(skills_data["missing_preferred"])
            ),
        },
        "semantic_relevance": {
            "available": semantic.get("semantic_matching_available", False),
            "overall_score": semantic.get("overall_score"),
            "section_scores": semantic.get("scores", {}),
        },
        "experience_match": {
            "matched": exp_data["matched"],
            "candidate_years": exp_data["candidate_experience"],
            "required_years": exp_data["required_experience"],
            "score": exp_data["score"],
        },
        "relevant_projects": relevant_projects,
        "major_gaps": major_gaps,
    }
