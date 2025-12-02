import logging

from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

# Setup logger
logger = logging.getLogger(__name__)


class BaseLLMClient:
    def __init__(self):
        # Inisialisasi Client Google Gen AI
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = False,
        temperature: float = 0.5,
    ) -> str:
        """
        Memanggil API Gemini dengan dukungan System Instruction & JSON Mode.
        """
        try:
            # 1. Konfigurasi Generasi
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                # Jika json_mode True, paksa output JSON murni
                response_mime_type="application/json" if json_mode else "text/plain",
            )

            # 2. Panggil Model secara Async (.aio)
            response = await self.client.aio.models.generate_content(
                model=self.model, contents=user_prompt, config=config
            )

            # 3. Return text result
            if response.text:
                return response.text
            else:
                raise ValueError("Empty response from LLM")

        except Exception as e:
            logger.error(f"LLM Call Failed: {str(e)}")
            raise e
