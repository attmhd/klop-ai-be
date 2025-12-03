from typing import List

from pydantic import BaseModel, Field


# --- INPUT ---
class QuestionItem(BaseModel):
    question: str = Field(..., description="Teks pertanyaan asli")
    answer: str = Field(..., description="Jawaban yang diinput oleh kandidat")
    expectedAnswer: str = Field(
        ..., description="Kunci jawaban (Opsi atau Rubrik Keywords)"
    )


class AssessmentRequest(BaseModel):
    title: str = Field(..., description="Role/Posisi")
    description: str = Field(..., description="Konteks/Level")
    questions: List[QuestionItem] = Field(
        ..., description="List soal yang akan dinilai"
    )


# --- OUTPUT ---
class ScoredQuestionItem(BaseModel):
    question: str
    answer: str
    isAnswerCorrect: bool = Field(
        ..., description="True jika jawaban kandidat sesuai kunci"
    )


class AssessmentResponse(BaseModel):
    summary: str = Field(
        ..., description="Ringkasan performa kandidat secara keseluruhan"
    )
    questions: List[ScoredQuestionItem]
