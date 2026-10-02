"""
Pydantic model for parsed job description data.

Preserved from V1's jd_parser.py JobDescription class,
moved here for clean separation of models from parsing logic.
"""

from pydantic import BaseModel, Field
from typing import List


class JobDescription(BaseModel):
    """Structured representation of a parsed job description."""

    title: str = Field(default="", description="Job title")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred/nice-to-have skills")
    education: List[str] = Field(default_factory=list, description="Education requirements")
    minimum_experience: int = Field(default=0, description="Minimum years of experience required")
    responsibilities: List[str] = Field(default_factory=list, description="Job responsibilities")
