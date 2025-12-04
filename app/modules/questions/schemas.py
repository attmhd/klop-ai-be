from typing import List, Optional

from pydantic import BaseModel, Field


class CreateQuestionRequest(BaseModel):
    title: str = Field(..., description="Role")
    description: str = Field(..., description="Context")


class QuestionRequest(BaseModel):
    title: str
    description: str
    question: str


class ComprehensiveRequest(BaseModel):
    title: str = Field(..., description="Role")
    description: str = Field(..., description="Context")
    isAnswerOptions: bool = Field(..., description="True = Pilihan Ganda")


class SimpleQuestionResponse(BaseModel):
    question: str


class ComprehensiveResponse(BaseModel):
    question: str
    isAnswerOptions: Optional[bool] = None
    answerOptions: Optional[List[str]] = None

    expectedAnswer: str
