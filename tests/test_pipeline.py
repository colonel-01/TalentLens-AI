"""
End-to-end test for the TalentLens-AI V2 pipeline.

This test runs the same resume (data/res.pdf) against a sample JD
through the full V2 hybrid matching pipeline.

Usage:
    uv run python -m tests.test_pipeline
"""

import json
import logging
import sys
import os

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline import run_pipeline, format_report


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    resume_path = "data/res.pdf"

    jd_text = """
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

    print("\n" + "=" * 60)
    print("  TalentLens-AI V2 — End-to-End Pipeline Test")
    print("=" * 60 + "\n")

    # Run the pipeline
    report = run_pipeline(resume_path, jd_text)

    # Print the formatted report
    print(format_report(report))

    # Verify key sections exist
    print("\n\n" + "=" * 60)
    print("  VALIDATION CHECKS")
    print("=" * 60)

    checks = [
        ("Report has candidate info", "candidate" in report),
        ("Report has job info", "job" in report),
        ("Report has match result", "match_result" in report),
        ("Report has final score", "final_score" in report.get("match_result", {})),
        ("Report has skill gap analysis", "skill_gap" in report),
        ("Report has job fit analysis", "job_fit" in report),
        ("Report has recommendations", "recommendations" in report),
        ("Score is between 0-100", 0 <= report["match_result"]["final_score"] <= 100),
        ("Scoring breakdown present", "scoring_breakdown" in report["match_result"]),
        ("Semantic availability flagged", "semantic_matching_available" in report["match_result"]),
    ]

    all_passed = True
    for name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("  ✅ All validation checks passed!")
    else:
        print("  ❌ Some checks failed. Review the output above.")

    print()

    # Save the full JSON report
    os.makedirs("data", exist_ok=True)
    with open("data/report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=list)
    print(f"  📄 Full JSON report saved to data/report.json")


if __name__ == "__main__":
    main()
