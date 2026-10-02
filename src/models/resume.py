"""
Pydantic model for parsed resume data.

Enhanced from V1 to include experience (years) and responsibilities,
which are needed for the hybrid matching engine.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Resume(BaseModel):
    """Structured representation of a parsed resume."""

    name: str = Field(default="", description="Candidate full name")
    education: List[str] = Field(default_factory=list, description="Education qualifications")
    skills: List[str] = Field(default_factory=list, description="Technical and soft skills")
    experience: Optional[int] = Field(default=None, description="Total years of experience")
    projects: List[str] = Field(default_factory=list, description="Project descriptions")
    achievements: List[str] = Field(default_factory=list, description="Achievements and certifications")
    responsibilities: List[str] = Field(
        default_factory=list,
        description="Key responsibilities from work experience"
    )
