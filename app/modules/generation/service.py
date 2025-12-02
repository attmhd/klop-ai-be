import logging

from app.shared.llm_client import BaseLLMClient
from app.shared.toon_parser import parse_toon_string

# Pastikan GENERATION_SYSTEM_PROMPT di file .prompts sudah diupdate
# dengan versi terbaru yang menerima parameter 'Question Count'
from .prompts import GENERATION_SYSTEM_PROMPT
from .schemas import GenerateData, GenerateRequest

logger = logging.getLogger(__name__)


class GenerationService:
    def __init__(self):
        # Inisialisasi Client Gemini
        self.llm = BaseLLMClient()

    async def generate_quiz(self, payload: GenerateRequest) -> GenerateData:
        try:
            # 1. Prepare User Prompt (UPDATE DI SINI)
            # Menambahkan parameter question_count ke dalam string prompt
            user_content = (
                f"Role: {payload.role}\n"
                f"Location: {payload.location}\n"
                f"Level: {payload.level}\n"
                f"Criteria: {payload.criteria}\n"
                f"Question Count: {payload.question_count}"
            )

            # 2. Call LLM (Gemini)
            # json_mode=False karena kita minta format YAML/TOON
            logger.info(
                f"Generating {payload.question_count} assessment(s) for: {payload.role}"
            )

            raw_toon_response = await self.llm.call_llm(
                system_prompt=GENERATION_SYSTEM_PROMPT,
                user_prompt=user_content,
                json_mode=False,
                temperature=0.4,
            )

            # 3. Parse TOON/YAML String -> Python Dict
            # Pastikan parser Anda bisa menangani list of questions di dalam YAML
            parsed_dict = parse_toon_string(raw_toon_response)

            # 4. Validasi ke Schema Pydantic
            return GenerateData(**parsed_dict)

        except Exception as e:
            logger.error(f"Generation Service Error: {str(e)}")
            raise e
