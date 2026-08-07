import os
import json

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from typing import List

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class JobDescription(BaseModel):
    title: str
    required_skills: List[str]
    preferred_skills: List[str]
    education: List[str]
    minimum_experience: int
    responsibilities: List[str]


def parse_job_description(jd_text: str):

    schema = JobDescription.model_json_schema()

    messages = [
        {
            "role": "system",
            "content": f"""
You are an expert job description parser.

Extract the information strictly according to this schema:

{schema}

Rules:
- Return ONLY valid JSON.
- Do not add explanations.
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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0
    )

    raw_json = response.choices[0].message.content

    data = json.loads(raw_json)

    job = JobDescription(**data)

    return job

if __name__ == "__main__":

    jd = """
    Machine Learning Engineer

    We are looking for an ML Engineer.

    Required Skills:
    Python
    SQL
    TensorFlow
    Docker

    Preferred Skills:
    AWS
    FastAPI

    Minimum Experience:
    2 years

    Education:
    Bachelor's Degree in Computer Science

    Responsibilities:
    - Build ML models
    - Deploy APIs
    - Work with data scientists
    """

    result = parse_job_description(jd)

    print(result)