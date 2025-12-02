from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

# 1. Definisi Variabel Generik 'T'
# T ini nanti akan digantikan oleh Schema spesifik (misal: GenerateData)
T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """
    Standard Response Envelope untuk semua endpoint API.
    Format:
    {
      "code": 200,
      "success": true,
      "message": "...",
      "data": { ... }
    }
    """

    code: int = Field(
        default=200, description="HTTP Status Code (misal: 200, 201, 400, 500)"
    )
    success: bool = Field(
        default=True, description="Flag status sukses/gagal untuk logic frontend"
    )
    message: str = Field(
        default="Success", description="Pesan yang bisa dibaca user (human-readable)"
    )
    data: Optional[T] = Field(
        default=None,
        description="Payload data dinamis. Bisa berupa Object, List, atau Null.",
    )

    # Konfigurasi untuk Dokumentasi Swagger/OpenAPI
    class Config:
        # Pydantic V2 uses 'json_schema_extra', V1 uses 'schema_extra'
        json_schema_extra = {
            "example": {
                "code": 200,
                "success": True,
                "message": "Operation successful",
                "data": {"sample_key": "sample_value"},
            }
        }
