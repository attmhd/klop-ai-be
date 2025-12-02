from pydantic import BaseModel, Field


# --- Request ---
class EnhanceRequest(BaseModel):
    role: str = Field(..., example="Senior Backend Engineer")
    location: str = Field(..., example="Jakarta, Indonesia")
    level: str = Field(..., example="Senior")
    criteria: str = Field(..., example="System Design & Scalability")
    question_to_enhance: str = Field(
        ...,
        example="Gimana cara scaling database?",
        description="Pertanyaan kasar yang ingin diperbaiki",
    )


# --- Response ---
class EnhanceData(BaseModel):
    original_text: str = Field(..., description="Teks input awal")
    enhanced_text: str = Field(..., description="Hasil perbaikan dari AI")
    improvement_notes: str = Field(..., description="Catatan perbaikan")
