"""
Semantic Matcher — section-level embedding comparison between resume and JD.

Instead of blindly embedding the entire resume and JD as one string,
this compares relevant sections:
    - Resume skills ↔ JD skills
    - Resume experience/responsibilities ↔ JD responsibilities
    - Resume projects ↔ JD requirements/responsibilities

Each section pair gets a cosine similarity score, which are then
averaged into an overall semantic similarity score.
"""

import logging
from typing import Dict, List, Optional

from src.embeddings.embedding_model import EmbeddingModel

logger = logging.getLogger(__name__)


def _prepare_text_block(items: List[str]) -> str:
    """Join a list of strings into a single lowercase text block for embedding."""
    return ". ".join(item.strip().lower() for item in items if item.strip())


def compute_section_similarity(
    embedding_model: EmbeddingModel,
    resume_texts: List[str],
    jd_texts: List[str],
    section_name: str = "section",
) -> Optional[float]:
    """
    Compute cosine similarity between two text sections.

    Args:
        embedding_model: The embedding model instance.
        resume_texts: List of resume text items for this section.
        jd_texts: List of JD text items for this section.
        section_name: Name of the section (for logging).

    Returns:
        Cosine similarity score (0-1), or None if embedding failed.
    """
    resume_block = _prepare_text_block(resume_texts)
    jd_block = _prepare_text_block(jd_texts)

    if not resume_block or not jd_block:
        logger.debug("Skipping %s comparison: empty text block.", section_name)
        return None

    resume_embedding = embedding_model.encode([resume_block])
    jd_embedding = embedding_model.encode([jd_block])

    if resume_embedding is None or jd_embedding is None:
        return None

    score = embedding_model.cosine_similarity(resume_embedding, jd_embedding)
    logger.debug("Semantic similarity for %s: %.3f", section_name, score)
    return score


def semantic_match(
    embedding_model: EmbeddingModel,
    resume_skills: List[str],
    resume_projects: List[str],
    resume_responsibilities: List[str],
    jd_required_skills: List[str],
    jd_preferred_skills: List[str],
    jd_responsibilities: List[str],
) -> Dict:
    """
    Run section-level semantic matching between resume and JD.

    Compares three section pairs:
        1. Skills ↔ Skills (all JD skills combined)
        2. Projects ↔ Responsibilities
        3. Responsibilities ↔ Responsibilities

    Args:
        embedding_model: Loaded EmbeddingModel instance.
        resume_skills: Candidate skill list.
        resume_projects: Candidate project descriptions.
        resume_responsibilities: Candidate work responsibilities.
        jd_required_skills: JD required skills.
        jd_preferred_skills: JD preferred skills.
        jd_responsibilities: JD responsibilities.

    Returns:
        Dictionary with per-section scores, overall score,
        and availability flag.
    """
    if not embedding_model.available:
        return {
            "semantic_matching_available": False,
            "scores": {},
            "overall_score": None,
            "message": "Semantic matching unavailable — embedding model not loaded.",
        }

    # Convert all resume and JD items to lowercase before comparing
    resume_skills = [s.strip().lower() for s in resume_skills if s.strip()]
    resume_projects = [p.strip().lower() for p in resume_projects if p.strip()]
    resume_responsibilities = [r.strip().lower() for r in resume_responsibilities if r.strip()]

    jd_required_skills = [s.strip().lower() for s in jd_required_skills if s.strip()]
    jd_preferred_skills = [s.strip().lower() for s in jd_preferred_skills if s.strip()]
    jd_responsibilities = [r.strip().lower() for r in jd_responsibilities if r.strip()]

    all_jd_skills = jd_required_skills + jd_preferred_skills

    # Section-level comparisons
    section_scores = {}

    # 1. Skills ↔ Skills
    skills_sim = compute_section_similarity(
        embedding_model, resume_skills, all_jd_skills, "skills"
    )
    if skills_sim is not None:
        section_scores["skills"] = round(skills_sim * 100, 1)

    # 2. Projects ↔ Responsibilities
    projects_sim = compute_section_similarity(
        embedding_model, resume_projects, jd_responsibilities, "projects_vs_responsibilities"
    )
    if projects_sim is not None:
        section_scores["projects_vs_responsibilities"] = round(projects_sim * 100, 1)

    # 3. Responsibilities ↔ Responsibilities
    resp_sim = compute_section_similarity(
        embedding_model, resume_responsibilities, jd_responsibilities, "responsibilities"
    )
    if resp_sim is not None:
        section_scores["responsibilities"] = round(resp_sim * 100, 1)

    # Overall semantic score = average of available section scores
    if section_scores:
        overall = sum(section_scores.values()) / len(section_scores)
        return {
            "semantic_matching_available": True,
            "scores": section_scores,
            "overall_score": round(overall, 1),
            "message": f"Semantic matching active ({len(section_scores)} sections compared).",
        }
    else:
        return {
            "semantic_matching_available": False,
            "scores": {},
            "overall_score": None,
            "message": (
                "Semantic matching failed — no valid section comparisons could be made. "
                "This may be due to empty resume/JD sections."
            ),
        }
