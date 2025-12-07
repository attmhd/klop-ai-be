import logging
from typing import Any, Optional

from openai import AsyncOpenAI  # pyright: ignore[reportMissingImports]
from tenacity import (  # pyright: ignore[reportMissingImports]
    retry,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

try:
    _HAS_GEMINI = True
except ImportError:
    _HAS_GEMINI = False

logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Custom exception ketika semua provider LLM gagal."""

    pass


class BaseLLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.KOLOSAL_API_KEY,
            base_url=settings.KOLOSAL_BASE_URL,
        )
        self.model = settings.KOLOSAL_MODEL

        self.gemini_client: Optional[Any] = None
        self.gemini_model: Optional[str] = getattr(settings, "GEMINI_MODEL", None)
        self._init_gemini_client()

    def _init_gemini_client(self):
        """Inisialisasi Gemini Client secara terisolasi."""
        gemini_api_key = getattr(settings, "GEMINI_API_KEY", None)

        if not _HAS_GEMINI:
            logger.debug("Google GenAI SDK not installed. Fallback disabled.")
            return

        if not gemini_api_key or not self.gemini_model:
            logger.debug(
                "GEMINI_API_KEY atau GEMINI_MODEL tidak diset. Fallback dinonaktifkan."
            )
            return

        try:
            from google import (
                genai as _genai,  # pyright: ignore[reportMissingImports, reportAttributeAccessIssue]
            )

            self.gemini_client = _genai.Client(api_key=gemini_api_key)
            logger.info("Gemini client initialized successfully for fallback.")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini client: {e}")
            self.gemini_client = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _call_kolosal(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool,
        temperature: float,
    ) -> str:
        """Memanggil Primary LLM (Kolosal)."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)

        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Empty response received from Kolosal LLM")

        return response.choices[0].message.content

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _call_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool,
        temperature: float,
    ) -> str:
        """Memanggil Fallback LLM (Gemini)."""
        if not self.gemini_client or not self.gemini_model or not _HAS_GEMINI:
            raise RuntimeError("Gemini fallback is not available config-wise.")

        try:
            from google.genai import (  # pyright: ignore[reportMissingImports]
                types as _types,
            )
        except Exception as e:
            raise RuntimeError(f"Gemini types unavailable: {e}")

        config = _types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            response_mime_type="application/json" if json_mode else "text/plain",
        )

        response = await self.gemini_client.aio.models.generate_content(
            model=self.gemini_model, contents=user_prompt, config=config
        )

        if not response.text:
            raise ValueError("Empty response received from Gemini LLM")

        return response.text

    async def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = False,
        temperature: float = 0.5,
    ) -> str:
        """
        Orkestrator utama: Coba Kolosal -> Gagal -> Coba Gemini.
        """
        try:
            return await self._call_kolosal(
                system_prompt, user_prompt, json_mode, temperature
            )
        except Exception as kolosal_err:
            logger.warning(
                f"Primary LLM (Kolosal) failed: {kolosal_err}. Attempting fallback..."
            )

            if not self.gemini_client:
                logger.error("Fallback (Gemini) not available. Raising original error.")
                raise kolosal_err

            try:
                return await self._call_gemini(
                    system_prompt, user_prompt, json_mode, temperature
                )
            except Exception as gemini_err:
                error_msg = (
                    f"All LLM providers failed. "
                    f"Kolosal error: {kolosal_err}. "
                    f"Gemini error: {gemini_err}"
                )
                logger.critical(error_msg)
                raise LLMProviderError(error_msg) from gemini_err
