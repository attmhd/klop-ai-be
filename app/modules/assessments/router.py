from fastapi import (  # pyright: ignore[reportMissingImports]
    APIRouter,
    HTTPException,
    status,
)

from .schemas import AssessmentRequest, AssessmentResponse
from .services import AssessmentService

router = APIRouter()
service = AssessmentService()


@router.post(
    "/scoring",
    response_model=AssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Score Multiple Questions (Batch)",
)
async def score_questions(payload: AssessmentRequest):
    """
    Menilai daftar pertanyaan secara massal.
    Menerima soal, jawaban user, dan kunci jawaban.
    Mengembalikan status benar/salah per soal dan summary total.
    """
    try:
        return await service.score_assessment(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
