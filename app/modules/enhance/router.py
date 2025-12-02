from fastapi import APIRouter, HTTPException, status

from app.shared.schemas import BaseResponse

from .schemas import EnhanceData, EnhanceRequest
from .service import EnhanceService

router = APIRouter()
service = EnhanceService()


@router.post(
    "/",
    response_model=BaseResponse[EnhanceData],
    status_code=status.HTTP_200_OK,
    summary="Enhance Question",
)
async def enhance_question_endpoint(payload: EnhanceRequest):
    try:
        # Panggil Service
        result = await service.enhance_question(payload)

        # Bungkus dengan Envelope Pattern
        return BaseResponse(
            code=200,
            success=True,
            message="Question enhanced successfully",
            data=result,
        )
    except Exception as e:
        # Error 500 jika gagal generate/parsing
        raise HTTPException(
            status_code=500, detail=f"Failed to enhance question: {str(e)}"
        )
