"""
TalentLens-AI V2 Pipeline — orchestrates the full hybrid matching workflow.

Flow:
    1. Parse Resume (PDF → structured JSON)
    2. Parse JD (text → structured JSON)
    3. Load Embedding Model (with fallback)
    4. Hybrid Matching (rule + semantic + experience)
    5. Skill Gap Analysis
    6. Job Fit Analysis
    7. LLM Recommendations
    8. Final Report Generation
"""

import json
import logging
import sys

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.config import validate_config
from src.embeddings.embedding_model import EmbeddingModel
from src.parser.resume_parser import parse_resume
from src.parser.jd_parser import parse_job_description
from src.matching.hybrid_matcher import hybrid_match
from src.analysis.skill_gap import analyze_skill_gaps
from src.analysis.job_fit import analyze_job_fit
from src.recommendations.recommendation_generator import generate_recommendations

logger = logging.getLogger(__name__)


def run_pipeline(resume_pdf_path: str, jd_text: str) -> dict:
    """
    Run the full TalentLens-AI V2 pipeline.

    Args:
        resume_pdf_path: Path to the resume PDF file.
        jd_text: Raw job description text.

    Returns:
        Complete analysis report as a dictionary.
    """
    # ── Validate configuration ────────────────────────────────────────────
    validate_config()

    # ── Step 1: Parse Resume ──────────────────────────────────────────────
    logger.info("Step 1/7: Parsing resume from %s", resume_pdf_path)
    resume = parse_resume(resume_pdf_path)
    logger.info("Resume parsed: %s (%d skills, %s yrs exp)",
                resume.name, len(resume.skills), resume.experience)

    # ── Step 2: Parse Job Description ─────────────────────────────────────
    logger.info("Step 2/7: Parsing job description")
    jd = parse_job_description(jd_text)
    logger.info("JD parsed: %s (%d required, %d preferred skills)",
                jd.title, len(jd.required_skills), len(jd.preferred_skills))

    # ── Step 3: Load Embedding Model ──────────────────────────────────────
    logger.info("Step 3/7: Loading embedding model")
    embedding_model = EmbeddingModel()

    # ── Step 4: Hybrid Matching ───────────────────────────────────────────
    logger.info("Step 4/7: Running hybrid matching")
    match_result = hybrid_match(resume, jd, embedding_model)

    # ── Step 5: Skill Gap Analysis ────────────────────────────────────────
    logger.info("Step 5/7: Analyzing skill gaps")
    skill_gap = analyze_skill_gaps(match_result, resume.skills, embedding_model)

    # ── Step 6: Job Fit Analysis ──────────────────────────────────────────
    logger.info("Step 6/7: Analyzing job fit")
    job_fit = analyze_job_fit(match_result, skill_gap, resume.projects, jd.responsibilities)

    # ── Step 7: LLM Recommendations ───────────────────────────────────────
    logger.info("Step 7/7: Generating recommendations")
    recommendations = generate_recommendations(
        job_fit=job_fit,
        skill_gap=skill_gap,
        match_result=match_result,
        candidate_name=resume.name or "The candidate",
        job_title=jd.title or "the position",
    )

    # ── Assemble Final Report ─────────────────────────────────────────────
    report = {
        "candidate": {
            "name": resume.name,
            "skills": resume.skills,
            "experience_years": resume.experience,
            "education": resume.education,
            "projects": resume.projects,
        },
        "job": {
            "title": jd.title,
            "required_skills": jd.required_skills,
            "preferred_skills": jd.preferred_skills,
            "minimum_experience": jd.minimum_experience,
        },
        "match_result": {
            "final_score": match_result["final_score"],
            "scoring_breakdown": match_result["scoring_breakdown"],
            "semantic_matching_available": match_result["semantic_matching_available"],
        },
        "skill_gap": skill_gap,
        "job_fit": job_fit,
        "recommendations": recommendations,
    }

    return report


