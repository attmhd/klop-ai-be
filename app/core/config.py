import os

from pydantic_settings import BaseSettings  # pyright: ignore[reportMissingImports]


class Settings(BaseSettings):
    KOLOSAL_API_KEY: str = os.getenv("KOLOSAL_API_KEY", "")
    KOLOSAL_BASE_URL: str = os.getenv("KOLOSAL_BASE_URL", "")
    KOLOSAL_MODEL: str = os.getenv("KOLOSAL_MODEL", "Qwen 3 30BA3B")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "")

    API_SECRET_TOKEN: str = os.getenv("API_SECRET_TOKEN", "")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
