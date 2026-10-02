"""
Job Description Parser — converts JD text to structured JobDescription data.

Preserved from V1's jd_parser.py with minimal changes:
- Uses centralized config (model name, API key)
- Model definition moved to src/models/job_description.py
- Added error handling for malformed LLM JSON
"""

import json
import logging

from groq import Groq

from src.config import GROQ_API_KEY, LLM_MODEL
from src.models.job_description import JobDescription

logger = logging.getLogger(__name__)


def parse_job_description(jd_text: str) -> JobDescription:
    """
    Parse a job description text into a structured JobDescription object.

    Args:
        jd_text: The raw job description text.

    Returns:
        A validated JobDescription object.

    Raises:
        ValueError: If the LLM returns invalid JSON.
    """
    client = Groq(api_key=GROQ_API_KEY)
    schema = JobDescription.model_json_schema()

    messages = [
        {
            "role": "system",
            "content": f"""You are an expert job description parser.

Extract the information strictly according to this schema:

{json.dumps(schema, indent=2)}

Rules:
- Return ONLY valid JSON.
- Do not add explanations or markdown.
- If a field is missing:
    - use [] for lists
    - use 0 for minimum_experience
    - use "" for title
- Do not hallucinate.
"""
        },
        {
            "role": "user",
            "content": jd_text
        }
    ]

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
        )

        raw_json = response.choices[0].message.content
        data = json.loads(raw_json)
        job = JobDescription(**data)
        logger.info("JD parsed successfully: %s", job.title)
        return job

    except json.JSONDecodeError as e:
        logger.error("LLM returned invalid JSON for JD: %s", e)
        raise ValueError(f"Failed to parse LLM response as JSON: {e}") from e
    except Exception as e:
        logger.error("JD parsing failed: %s", e)
        raise


if __name__ == "__main__":
    sample_jd = """
    Machine Learning Engineer

    We are looking for an ML Engineer.

    Required Skills:
    Python, SQL, TensorFlow, Docker

    Preferred Skills:
    AWS, FastAPI

    Minimum Experience:
    2 years

    Education:
    Bachelor's Degree in Computer Science

    Responsibilities:
    - Build ML models
    - Deploy APIs
    - Work with data scientists
    """

    result = parse_job_description(sample_jd)
    print(result.model_dump_json(indent=2))