def format_report(report: dict) -> str:
    """
    Format the analysis report as a human-readable text report.

    Args:
        report: Output from run_pipeline.

    Returns:
        Formatted report string.
    """
    lines = []
    hr = "═" * 60

    lines.append(hr)
    lines.append("         TALENTLENS-AI V2 — CANDIDATE REPORT")
    lines.append(hr)
    lines.append("")

    # ── Candidate Info ────────────────────────────────────────────────────
    candidate = report["candidate"]
    job = report["job"]
    lines.append(f"  Candidate:  {candidate['name']}")
    lines.append(f"  Position:   {job['title']}")
    lines.append(f"  Experience: {candidate['experience_years'] or 'N/A'} years")
    lines.append("")

    # ── Overall Score ─────────────────────────────────────────────────────
    match = report["match_result"]
    job_fit = report["job_fit"]
    lines.append(f"  ┌──────────────────────────────────────────────┐")
    lines.append(f"  │  OVERALL MATCH: {match['final_score']:.1f}%  —  {job_fit['fit_level']:<20}│")
    lines.append(f"  └──────────────────────────────────────────────┘")
    lines.append("")

    # ── Score Breakdown ───────────────────────────────────────────────────
    breakdown = match["scoring_breakdown"]
    lines.append("  SCORE BREAKDOWN")
    lines.append("  " + "─" * 44)
    lines.append(f"  Rule-Based Score:  {breakdown['rule_score']:.1f}%  (weight: {breakdown['rule_weight']:.0%})")

    if match["semantic_matching_available"]:
        lines.append(f"  Semantic Score:    {breakdown['semantic_score']:.1f}%  (weight: {breakdown['semantic_weight']:.0%})")
    else:
        lines.append(f"  Semantic Score:    ⚠ UNAVAILABLE")
        if "fallback_note" in breakdown:
            lines.append(f"                     {breakdown['fallback_note']}")

    lines.append(f"  Experience Score:  {breakdown['experience_score']:.1f}%  (weight: {breakdown['experience_weight']:.0%})")
    lines.append("")

    # ── Matched Skills ────────────────────────────────────────────────────
    skill_gap = report["skill_gap"]
    lines.append("  MATCHED SKILLS")
    lines.append("  " + "─" * 44)
    for skill in skill_gap["matched_required"]:
        lines.append(f"  ✓ {skill}  (required)")
    for skill in skill_gap["matched_preferred"]:
        lines.append(f"  ✓ {skill}  (preferred)")
    if not skill_gap["matched_required"] and not skill_gap["matched_preferred"]:
        lines.append("  (none)")
    lines.append("")

    # ── Missing Skills ────────────────────────────────────────────────────
    lines.append("  MISSING SKILLS")
    lines.append("  " + "─" * 44)
    for skill in skill_gap["missing_required"]:
        lines.append(f"  ✗ {skill}  (required)")
    for skill in skill_gap["missing_preferred"]:
        lines.append(f"  ✗ {skill}  (preferred)")
    if not skill_gap["missing_required"] and not skill_gap["missing_preferred"]:
        lines.append("  (none — all skills matched!)")
    lines.append("")

    # ── Related Skills ────────────────────────────────────────────────────
    if skill_gap["related_skills"]:
        lines.append("  RELATED / PARTIALLY MATCHED SKILLS")
        lines.append("  " + "─" * 44)
        for rel in skill_gap["related_skills"]:
            lines.append(
                f"  ≈ {rel['related_to']} → {rel['missing_skill']}  "
                f"({rel['similarity']}% similar)"
            )
        lines.append("")

    # ── Experience ────────────────────────────────────────────────────────
    exp = job_fit["experience_match"]
    lines.append("  EXPERIENCE")
    lines.append("  " + "─" * 44)
    lines.append(f"  Candidate: {exp['candidate_years'] or 'N/A'} years")
    lines.append(f"  Required:  {exp['required_years']} years")
    lines.append(f"  Status:    {'✓ Met' if exp['matched'] else '✗ Not met'}")
    lines.append("")

    # ── Major Gaps ────────────────────────────────────────────────────────
    if job_fit["major_gaps"]:
        lines.append("  KEY GAPS")
        lines.append("  " + "─" * 44)
        for gap in job_fit["major_gaps"]:
            lines.append(f"  • {gap}")
        lines.append("")

    # ── Recommendations ───────────────────────────────────────────────────
    recs = report["recommendations"]
    lines.append("  RECOMMENDATIONS")
    lines.append("  " + "─" * 44)

    if recs.get("match_reasons"):
        lines.append("  Why this candidate matches:")
        for reason in recs["match_reasons"]:
            lines.append(f"    + {reason}")
        lines.append("")

    if recs.get("gap_reasons"):
        lines.append("  Why this candidate may fall short:")
        for reason in recs["gap_reasons"]:
            lines.append(f"    - {reason}")
        lines.append("")

    if recs.get("resume_improvements"):
        lines.append("  Resume improvement suggestions:")
        for i, suggestion in enumerate(recs["resume_improvements"], 1):
            lines.append(f"    {i}. {suggestion}")
        lines.append("")

    if recs.get("skills_to_develop"):
        lines.append("  Skills/projects to develop:")
        for i, skill in enumerate(recs["skills_to_develop"], 1):
            lines.append(f"    {i}. {skill}")
        lines.append("")

    if recs.get("_fallback"):
        lines.append(f"  ⚠ {recs['_fallback_reason']}")
        lines.append("")

    lines.append(hr)
    lines.append("  Report generated by TalentLens-AI V2")
    lines.append(hr)

    return "\n".join(lines)


# ── CLI Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Default paths for testing
    resume_path = "data/res.pdf"

    # Sample JD for testing
    sample_jd = """
    Machine Learning Engineer

    We are looking for an experienced ML Engineer to join our team.

    Required Skills:
    - Python
    - SQL
    - TensorFlow or PyTorch
    - Docker
    - Git

    Preferred Skills:
    - AWS or GCP
    - FastAPI
    - Kubernetes
    - MLflow

    Minimum Experience:
    2 years

    Education:
    Bachelor's Degree in Computer Science or related field

    Responsibilities:
    - Build and deploy machine learning models
    - Design and implement REST APIs for model serving
    - Work with data scientists to productionize models
    - Set up CI/CD pipelines for ML workflows
    - Monitor model performance in production
    """

    # Allow custom resume path from command line
    if len(sys.argv) > 1:
        resume_path = sys.argv[1]

    print("\n🚀 TalentLens-AI V2 Pipeline Starting...\n")

    report = run_pipeline(resume_path, sample_jd)

    # Print formatted report
    print(format_report(report))

    # Also save raw JSON
    with open("data/report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=list)
        print(f"\n📄 Raw JSON report saved to data/report.json")
