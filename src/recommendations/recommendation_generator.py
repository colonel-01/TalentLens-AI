"""
Recommendation Generator — LLM-powered explainable insights.

The LLM is called ONLY AFTER all deterministic/semantic analysis is complete.
It receives the structured matching results and generates human-readable
recommendations. It does NOT calculate scores independently.

Design Decision:
    The LLM acts as a "narrator" — it explains results that were already
    computed deterministically. This keeps scoring transparent and reproducible
    while adding the interpretability that LLMs are good at.
"""

import json
import logging

from groq import Groq

from src.config import GROQ_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)


def generate_recommendations(
    job_fit: dict,
    skill_gap: dict,
    match_result: dict,
    candidate_name: str = "The candidate",
    job_title: str = "the position",
) -> dict:
    """
    Use the LLM to generate explainable recommendations based on
    pre-computed matching results.

    The LLM does NOT:
        - Calculate its own score
        - Override deterministic results
        - Hallucinate skills not found in the data

    The LLM DOES:
        - Explain why the candidate matches or doesn't match
        - Highlight important skill gaps
        - Suggest resume improvements
        - Recommend skills/projects to develop

    Args:
        job_fit: Output from analyze_job_fit.
        skill_gap: Output from analyze_skill_gaps.
        match_result: Output from hybrid_match.
        candidate_name: Name of the candidate.
        job_title: Title of the job.

    Returns:
        Dictionary with recommendation sections.
    """
    # Build a context summary for the LLM
    context = {
        "candidate_name": candidate_name,
        "job_title": job_title,
        "overall_score": job_fit["overall_score"],
        "fit_level": job_fit["fit_level"],
        "matched_required_skills": skill_gap["matched_required"],
        "missing_required_skills": skill_gap["missing_required"],
        "matched_preferred_skills": skill_gap["matched_preferred"],
        "missing_preferred_skills": skill_gap["missing_preferred"],
        "related_skills": skill_gap["related_skills"],
        "experience_matched": job_fit["experience_match"]["matched"],
        "candidate_experience": job_fit["experience_match"]["candidate_years"],
        "required_experience": job_fit["experience_match"]["required_years"],
        "relevant_projects": job_fit["relevant_projects"],
        "major_gaps": job_fit["major_gaps"],
        "semantic_available": job_fit["semantic_relevance"]["available"],
        "semantic_score": job_fit["semantic_relevance"]["overall_score"],
    }

    system_prompt = """You are an expert career advisor and recruitment analyst.

You are given structured analysis results from a resume-JD matching system.
Based ONLY on the provided data, generate insightful recommendations.

IMPORTANT RULES:
- Do NOT invent or calculate any scores. The scores are already provided.
- Do NOT mention skills that are not in the provided data.
- Base all analysis strictly on the evidence provided.
- Be constructive and actionable in recommendations.
- Keep each section concise (3-5 bullet points max).

Return your response as a JSON object with these exact keys:
{
    "match_reasons": ["reason1", "reason2", ...],
    "gap_reasons": ["gap1", "gap2", ...],
    "key_skill_gaps": ["skill_gap_insight1", ...],
    "resume_improvements": ["suggestion1", "suggestion2", ...],
    "skills_to_develop": ["skill1", "skill2", ...]
}
"""

    user_prompt = f"""Analyze this candidate evaluation for the position of {job_title}:

{json.dumps(context, indent=2)}

Generate recommendations based strictly on this data."""

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Slightly creative but grounded
        )

        raw = response.choices[0].message.content
        recommendations = json.loads(raw)

        # Validate expected keys
        expected_keys = [
            "match_reasons", "gap_reasons", "key_skill_gaps",
            "resume_improvements", "skills_to_develop",
        ]
        for key in expected_keys:
            if key not in recommendations:
                recommendations[key] = []

        logger.info("Recommendations generated successfully.")
        return recommendations

    except json.JSONDecodeError as e:
        logger.error("LLM returned invalid JSON for recommendations: %s", e)
        return _fallback_recommendations(job_fit, skill_gap)
    except Exception as e:
        logger.error("Recommendation generation failed: %s", e)
        return _fallback_recommendations(job_fit, skill_gap)


def _fallback_recommendations(job_fit: dict, skill_gap: dict) -> dict:
    """
    Generate basic recommendations without LLM when the API call fails.
    These are mechanical but still useful.
    """
    recommendations = {
        "match_reasons": [],
        "gap_reasons": [],
        "key_skill_gaps": [],
        "resume_improvements": [],
        "skills_to_develop": [],
        "_fallback": True,
        "_fallback_reason": "LLM recommendation generation failed. Basic recommendations provided.",
    }

    # Match reasons
    matched = skill_gap.get("matched_required", [])
    if matched:
        recommendations["match_reasons"].append(
            f"Candidate has {len(matched)} required skill(s): {', '.join(matched)}"
        )
    if job_fit["experience_match"]["matched"]:
        recommendations["match_reasons"].append("Candidate meets the experience requirement.")

    # Gap reasons
    for gap in job_fit.get("major_gaps", []):
        recommendations["gap_reasons"].append(gap)

    # Skills to develop
    missing = skill_gap.get("missing_required", [])
    recommendations["skills_to_develop"] = missing[:5]

    # Resume improvements
    if not job_fit["experience_match"]["matched"]:
        recommendations["resume_improvements"].append(
            "Highlight all relevant work experience with clear dates."
        )
    if missing:
        recommendations["resume_improvements"].append(
            f"Consider learning: {', '.join(missing[:3])}"
        )

    return recommendations
