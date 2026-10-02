"""
Resume Parser — extracts text from PDF and converts to structured Resume data.

Refactored from V1's res_parser.py:
- Wrapped in a function (was running at import-time)
- Added 'experience' and 'responsibilities' to the extraction schema
- Uses centralized config for model name and API key
- Added error handling for malformed LLM JSON
"""

import json
import logging

import pymupdf
from groq import Groq

from src.config import GROQ_API_KEY, LLM_MODEL
from src.models.resume import Resume

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a resume PDF using PyMuPDF.

    If the PDF is image-based (scanned), this will return empty/minimal text.
    OCR fallback can be added in a future version.
    """
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def parse_resume(pdf_path: str) -> Resume:
    """
    Parse a resume PDF into a structured Resume object.

    Steps:
        1. Extract raw text from PDF via PyMuPDF
        2. Send to LLM for structured extraction
        3. Validate and return as Resume Pydantic model

    Args:
        pdf_path: Path to the resume PDF file.

    Returns:
        A validated Resume object.

    Raises:
        ValueError: If the LLM returns invalid JSON or the PDF is empty.
    """
    # Step 1: Extract text
    resume_text = extract_text_from_pdf(pdf_path)

    if not resume_text.strip():
        raise ValueError(
            f"No text could be extracted from '{pdf_path}'. "
            "The PDF may be image-based (scanned). OCR fallback is not yet implemented."
        )

    # Step 2: Send to LLM
    client = Groq(api_key=GROQ_API_KEY)
    schema = Resume.model_json_schema()

    system_prompt = f"""You are an expert resume parser.
Extract information from the resume strictly according to this JSON schema:

{json.dumps(schema, indent=2)}

Rules:
- Return ONLY valid JSON.
- Do not add explanations or markdown.
- If a field is missing, use the default: "" for strings, [] for lists, null for experience.
- For 'experience', extract the total years of professional experience as an integer.
  If unclear, estimate from work history dates. If no work experience, use 0.
- For 'responsibilities', extract key responsibilities from work experience sections.
- Do not hallucinate information not present in the resume.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": resume_text},
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
        resume = Resume(**data)
        logger.info("Resume parsed successfully for: %s", resume.name)
        return resume

    except json.JSONDecodeError as e:
        logger.error("LLM returned invalid JSON for resume: %s", e)
        raise ValueError(f"Failed to parse LLM response as JSON: {e}") from e
    except Exception as e:
        logger.error("Resume parsing failed: %s", e)
        raise


if __name__ == "__main__":
    result = parse_resume("data/res.pdf")
    print(result.model_dump_json(indent=2))
