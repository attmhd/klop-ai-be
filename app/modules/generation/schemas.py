from typing import List, Optional

from pydantic import BaseModel, Field


# --- Input Request ---
class GenerateRequest(BaseModel):
    role: str = Field(..., example="Senior Backend Engineer")
    location: str = Field(..., example="Jakarta, Indonesia")
    level: str = Field(..., example="Senior")
    criteria: str = Field(..., example="System Design & Scalability")
    question_count: int = Field(1, example=1)


# --- Output Response Components ---
class RubricItem(BaseModel):
    positive: List[str] = Field(..., description="Indikator jawaban benar")
    negative: List[str] = Field(..., description="Red flag jawaban salah")


class QuestionItem(BaseModel):
    id: int
    text: str = Field(
        ..., description="Gabungan Skenario dan Pertanyaan dalam format Markdown"
    )
    rubric: RubricItem


class GenerateData(BaseModel):
    meta: dict = Field(default_factory=dict)
    questions: List[QuestionItem]
