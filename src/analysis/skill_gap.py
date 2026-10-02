"""
Skill Gap Analysis — identifies matched, missing, and semantically related skills.

Goes beyond simple set difference by using semantic similarity to find
"related" skills — e.g., if the JD wants "backend development" and the
candidate has "Flask", that's flagged as a related/partial match.
"""

import logging
from typing import Dict, List, Optional

from src.embeddings.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)


def _find_related_skills(
    resume_skills: List[str],
    missing_skills: List[str],
    embedding_model: EmbeddingModel,
    threshold: float = 0.45,
) -> List[Dict]:
    """
    Find resume skills that are semantically related to missing JD skills.

    Args:
        resume_skills: All candidate skills (normalized).
        missing_skills: Skills missing from the candidate's resume.
        embedding_model: EmbeddingModel instance.
        threshold: Minimum cosine similarity to consider "related".

    Returns:
        List of dicts: {"missing_skill": ..., "related_to": ..., "similarity": ...}
    """
    if not embedding_model.available or not resume_skills or not missing_skills:
        return []

    # Convert all skills to lowercase before comparing
    resume_skills = [s.strip().lower() for s in resume_skills if s.strip()]
    missing_skills = [s.strip().lower() for s in missing_skills if s.strip()]

    related = []

    for missing in missing_skills:
        missing_emb = embedding_model.encode([missing])
        if missing_emb is None:
            continue

        best_match = None
        best_score = 0.0

        for skill in resume_skills:
            skill_emb = embedding_model.encode([skill])
            if skill_emb is None:
                continue

            sim = embedding_model.cosine_similarity(skill_emb, missing_emb)
            if sim > best_score:
                best_score = sim
                best_match = skill

        if best_match and best_score >= threshold:
            related.append({
                "missing_skill": missing,
                "related_to": best_match,
                "similarity": round(best_score * 100, 1),
            })

    return related


def analyze_skill_gaps(
    match_result: Dict,
    resume_skills: List[str],
    embedding_model: Optional[EmbeddingModel] = None,
) -> Dict:
    """
    Produce a comprehensive skill gap analysis.

    Args:
        match_result: Output from hybrid_match containing skills matching data.
        resume_skills: Original resume skills list.
        embedding_model: EmbeddingModel for finding related skills (optional).

    Returns:
        Dictionary with matched, missing required, missing preferred,
        and related/partially matched skills.
    """
    skills_data = match_result["rule_result"]["skills"]

    result = {
        "matched_required": skills_data["matched_required"],
        "matched_preferred": skills_data["matched_preferred"],
        "missing_required": skills_data["missing_required"],
        "missing_preferred": skills_data["missing_preferred"],
        "related_skills": [],
        "summary": {},
    }

    # Find semantically related skills for missing ones
    if embedding_model and embedding_model.available:
        all_missing = skills_data["missing_required"] + skills_data["missing_preferred"]
        related = _find_related_skills(
            resume_skills=resume_skills,
            missing_skills=all_missing,
            embedding_model=embedding_model,
        )
        result["related_skills"] = related

    # Summary stats
    total_required = len(skills_data["matched_required"]) + len(skills_data["missing_required"])
    total_preferred = len(skills_data["matched_preferred"]) + len(skills_data["missing_preferred"])

    result["summary"] = {
        "required_matched": len(skills_data["matched_required"]),
        "required_total": total_required,
        "preferred_matched": len(skills_data["matched_preferred"]),
        "preferred_total": total_preferred,
        "related_found": len(result["related_skills"]),
    }

    return result
