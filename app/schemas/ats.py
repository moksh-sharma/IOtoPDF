"""ATS score schemas - Shakkar Daddy."""

__author__ = "Shakkar Daddy"

from pydantic import BaseModel, Field


class CategoryScore(BaseModel):
    """Score breakdown for a single ATS category."""

    name: str
    score: int
    max_score: int
    feedback: list[str] = Field(default_factory=list)


class ATSScoreReport(BaseModel):
    """Full ATS analysis report for a resume."""

    score: int = Field(ge=0, le=100)
    grade: str
    summary: str
    categories: list[CategoryScore]
    tips: list[str] = Field(default_factory=list)
    word_count: int = 0
    ocr_quality: str = "good"
